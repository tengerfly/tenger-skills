from __future__ import annotations
import argparse, os, re, sys
from datetime import datetime, timezone
from collections import defaultdict, deque
from pathlib import Path, PureWindowsPath
from typing import Any
import yaml

LIFECYCLES = {"CREATE", "CHANGE", "DEFECT", "REFACTOR", "INCIDENT", "OPTIMIZE"}
GATES = {"PASS", "CONDITIONAL", "BLOCKED"}
STATUSES = {"DRAFT", "REVIEW", "APPROVED", "SUPERSEDED"}
EVIDENCE_TYPES = {"validation-report", "test-report", "release-report", "inspection", "signal", "research", "triage", "incident"}
EXTERNAL_REF = re.compile(r"^(?:USER|REQ|EXT|URL|ISSUE|PR|COMMIT|RUN)-[A-Za-z0-9][A-Za-z0-9_.:-]*$")
REQUIRED_SECTIONS = ["Purpose", "Trigger", "Inputs", "Preconditions", "Responsibilities", "Non-goals", "Procedure", "Outputs", "Evidence", "Gate", "Failure Route", "Downstream Contract", "State Changes"]
BLOCKED_STATES = {"WORKFLOW_BLOCKED", "INSPECTION_BLOCKED", "BASELINE_INCOMPLETE", "OBSERVABILITY_GAP", "RELEASE_PAUSED", "DEPLOYMENT_ROLLED_BACK"}

class DuplicateKeyError(ValueError): pass
class StrictLoader(yaml.SafeLoader): pass

def _mapping(loader, node, deep=False):
    result = {}
    for k_node, v_node in node.value:
        key = loader.construct_object(k_node, deep=deep)
        if key in result: raise DuplicateKeyError(f"duplicate YAML key: {key!r}")
        result[key] = loader.construct_object(v_node, deep=deep)
    return result
StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)

def load_yaml(path: Path):
    try:
        with path.open("r", encoding="utf-8-sig") as fh: value = yaml.load(fh, Loader=StrictLoader)
    except Exception as exc: raise ValueError(f"cannot parse YAML {path}: {exc}") from exc
    return {} if value is None else value

def items(value): return [] if value is None else (value if isinstance(value, list) else [value])
def add(errors, text): errors.append(text)
def file_exists(path): return path.is_file()
def rel_dir(root, path): return path.relative_to(root).parent.as_posix()

def frontmatter(path):
    text = path.read_text(encoding="utf-8-sig")
    m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.S)
    if not m: return None, None
    fm = m.group(1)
    n = re.search(r"(?m)^name:\s*(.+?)\s*$", fm)
    d = re.search(r"(?m)^description:\s*(.+?)\s*$", fm)
    return (n.group(1).strip() if n else None), (d.group(1).strip() if d else None)

def skill_files(root):
    result = []
    def fail(error):
        raise ValueError(f"cannot inventory Skill files: {error}")
    for current, dirs, files in os.walk(root, topdown=True, followlinks=False, onerror=fail):
        dirs[:] = [d for d in dirs if d not in {
            ".git", ".spec", ".agents", ".codex", ".venv", "__pycache__",
            "node_modules", "_clones", "dist", "build", "assets"
        }]
        if "SKILL.md" in files:
            result.append(Path(current) / "SKILL.md")
    return sorted(result, key=lambda p: p.relative_to(root).as_posix())

def read_three(root):
    return (load_yaml(root/"governance/skill-registry.yaml"), load_yaml(root/"governance/workflow-registry.yaml"), load_yaml(root/"governance/state-registry.yaml"))

def check_registry(root):
    errors=[]
    try: reg,wf,_=read_three(root)
    except ValueError as exc: return [str(exc)]
    by_id={}; paths={}; aliases={}
    for e in items(reg.get("skills")):
        if not isinstance(e,dict): add(errors,"skill registry entry must be a mapping"); continue
        sid=str(e.get("id", "")); path=str(e.get("path", ""))
        if not sid: add(errors,"registry entry missing id"); continue
        if sid in by_id: add(errors,f"duplicate registry id: {sid}")
        by_id[sid]=e
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*",sid): add(errors,f"registry id must be lowercase kebab-case: {sid}")
        for a in items(e.get("legacyAliases")):
            a=str(a)
            if a in aliases: add(errors,f"duplicate legacy alias: {a}")
            elif a==sid: add(errors,f"legacy alias duplicates canonical id: {a}")
            else: aliases[a]=sid
        if e.get("status") not in {"active","external"}: add(errors,f"invalid Skill status: {sid}")
        if e.get("status")=="external": continue
        if not path: add(errors,f"registry entry missing path: {sid}"); continue
        if path in paths: add(errors,f"duplicate registry path: {path}")
        paths[path]=sid
        f=root/Path(path)/"SKILL.md"
        if not file_exists(f): add(errors,f"registry path does not contain SKILL.md: {path}"); continue
        name,_=frontmatter(f)
        if not name: add(errors,f"frontmatter name missing: {path}")
        elif name!=sid: add(errors,f"frontmatter name does not match registry id: {path} -> {name}")
    actual={}
    git_dirs=[]
    try:
        import subprocess
        result=subprocess.run(["git","-C",str(root),"ls-files","-z","--","*/SKILL.md"],capture_output=True,text=True,encoding="utf-8",check=False)
        if result.returncode: add(errors,"git inventory failed: "+result.stderr.strip())
        out=result.stdout.split("\0")
        git_dirs=[Path(x).parent.as_posix() for x in out if x.strip()]
    except OSError as exc: add(errors,f"git inventory failed: {exc}")
    for f in skill_files(root):
        d=rel_dir(root,f); name,_=frontmatter(f)
        for gd in git_dirs:
            if gd.casefold()==d.casefold(): d=gd; break
        if not name: add(errors,f"skill has invalid frontmatter: {f.relative_to(root).as_posix()}"); continue
        if name in actual: add(errors,f"duplicate skill frontmatter name: {name}")
        actual[name]=d
        if name not in by_id: add(errors,f"skill is not registered: {name} ({d})")
        elif by_id[name].get("status")!="external" and by_id[name].get("path")!=d: add(errors,f"registry path casing or value mismatch for {name}: registry={by_id[name].get('path')}, actual={d}")
    for sid,e in by_id.items():
        if e.get("status")!="external" and e.get("path") not in actual.values(): add(errors,f"registry path is not a Skill directory: {e.get('path')}")
    known=set(by_id)
    for alias in aliases:
        if alias in known: add(errors,f"legacy alias conflicts with canonical id: {alias}")
    if len({p.casefold() for p in paths}) != len(paths): add(errors,"case-insensitive registry path collision")
    for w in items(wf.get("workflows")):
        for sid in items(w.get("skills"))+items(w.get("entrySkills")):
            if sid and str(sid) not in known: add(errors,f"workflow {w.get('id')} references unknown canonical skill: {sid}")
    return errors

def check_skill_contract(root, include_legacy=False):
    errors=[]; checked=0
    try: reg=load_yaml(root/"governance/skill-registry.yaml")
    except ValueError as exc: return [str(exc)]
    for e in items(reg.get("skills")):
        if not isinstance(e,dict) or e.get("status")!="active": continue
        level=e.get("contractLevel","v1")
        if level=="legacy-adapter":
            adapter=root/str(e.get("contractPath",""))
            if not adapter.is_file():
                add(errors,f"[{e.get('id')}] adapter contract missing")
            else:
                text=adapter.read_text(encoding="utf-8-sig")
                for section in REQUIRED_SECTIONS:
                    if not re.search(rf"(?m)^##\s+{re.escape(section)}\s*$",text):
                        add(errors,f"[{e.get('id')}] adapter missing section: {section}")
            continue
        if level not in {"v1","legacy-wrapper"}: add(errors,f"[{e.get('id')}] unsupported contractLevel: {level}"); continue
        checked+=1; f=root/str(e.get("path",""))/"SKILL.md"
        if not file_exists(f): add(errors,f"[{e.get('id')}] SKILL.md not found"); continue
        text=f.read_text(encoding="utf-8-sig"); name,desc=frontmatter(f)
        if not text.startswith("---"): add(errors,f"[{e.get('id')}] missing YAML frontmatter")
        if not name: add(errors,f"[{e.get('id')}] missing frontmatter name")
        if not desc: add(errors,f"[{e.get('id')}] missing frontmatter description")
        if name and not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*",name): add(errors,f"[{e.get('id')}] name must be lowercase kebab-case: {name}")
        for section in REQUIRED_SECTIONS:
            if not re.search(rf"(?m)^##\s+{re.escape(section)}\s*$",text): add(errors,f"[{e.get('id')}] missing required section: {section}")
        if re.search(r"(?m)^\s*\[TODO:",text): add(errors,f"[{e.get('id')}] contains unfinished TODO marker")
    if checked==0: add(errors,"no v1 Skill was checked")
    return errors

def artifact_context(root):
    errors=[]
    try: manifest=load_yaml(root/".spec/manifest.yaml"); registry=load_yaml((root if (root/"governance/artifact-registry.yaml").is_file() else Path(__file__).resolve().parent.parent)/"governance/artifact-registry.yaml")
    except ValueError as exc: return {},{},[str(exc)]
    schema = load_yaml(Path(__file__).resolve().parents[1] / "governance/schemas/artifact-manifest.schema.yaml")
    if not isinstance(manifest.get("artifacts"), list):
        errors.append("manifest.artifacts must be a list")
    defs={str(x.get("type")):x for x in items(registry.get("artifacts")) if isinstance(x,dict) and x.get("type")}
    by_id={}; artifacts=items(manifest.get("artifacts"))
    if not manifest.get("projectId"): add(errors,"manifest.projectId is required")
    if not artifacts: add(errors,"manifest.artifacts is empty")
    for a in artifacts:
        if not isinstance(a,dict): add(errors,"manifest artifact must be a mapping"); continue
        aid=str(a.get("artifactId","")); typ=str(a.get("type",""))
        if not aid: add(errors,"artifact missing artifactId")
        elif aid in by_id: add(errors,f"duplicate artifactId: {aid}")
        by_id[aid]=a
        d=defs.get(typ)
        if not d: add(errors,f"unknown artifact type: {aid} -> {typ}")
        required=d.get("required",["artifactId","type","path","lifecycle","owner","status","producedBy","producedAt"]) if d else ["artifactId","type","path","lifecycle","owner","status","producedBy","producedAt"]
        required = set(items(required)) | set(schema["requiredArtifactFields"])
        for field in sorted(required):
            if a.get(field) is None or (isinstance(a.get(field),str) and not a.get(field).strip()): add(errors,f"artifact {aid} missing required field: {field}")
        if a.get("lifecycle") not in LIFECYCLES: add(errors,f"artifact {aid} has invalid lifecycle: {a.get('lifecycle')}")
        if a.get("status") not in STATUSES: add(errors,f"artifact {aid} has invalid status: {a.get('status')}")
        p=Path(str(a.get("path",""))); target=p if p.is_absolute() else root/p
        try: target.resolve().relative_to(root.resolve())
        except ValueError: add(errors,f"artifact path escapes project root: {aid} -> {p}")
        if not file_exists(target): add(errors,f"artifact path does not exist: {aid} -> {p}")
    return manifest,by_id,errors

def check_artifact(root):
    manifest,by_id,errors=artifact_context(root)
    if not by_id: return errors
    for aid,a in by_id.items():
        for field in ("sourceRefs","evidenceRefs","decisionRefs"):
            for ref in items(a.get(field)):
                ref=str(ref)
                if ref not in by_id and not (field=="sourceRefs" and EXTERNAL_REF.fullmatch(ref)): add(errors,f"{aid}.{field} references unknown id: {ref}")
        for ref in items(a.get("evidenceRefs")):
            if ref in by_id and by_id[ref].get("type") not in EVIDENCE_TYPES:
                errors.append(f"{aid}.evidenceRefs must point to evidence: {ref}")
        if a.get("type")!="decision" and a.get("status")=="APPROVED" and not items(a.get("decisionRefs")): add(errors,f"approved artifact requires decisionRefs: {aid}")
        if a.get("type")=="decision" and items(a.get("decisionRefs")): add(errors,f"decision artifact cannot self-authorize via decisionRefs: {aid}")
        for ref in items(a.get("decisionRefs")):
            if ref in by_id and by_id[ref].get("type")!="decision": add(errors,f"{aid}.decisionRefs must point to decision artifacts: {ref}")
    return errors

def check_trace(root):
    errors=[]
    try: t=load_yaml(root/".spec/traceability.yaml")
    except ValueError as exc: return [str(exc)]
    if not t.get("projectId"): add(errors,"traceability.projectId is required")
    schema = load_yaml(Path(__file__).resolve().parents[1] / "governance/schemas/traceability.schema.yaml")
    if not isinstance(t.get("links"), list):
        errors.append("traceability.links must be a list")
    links=items(t.get("links")); ids=set(); relations=set(schema["allowedRelations"])
    if not links: add(errors,"traceability.links is empty")
    for l in links:
        if not isinstance(l,dict): add(errors,"traceability link must be a mapping"); continue
        for f in schema["requiredLinkFields"]:
            if l.get(f) is None or (isinstance(l.get(f),str) and not l.get(f).strip()): add(errors,f"link missing required field: {f}")
        lid=str(l.get("linkId",""))
        if lid in ids: add(errors,f"duplicate linkId: {lid}")
        ids.add(lid)
        if l.get("relation") not in relations: add(errors,f"invalid relation for {lid}: {l.get('relation')}")
        if l.get("lifecycle") not in LIFECYCLES: add(errors,f"invalid lifecycle for {lid}: {l.get('lifecycle')}")
    return errors


def check_link_references(trace, by_id):
    errors=[]
    for l in items(trace.get("links")):
        if not isinstance(l,dict): continue
        for field in ("from","to","evidenceRefs","decisionRefs"):
            vals=[l.get(field)] if field in ("from","to") else items(l.get(field))
            for ref in vals:
                ref=str(ref)
                if ref not in by_id: add(errors,f"{l.get('linkId')}.{field} references unknown local artifact: {ref}")
                elif field=="evidenceRefs" and by_id[ref].get("type") not in EVIDENCE_TYPES: add(errors,f"{l.get('linkId')}.evidenceRefs is not evidence: {ref}")
                elif field=="decisionRefs" and by_id[ref].get("type")!="decision": add(errors,f"{l.get('linkId')}.decisionRefs is not a decision: {ref}")
    return errors

def check_refs(root):
    errors=[]
    try: manifest=load_yaml(root/".spec/manifest.yaml"); wf=load_yaml(root/".spec/workflow.yaml"); trace=load_yaml(root/".spec/traceability.yaml"); states=load_yaml(root/"governance/state-registry.yaml")
    except ValueError as exc: return [str(exc)]
    _,by_id,base=artifact_context(root); errors.extend(base)
    schema = load_yaml(Path(__file__).resolve().parents[1] / "governance/schemas/workflow.schema.yaml")
    for field in schema["requiredRoot"]:
        if field not in wf or wf[field] is None or wf[field] == "":
            errors.append(f"workflow missing required field: {field}")
    if wf.get("lifecycle") not in LIFECYCLES:
        errors.append("workflow has invalid lifecycle")
    for field in ("artifactRefs", "evidenceRefs", "decisionRefs"):
        if not isinstance(wf.get(field), list):
            errors.append(f"workflow.{field} must be a list")
    if wf.get("projectId")!=manifest.get("projectId"): add(errors,"workflow.projectId must match manifest.projectId")
    if trace.get("projectId")!=manifest.get("projectId"): add(errors,"traceability.projectId must match manifest.projectId")
    state_ids={str(x.get("id")) for x in items(states.get("states")) if isinstance(x,dict)}
    if wf.get("state") not in state_ids: add(errors,f"workflow.state is not registered: {wf.get('state')}")
    def wfrefs(field, types=None):
        for ref in items(wf.get(field)):
            ref=str(ref)
            if ref not in by_id: add(errors,f"workflow.{field} references unknown id: {ref}")
            elif types and by_id[ref].get("type") not in types: add(errors,f"workflow.{field} has wrong artifact type: {ref}")
    wfrefs("artifactRefs"); wfrefs("evidenceRefs",EVIDENCE_TYPES); wfrefs("decisionRefs",{"decision"})
    for a in by_id.values():
        for field in ("sourceRefs","evidenceRefs","decisionRefs"):
            for ref in items(a.get(field)):
                ref=str(ref)
                if ref not in by_id and not (field=="sourceRefs" and EXTERNAL_REF.fullmatch(ref)): add(errors,f"{a.get('artifactId')}.{field} references unknown id: {ref}")
        for ref in items(a.get("decisionRefs")):
            if ref in by_id and by_id[ref].get("type")!="decision": add(errors,f"{a.get('artifactId')}.decisionRefs must point to decision: {ref}")
    errors.extend(check_link_references(trace, by_id))
    return errors


def timestamp(value):
    try:
        result = value if isinstance(value, datetime) else datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if result.tzinfo is None:
            raise ValueError("timezone is required")
        return result
    except (ValueError, TypeError) as exc:
        raise ValueError(f"invalid timezone-aware timestamp: {value}") from exc


def approval_context(root, workflow, by_id):
    decisions = {}
    errors = []
    policy_path = root / ".spec/authorization.yaml"
    policy = load_yaml(policy_path) if policy_path.is_file() else {"approvers": []}
    if policy.get("projectId", workflow.get("projectId")) != workflow.get("projectId"):
        errors.append("authorization policy projectId mismatch")
    for aid, item in by_id.items():
        if item.get("type") != "decision":
            continue
        target = (root / item["path"]).resolve()
        if not target.is_relative_to(root.resolve()):
            errors.append(f"decision path escapes root: {aid}")
            continue
        record = load_yaml(target)
        if record.get("decisionId") != aid or record.get("status") != item.get("status"):
            errors.append(f"decision identity/status mismatch: {aid}")
        decisions[aid] = record
    context = dict(workflow)
    context["approvers"] = policy.get("approvers", [])
    return decisions, context, errors


def approval_errors(ref, action, decisions, context, *, exception_id=None, owner=None, artifact_id=None):
    decision = decisions.get(ref, {})
    errors = []
    if not decision or decision.get("status") != "APPROVED" or decision.get("decision") != "approve":
        return [f"approval {ref} is missing or not approved"]
    for field in ("projectId", "executionId"):
        if decision.get(field) != context.get(field):
            errors.append(f"approval {ref} {field} mismatch")
    approver = decision.get("approvedBy")
    policy = context.get("approvers", [])
    if not any(p.get("id") == approver and action in p.get("actions", []) for p in policy if isinstance(p, dict)):
        errors.append(f"approval {ref} approver is not authorized for {action}")
    scope = decision.get("scope", {})
    if action not in scope.get("actions", []):
        errors.append(f"approval {ref} scope does not authorize {action}")
    if exception_id and scope.get("exceptionId") != exception_id:
        errors.append(f"approval {ref} exceptionId mismatch")
    if owner and decision.get("owner") != owner:
        errors.append(f"approval {ref} owner mismatch")
    if artifact_id and artifact_id not in scope.get("artifactIds", []):
        errors.append(f"approval {ref} does not cover artifact {artifact_id}")
    now = datetime.now(timezone.utc)
    try:
        if not timestamp(decision.get("approvedAt")) <= now < timestamp(decision.get("expiresAt")):
            errors.append(f"approval {ref} is expired or not yet effective")
    except ValueError as exc:
        errors.append(f"approval {ref}: {exc}")
    return errors


def gate_check(record, label, by_id, decisions=None, context=None):
    errors = []
    decisions, context = decisions or {}, context or {}
    gate = record.get("gate", record.get("outcome"))
    if gate not in GATES:
        return [f"{label} has invalid gate: {gate}"]
    if type(record.get("allowDownstream")) is not bool:
        errors.append(f"{label}.allowDownstream must be boolean")
    for field in ("reason", "nextAction"):
        if not str(record.get(field, "")).strip():
            errors.append(f"{label} missing {field}")
    risks = record.get("unresolvedRisks", [])
    if not isinstance(risks, list):
        return errors + [f"{label}.unresolvedRisks must be a list"]
    severities = []
    for risk in risks:
        if not isinstance(risk, dict) or risk.get("severity") not in {"P0", "P1", "P2", "P3"}:
            errors.append(f"{label} invalid risk severity")
        else:
            severities.append(risk["severity"])
    if gate == "PASS" and set(severities) & {"P0", "P1"}:
        errors.append(f"{label} PASS cannot contain unresolved P0/P1 risks")
    if gate == "BLOCKED":
        if record.get("allowDownstream") is not False:
            errors.append(f"{label} BLOCKED must set allowDownstream: false")
        for field in ("owner", "requiredInput", "clearanceCondition"):
            if not record.get(field):
                errors.append(f"{label} BLOCKED missing {field}")
    elif not record.get("evidenceRefs"):
        errors.append(f"{label} non-blocked gate requires evidenceRefs")
    if gate == "CONDITIONAL":
        if "P0" in severities:
            errors.append(f"{label} CONDITIONAL cannot contain unresolved P0")
        for field in ("exceptionId", "risk", "owner", "dueAt", "remediation", "approvalRef"):
            if not record.get(field):
                errors.append(f"{label} CONDITIONAL missing {field}")
        try:
            if timestamp(record.get("dueAt")) <= datetime.now(timezone.utc):
                errors.append(f"{label} exception dueAt has expired")
        except ValueError as exc:
            errors.append(str(exc))
        ref = record.get("approvalRef")
        if ref not in items(record.get("decisionRefs")):
            errors.append(f"{label} approvalRef must appear in decisionRefs")
        errors.extend(approval_errors(ref, "accept-risk", decisions, context,
                                      exception_id=record.get("exceptionId"), owner=record.get("owner")))
    for field, types in (("evidenceRefs", EVIDENCE_TYPES), ("decisionRefs", {"decision"})):
        for ref in items(record.get(field)):
            item = by_id.get(ref)
            if not item or item.get("type") not in types:
                errors.append(f"{label}.{field} invalid reference/type: {ref}")
            elif gate != "BLOCKED" and item.get("status") not in {"REVIEW", "APPROVED"}:
                errors.append(f"{label}.{field} cannot use draft/superseded record: {ref}")
    return errors

def check_gate(root):
    workflow = load_yaml(root / ".spec/workflow.yaml")
    _, by_id, errors = artifact_context(root)
    decisions, context, issues = approval_context(root, workflow, by_id)
    errors.extend(issues)
    errors.extend(gate_check(workflow, "workflow", by_id, decisions, context))
    for path in sorted((root / ".spec/gates").glob("*.yaml")):
        record = load_yaml(path)
        for field in ("projectId", "workflowId", "executionId", "lifecycle"):
            if not record.get(field) or record.get(field) != workflow.get(field):
                errors.append(f"{path.name} {field} mismatch")
        errors.extend(gate_check(record, path.name, by_id, decisions, context))
    for aid, item in by_id.items():
        if item.get("status") == "APPROVED" and item.get("type") != "decision":
            if not any(not approval_errors(ref, "approve-artifact", decisions, context, artifact_id=aid)
                       for ref in items(item.get("decisionRefs"))):
                errors.append(f"approved artifact lacks valid scoped approval: {aid}")
    return errors

def check_transitions(root):
    errors=[]
    try: s=load_yaml(root/"governance/state-registry.yaml"); a=load_yaml(root/"governance/artifact-registry.yaml"); skills=load_yaml(root/"governance/skill-registry.yaml")
    except ValueError as exc: return [str(exc)]
    states={str(x.get("id")):x for x in items(s.get("states")) if isinstance(x,dict)}; types={str(x.get("type")) for x in items(a.get("artifacts")) if isinstance(x,dict)}; actors={"workflow","user","system","auto-test","quality-inspection"}|{str(x.get("id")) for x in items(skills.get("skills")) if isinstance(x,dict)}; seen=set()
    for t in items(s.get("transitions")):
        if not isinstance(t,dict): add(errors,"transition must be a mapping"); continue
        tid=str(t.get("id",""))
        if not tid: add(errors,"transition missing id")
        if tid in seen: add(errors,f"duplicate transition id: {tid}")
        seen.add(tid)
        for f in ("from","to","lifecycle","actor","requiredArtifacts","requiredEvidence","requiredOutcome","allowDownstream","failureRoute","reversible","timeoutHours"):
            if f not in t: add(errors,f"{tid} missing transition field: {f}")
        src,dst=str(t.get("from","")),str(t.get("to",""))
        if src not in states or dst not in states: add(errors,f"{tid} references unknown state: {src}->{dst}")
        scope=items(t.get("lifecycle"))
        if not scope or any(x not in LIFECYCLES for x in scope): add(errors,f"{tid} has invalid lifecycle scope: {scope}")
        if str(t.get("actor","")) not in actors: add(errors,f"{tid} references unknown actor: {t.get('actor')}")
        if t.get("requiredOutcome") not in GATES: add(errors,f"{tid} has invalid requiredOutcome: {t.get('requiredOutcome')}")
        if type(t.get("allowDownstream")) is not bool: add(errors,f"{tid}.allowDownstream must be boolean")
        if type(t.get("reversible")) is not bool: add(errors,f"{tid}.reversible must be boolean")
        try:
            if float(t.get("timeoutHours"))<=0: add(errors,f"{tid}.timeoutHours must be positive")
        except (TypeError,ValueError): add(errors,f"{tid}.timeoutHours must be numeric")
        failure=str(t.get("failureRoute",""))
        if failure not in states and failure!="NONE": add(errors,f"{tid} failureRoute is not a state or NONE: {failure}")
        for typ in items(t.get("requiredArtifacts")):
            if str(typ) not in types: add(errors,f"{tid} requiredArtifacts references unknown artifact type: {typ}")
        if dst in BLOCKED_STATES and (t.get("requiredOutcome")!="BLOCKED" or t.get("allowDownstream") is not False): add(errors,f"{tid} enters {dst} without BLOCKED/false")
        if dst=="COMPLETED" and t.get("allowDownstream") is not False: add(errors,f"{tid} entering COMPLETED must close downstream")
        reqa={str(x) for x in items(t.get("requiredArtifacts"))}; reqe={str(x) for x in items(t.get("requiredEvidence"))}
        if dst=="DEV_IN_PROGRESS" and ("tech-design" not in reqa or "tech-review" not in reqe): add(errors,f"{tid} entering DEV_IN_PROGRESS must require tech-design and tech-review")
        if dst=="RELEASE_PLANNING_IN_PROGRESS" and "test-report" not in reqa: add(errors,f"{tid} entering release planning must require test-report")
        if dst=="DEPLOYMENT_IN_PROGRESS" and not {"release-plan","test-report"}.issubset(reqa|{""}): add(errors,f"{tid} entering deployment must require release-plan and test-report")
        if dst=="DEPLOYMENT_IN_PROGRESS" and "test-run" not in reqe: add(errors,f"{tid} entering deployment must require test-run")
    policies = {
        "PRD_APPROVED": ("prd-review", {"prd"}, {"prd-review"}),
        "TECH_DESIGN_APPROVED": ("tech-review", {"tech-design"}, {"tech-review"}),
        "CODE_REVIEW_PASSED": ("code-review", {"code-change"}, {"code-review"}),
        "TEST_IN_PROGRESS": (None, {"code-change"}, {"code-review"}),
        "TEST_PASSED": ("auto-test", {"code-change", "test-report"}, {"code-review", "test-run"}),
        "RELEASE_PLANNING_IN_PROGRESS": (None, {"test-report"}, {"code-review", "test-run"}),
        "DEPLOYMENT_IN_PROGRESS": (None, {"release-plan", "test-report"}, {"code-review", "test-run"}),
    }
    skill_map = {x["id"]: x for x in skills["skills"]}
    roles = set(s.get("evidenceRoles", []))
    pairs = set()
    for t in s["transitions"]:
        pair = (t["from"], t["to"])
        if pair in pairs:
            errors.append(f"duplicate transition edge: {pair}")
        pairs.add(pair)
        for lc in t.get("lifecycle", []):
            for endpoint in pair:
                if lc not in states.get(endpoint, {}).get("lifecycle", []):
                    errors.append(f"{t['id']} lifecycle {lc} is outside state scope: {endpoint}")
            if lc not in skill_map.get(t.get("actor"), {}).get("lifecycle", []):
                errors.append(f"{t['id']} actor does not support lifecycle {lc}")
        if not set(t.get("requiredEvidence", [])).issubset(roles):
            errors.append(f"{t['id']} references unknown evidence role")
        if t["to"] in policies:
            actor, artifacts, evidence = policies[t["to"]]
            if actor and t.get("actor") != actor:
                errors.append(f"{t['id']} requires review actor {actor}")
            if not artifacts.issubset(t.get("requiredArtifacts", [])) or not evidence.issubset(t.get("requiredEvidence", [])):
                errors.append(f"{t['id']} bypasses required review/test evidence")
        if t["to"] == "DEPLOYMENT_IN_PROGRESS" and t.get("requiresAuthorization") != "deploy":
            errors.append(f"{t['id']} deployment requires explicit deploy authorization")
    return errors


def check_graph(root):
    errors = check_transitions(root)
    state_registry = load_yaml(root / "governance/state-registry.yaml")
    workflow_registry = load_yaml(root / "governance/workflow-registry.yaml")
    states = {s["id"]: s for s in state_registry["states"]}
    transitions = state_registry["transitions"]
    if len(states) != len(state_registry["states"]):
        errors.append("duplicate state id")
    for workflow in workflow_registry["workflows"]:
        if "exitGate" in workflow or workflow.get("exitState") not in states:
            errors.append(f"{workflow['id']} must use a registered exitState, not exitGate")
    def walk(starts, edges, excluded=None):
        seen = set(starts) - {excluded}
        queue = deque(seen)
        while queue:
            for target in edges.get(queue.popleft(), []):
                if target not in seen and target != excluded:
                    seen.add(target)
                    queue.append(target)
        return seen
    all_reachable = set()
    for lifecycle in sorted(LIFECYCLES):
        starts = state_registry.get("entryStates", {}).get(lifecycle, [])
        if not starts or any(s not in states for s in starts):
            errors.append(f"invalid entry states for {lifecycle}")
            continue
        forward, reverse = defaultdict(list), defaultdict(list)
        for transition in transitions:
            if lifecycle in transition.get("lifecycle", []):
                forward[transition["from"]].append(transition["to"])
                reverse[transition["to"]].append(transition["from"])
        reachable = walk(starts, forward)
        all_reachable.update(reachable)
        terminals = {sid for sid, s in states.items() if (s.get("terminal") and sid == "COMPLETED") or
                     (s.get("handoffLifecycle") and lifecycle in s.get("handoffFrom", []))}
        finishable = walk(terminals, reverse)
        for sid in sorted(reachable - finishable):
            errors.append(f"{lifecycle} state cannot reach completion or explicit handoff: {sid}")
        if walk(starts, forward, "TEST_PASSED") & {"RELEASE_PLANNING_IN_PROGRESS", "DEPLOYMENT_IN_PROGRESS"}:
            errors.append(f"{lifecycle} can bypass TEST_PASSED before release")
        if "TEST_PASSED" in walk(starts, forward, "CODE_REVIEW_PASSED"):
            errors.append(f"{lifecycle} can bypass CODE_REVIEW_PASSED before tests pass")
    for sid in sorted(set(states) - all_reachable):
        errors.append(f"state unreachable in every lifecycle: {sid}")
    return errors

def check_knowledge(root, strict=False):
    try: r=load_yaml(root/"governance/knowledge-registry.yaml")
    except ValueError as exc: return [str(exc)],[]
    env=str(r.get("rootEnv","")); warnings=[]
    if not env: return ["knowledge registry rootEnv is required"],warnings
    value=os.environ.get(env)
    if not value:
        msg=f"knowledge dependency is not configured; set {env} (policy={r.get('missingPolicy','warn-and-degrade')})"
        return ([msg] if strict or r.get("required") is True else []), [msg] if not strict and r.get("required") is not True else []
    p=Path(value)
    if not p.is_dir(): return [f"knowledge root does not exist: {p}"],warnings
    for x in items(r.get("minimum")):
        if not (p/str(x)).is_file(): return [f"required knowledge asset not found: {x}"],warnings
    return [],warnings


def validate_task(task, state_ids, skill_ids):
    if not isinstance(task, dict):
        return ["task must be a mapping"]
    errors = []
    schema = load_yaml(Path(__file__).resolve().parents[1] / "governance/schemas/task-envelope.schema.yaml")
    for field in schema["requiredTaskFields"]:
        if task.get(field) is None or task.get(field) == "":
            errors.append(f"task missing required field: {field}")
    for field in ("taskId", "projectId", "executionId", "revision", "transitionId", "requestedAction", "nextAction"):
        if not isinstance(task.get(field), str) or not task[field].strip():
            errors.append(f"task.{field} must be a non-empty string")
    if task.get("lifecycle") not in LIFECYCLES:
        errors.append("task has invalid lifecycle")
    for field in ("currentState", "targetState"):
        if task.get(field) not in state_ids:
            errors.append(f"task.{field} is not registered")
    if task.get("requiredSkill") not in skill_ids:
        errors.append("task.requiredSkill is not registered")
    for field in ("inputRefs", "artifactRefs", "evidenceRefs", "decisionRefs", "clearanceEvidenceRefs"):
        values = task.get(field, [])
        if not isinstance(values, list) or any(not isinstance(v, str) or not v for v in values):
            errors.append(f"task.{field} must be a list of non-empty IDs")
    scope = task.get("scope")
    if not isinstance(scope, dict):
        errors.append("task.scope must be a mapping")
    else:
        for field in ("allowedPaths", "forbiddenPaths"):
            values = scope.get(field, [])
            if not isinstance(values, list):
                errors.append(f"task.scope.{field} must be a list")
                continue
            for value in values:
                if not isinstance(value, str) or not value.strip():
                    errors.append(f"task.scope.{field} must contain non-empty paths")
                    continue
                path = PureWindowsPath(value)
                if path.drive or path.root or ".." in path.parts or ":" in value:
                    errors.append(f"task.scope.{field} must contain project-relative paths: {value}")
    authorization = task.get("authorization")
    if not isinstance(authorization, dict):
        errors.append("task.authorization must be a mapping")
    else:
        for field in ("actor", "grantedBy", "grantedAt", "approvalRef"):
            if not authorization.get(field):
                errors.append(f"task.authorization missing {field}")
        try:
            timestamp(authorization.get("grantedAt"))
        except ValueError as exc:
            errors.append(str(exc))
    output = task.get("expectedOutput")
    if not isinstance(output, dict):
        errors.append("task.expectedOutput must be a mapping")
    else:
        for field in ("artifactType", "path"):
            if not isinstance(output.get(field), str) or not output[field].strip():
                errors.append(f"task.expectedOutput missing {field}")
        checks = output.get("acceptanceChecks")
        if not isinstance(checks, list) or any(not isinstance(c, str) or not c.strip() for c in checks):
            errors.append("task.expectedOutput.acceptanceChecks must be a list of checks")
    gate = task.get("gate")
    if not isinstance(gate, dict):
        errors.append("task.gate must be a mapping")
    else:
        if gate.get("outcome") not in GATES:
            errors.append("task.gate.outcome is invalid")
        if "gate" in gate:
            errors.append("task.gate ambiguous gate/outcome keys")
        if type(gate.get("allowDownstream")) is not bool:
            errors.append("task.gate.allowDownstream must be boolean")
    return errors

def check_task(root):
    try:
        task_root=load_yaml(root/"shared/templates/task-envelope.yaml")
        state=load_yaml(root/"governance/state-registry.yaml")
        skills=load_yaml(root/"governance/skill-registry.yaml")
    except ValueError as exc: return [str(exc)]
    state_ids={str(x.get("id")) for x in items(state.get("states")) if isinstance(x,dict)}
    skill_ids={str(x.get("id")) for x in items(skills.get("skills")) if isinstance(x,dict) and x.get("status")!="external"}
    if not isinstance(task_root,dict) or not isinstance(task_root.get("task"),dict): return ["task envelope must contain a task mapping"]
    return validate_task(task_root["task"],state_ids,skill_ids)

def check_fixture(root, kind):
    if kind == "manifest":
        return artifact_context(root)[2]
    return check_trace(root)

def check_system(root, skip_fixtures=False, skip_knowledge=False, strict=False):
    errors=[]
    for p in (".spec/manifest.yaml",".spec/traceability.yaml",".spec/workflow.yaml"):
        if not file_exists(root/p): add(errors,f"root self-spec is required: {p}")
    checks=[("registry",lambda:check_registry(root)),("skill-contract",lambda:check_skill_contract(root,True)),("graph",lambda:check_graph(root)),("transition",lambda:check_transitions(root)),("artifact",lambda:check_artifact(root)),("trace",lambda:check_trace(root)),("refs",lambda:check_refs(root)),("gate",lambda:check_gate(root)),("task",lambda:check_task(root))]
    if not skip_knowledge:
        knowledge_errors, warnings = check_knowledge(root, strict)
        errors.extend(f"knowledge: {e}" for e in knowledge_errors)
        for warning in warnings:
            print("WARNING: " + warning, file=sys.stderr)
    for name, fn in checks:
        try:
            errors.extend(f"{name}: {e}" for e in fn())
        except (ValueError, OSError, KeyError, TypeError, AttributeError) as exc:
            errors.append(f"{name}: invalid document: {exc}")
    if not skip_fixtures:
        d=root/"scripts/fixtures"
        if d.is_dir():
            for f in sorted(x for x in d.iterdir() if x.is_dir()):
                errors.extend(f"fixture {f.name} manifest: {e}" for e in check_fixture(f,"manifest"))
                errors.extend(f"fixture {f.name} traceability: {e}" for e in check_fixture(f,"trace"))
    return errors

def main(argv=None):
    parser = argparse.ArgumentParser()
    commands = {"registry": check_registry, "artifact": check_artifact, "trace": check_trace,
                "refs": check_refs, "gate": check_gate, "transition": check_transitions,
                "graph": check_graph, "task": check_task}
    parser.add_argument("command", choices=[*commands, "skill-contract", "knowledge", "system"])
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--include-legacy", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--skip-fixtures", action="store_true")
    parser.add_argument("--skip-knowledge", action="store_true")
    args = parser.parse_args(argv)
    root = Path(args.project_root).resolve()
    try:
        if args.command in commands:
            errors = commands[args.command](root)
        elif args.command == "skill-contract":
            errors = check_skill_contract(root, args.include_legacy)
        elif args.command == "knowledge":
            errors, warnings = check_knowledge(root, args.strict)
            for warning in warnings:
                print("WARNING: " + warning, file=sys.stderr)
        else:
            errors = check_system(root, args.skip_fixtures, args.skip_knowledge, args.strict)
            import subprocess
            result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s",
                                     str(Path(__file__).resolve().parent / "tests"), "-p", "test_*.py", "-v"], check=False)
            if result.returncode:
                errors.append("regression tests failed")
    except (ValueError, OSError, KeyError, TypeError, AttributeError) as exc:
        errors = [f"invalid document: {exc}"]
    for error in errors:
        print(error, file=sys.stderr)
    print(f"{args.command} validation " + (f"failed: {len(errors)} error(s)" if errors else "passed"))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

