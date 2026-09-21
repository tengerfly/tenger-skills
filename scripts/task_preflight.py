"""Read-only transition readiness checks. Never executes Skills or changes state."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path, PureWindowsPath

import validate_core as core

TOOL_ROOT = Path(__file__).resolve().parents[1]


def safe_path(root, value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("path must be a non-empty project-relative string")
    portable = value.replace("\\", "/")
    path = Path(portable)
    if path.is_absolute() or PureWindowsPath(value).drive or ".." in path.parts or ":" in portable:
        raise ValueError(f"path must be project-relative without traversal: {value}")
    target = (root / path).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError(f"path escapes root (including symlink): {value}")
    return target


def within(path, parent):
    return path == parent or path.is_relative_to(parent)


def scope_errors(root, task, decision):
    errors = []
    try:
        scope = task["scope"]
        grant = decision.get("scope", {})
        allowed = [safe_path(root, p) for p in scope.get("allowedPaths", [])]
        granted = [safe_path(root, p) for p in grant.get("allowedPaths", [])]
        forbidden = [safe_path(root, p) for p in scope.get("forbiddenPaths", []) + grant.get("forbiddenPaths", [])]
        output = safe_path(root, task["expectedOutput"]["path"])
        if not allowed or not granted:
            errors.append("task and approval must specify non-empty allowedPaths")
        if any(not any(within(p, g) for g in granted) for p in allowed):
            errors.append("task allowedPaths exceeds approval scope")
        if not any(within(output, p) for p in allowed):
            errors.append("expectedOutput.path is outside task allowedPaths")
        if any(within(output, p) for p in forbidden):
            errors.append("expectedOutput.path is forbidden; deny takes precedence")
    except (ValueError, KeyError, TypeError) as exc:
        errors.append(f"invalid path scope: {exc}")
    return errors


def plan(root, task, registry_root=TOOL_ROOT):
    """Check a proposed completed transition against on-disk inputs and evidence."""
    states = core.load_yaml(registry_root / "governance/state-registry.yaml")
    skills = core.load_yaml(registry_root / "governance/skill-registry.yaml")
    state_map = {s["id"]: s for s in states["states"]}
    skill_map = {s["id"]: s for s in skills["skills"] if s.get("status") != "external"}
    errors = core.validate_task(task, set(state_map), set(skill_map))
    if errors:
        return None, errors
    workflow = core.load_yaml(root / ".spec/workflow.yaml")
    manifest, by_id, base = core.artifact_context(root)
    errors.extend(base)
    decisions, context, base = core.approval_context(root, workflow, by_id)
    errors.extend(base)
    errors.extend(core.check_gate(root))
    if manifest.get("projectId") != workflow.get("projectId"):
        errors.append("manifest/workflow projectId mismatch")
    for field in ("projectId", "executionId", "lifecycle", "revision"):
        if not task.get(field) or task.get(field) != workflow.get(field):
            errors.append(f"task/workflow {field} mismatch or missing")
    if task["currentState"] != workflow.get("state"):
        errors.append("task currentState is stale")
    transition = next((t for t in states["transitions"] if t["id"] == task.get("transitionId")), None)
    if transition is None:
        return None, errors + ["unknown transitionId"]
    if transition["from"] != task["currentState"] or transition["to"] != task.get("targetState"):
        errors.append("transition endpoints do not match task")
    lifecycle, actor = task["lifecycle"], task["requiredSkill"]
    if actor != transition["actor"] or task["authorization"].get("actor") != actor:
        errors.append("transition actor / authorization actor mismatch")
    if lifecycle not in transition["lifecycle"] or lifecycle not in skill_map[actor].get("lifecycle", []):
        errors.append("transition or actor does not support task lifecycle")
    for sid in (transition["from"], transition["to"]):
        if lifecycle not in state_map[sid].get("lifecycle", []):
            errors.append(f"state does not support task lifecycle: {sid}")
    gate = dict(task["gate"])
    if "gate" in gate:
        errors.append("task.gate uses outcome only; ambiguous gate/outcome keys are forbidden")
    for field in ("evidenceRefs", "decisionRefs"):
        gate[field] = task.get(field, [])
    errors.extend(core.gate_check(gate, "task.gate", by_id, decisions, context))
    if gate.get("outcome") != transition["requiredOutcome"] or gate.get("allowDownstream") != transition["allowDownstream"]:
        errors.append("task Gate does not meet registered transition requirements")
    auth_ref = task["authorization"].get("approvalRef")
    if auth_ref not in task.get("decisionRefs", []):
        errors.append("authorization approvalRef must be in decisionRefs")
    actions = ["execute-task"]
    if transition.get("requiresAuthorization"):
        actions.append(transition["requiresAuthorization"])
    if workflow.get("gate") == "BLOCKED" and gate.get("outcome") != "BLOCKED":
        actions.append("clear-block")
        if not task.get("clearanceEvidenceRefs") or not set(task["clearanceEvidenceRefs"]).issubset(task.get("evidenceRefs", [])):
            errors.append("clearing BLOCKED requires clearanceEvidenceRefs included in evidenceRefs")
    for action in actions:
        errors.extend(core.approval_errors(auth_ref, action, decisions, context))
    decision = decisions.get(auth_ref, {})
    if task["authorization"].get("grantedBy") != decision.get("approvedBy"):
        errors.append("authorization.grantedBy differs from signed-off decision")
    try:
        if core.timestamp(task["authorization"].get("grantedAt")) != core.timestamp(decision.get("approvedAt")):
            errors.append("authorization.grantedAt differs from decision")
    except ValueError as exc:
        errors.append(str(exc))
    scope = decision.get("scope", {})
    if scope.get("actor") != actor or transition["id"] not in scope.get("transitionIds", []):
        errors.append("approval must explicitly cover actor and transitionId")
    errors.extend(scope_errors(root, task, decision))
    for field in ("inputRefs", "artifactRefs", "evidenceRefs", "decisionRefs"):
        if not isinstance(task.get(field, []), list):
            errors.append(f"task.{field} must be a list")
            continue
        for ref in task.get(field, []):
            if ref not in by_id:
                errors.append(f"task.{field} unknown reference: {ref}")
            elif field == "decisionRefs" and by_id[ref].get("type") != "decision":
                errors.append(f"task.decisionRefs wrong type: {ref}")
    subjects = set(task.get("inputRefs", [])) | set(task.get("artifactRefs", []))
    artifact_types = set()
    for ref in subjects:
        item = by_id.get(ref, {})
        artifact_types.add(item.get("type"))
        if item.get("status") not in {"REVIEW", "APPROVED"}:
            errors.append(f"task subject is not ready: {ref}")
    missing = set(transition["requiredArtifacts"]) - artifact_types
    if missing:
        errors.append(f"missing transition artifact types: {sorted(missing)}")
    roles = set()
    digests = {}
    for ref in subjects & set(by_id):
        try:
            digests[ref] = hashlib.sha256(safe_path(root, by_id[ref]["path"]).read_bytes()).hexdigest()
        except (OSError, ValueError) as exc:
            errors.append(f"cannot hash subject {ref}: {exc}")
    for ref in task.get("evidenceRefs", []):
        item = by_id.get(ref, {})
        if item.get("type") not in core.EVIDENCE_TYPES:
            errors.append(f"invalid evidence type: {ref}")
            continue
        for field in ("executionId", "revision", "lifecycle"):
            if item.get(field) != task.get(field):
                errors.append(f"evidence {ref} stale/wrong {field}")
        if item.get("result") != "PASS" or item.get("status") not in {"REVIEW", "APPROVED"}:
            errors.append(f"evidence {ref} is not a current PASS result")
        if item.get("role") not in states.get("evidenceRoles", []):
            errors.append(f"evidence {ref} unknown role")
        roles.add(item.get("role"))
        if not subjects.issubset(item.get("subjectRefs", [])):
            errors.append(f"evidence {ref} does not cover all task subjects")
        if any(item.get("subjectDigests", {}).get(s) != digest for s, digest in digests.items()):
            errors.append(f"evidence {ref} subjectDigests mismatch")
        try:
            digest = hashlib.sha256(safe_path(root, item["path"]).read_bytes()).hexdigest()
            if item.get("contentDigest") != digest:
                errors.append(f"evidence {ref} contentDigest mismatch")
        except (OSError, ValueError, KeyError) as exc:
            errors.append(f"cannot hash evidence {ref}: {exc}")
    if not set(transition["requiredEvidence"]).issubset(roles):
        errors.append("missing required transition evidence roles")
    output = task["expectedOutput"]
    types = {a["type"] for a in core.load_yaml(registry_root / "governance/artifact-registry.yaml")["artifacts"]}
    if output.get("artifactType") not in types or not output.get("acceptanceChecks"):
        errors.append("expectedOutput requires registered artifactType and non-empty acceptanceChecks")
    if errors:
        return None, errors
    return {"mode": "read-only-transition-readiness", "taskId": task["taskId"],
            "transitionId": transition["id"], "from": transition["from"], "to": transition["to"],
            "requiredSkill": actor, "executionId": task["executionId"], "revision": task["revision"],
            "failureRoute": transition["failureRoute"], "timeoutHours": transition["timeoutHours"],
            "stateChanged": False, "skillExecuted": False}, []


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--task-file", required=True)
    args = parser.parse_args(argv)
    try:
        root = Path(args.project_root).resolve()
        task = core.load_yaml(safe_path(root, args.task_file))["task"]
        result, errors = plan(root, task)
    except (ValueError, OSError, KeyError, TypeError, AttributeError) as exc:
        result, errors = None, [f"invalid task/project document: {exc}"]
    print(json.dumps({"plan": result, "errors": errors}, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
