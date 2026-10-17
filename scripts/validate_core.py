from __future__ import annotations
import argparse, hashlib, os, re, shutil, subprocess, sys
from datetime import datetime, timezone
from collections import defaultdict, deque
from pathlib import Path, PureWindowsPath
from typing import Any
import yaml

LIFECYCLES = {"CREATE", "CHANGE", "DEFECT", "REFACTOR", "INCIDENT", "OPTIMIZE"}
GATES = {"PASS", "CONDITIONAL", "BLOCKED"}
PRODUCT_BASELINE_TYPES = {"product-definition", "application-blueprint", "feature-decision"}
PRD_BASELINE_STATES = {"PRD_IN_PROGRESS", "PRD_REVIEW_IN_PROGRESS", "PRD_APPROVED"}
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

def project_path(root, value):
    """Resolve a manifest `path` inside the project root; refuse traversal and symlink escape."""
    if not isinstance(value, str) or not value.strip():
        return None, "path must be a non-empty project-relative string"
    portable = value.replace("\\", "/")
    candidate = Path(portable)
    if candidate.is_absolute() or PureWindowsPath(value).drive or ".." in candidate.parts or ":" in portable:
        return None, f"path must be project-relative without traversal: {value}"
    target = (root / candidate).resolve()
    if not target.is_relative_to(root.resolve()):
        return None, f"path escapes project root: {value}"
    return target, None

def sha256_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def check_digests(root, by_id):
    """Mechanical enforcement of declared content digests.

    A ledger that says a baseline is APPROVED must be falsifiable against the bytes on disk:
    tampering with an artifact body while leaving the ledger untouched is the failure mode
    this exists to catch, so declared digests are always compared and never trusted.
    Requiring digests only applies from `requiredAfter` onward, so pre-existing unbound
    approvals surface as migration debt instead of masquerading as fresh regressions.
    """
    errors = []
    schema = load_yaml(Path(__file__).resolve().parents[1] / "governance/schemas/artifact-manifest.schema.yaml")
    digest_spec = schema.get("digestFields", {}) if isinstance(schema, dict) else {}
    required_status = str(digest_spec.get("requiredForStatus", "APPROVED"))
    required_after = str(digest_spec.get("requiredAfter", ""))
    for aid, item in by_id.items():
        if item.get("type") == "decision":
            continue
        declared = item.get("contentDigest")
        target, path_error = project_path(root, item.get("path"))
        if declared is None:
            approved = item.get("status") == required_status
            produced_at = str(item.get("producedAt") or item.get("approvedAt") or "")[:10]
            if approved and required_after and produced_at and produced_at >= required_after:
                add(errors, f"{aid} {required_status} artifact requires contentDigest (required since {required_after})")
            continue
        if path_error:
            add(errors, f"{aid} contentDigest cannot be verified: {path_error}")
            continue
        if not target.is_file():
            add(errors, f"{aid} contentDigest cannot be verified: file missing {item.get('path')}")
            continue
        try:
            actual = sha256_file(target)
        except OSError as exc:
            add(errors, f"{aid} contentDigest unreadable: {exc}")
            continue
        if actual != str(declared).removeprefix("sha256:"):
            add(errors, f"{aid} contentDigest mismatch with file on disk: {item.get('path')}")
    bindings, structural = subject_bindings(root, by_id)
    errors.extend(structural)
    for ref, rows in sorted(bindings.items()):
        latest = max(rows, key=lambda row: row[0])
        if latest[2] != latest[3]:
            add(errors, f"{ref}.subjectDigests mismatch for {latest[1]}: baseline drifted after approval"
                        f"（最新绑定时间 {latest[0]}，正文改后台账未重签）")
    return errors

def attested_at(value):
    """Normalise producedAt to a 14-digit key; the ledger mixes '…T09:34:00' and '… 09:34:00',
    and raw string ordering picks the wrong latest attestation (space sorts before 'T')."""
    return re.sub(r"[^0-9]", "", str(value or ""))[:14].ljust(14, "0")

def subject_bindings(root, by_id):
    """Every subjectDigests attestation resolved against today's bytes: ref -> [(time, evidence, declared, actual)].

    An attestation means "these are the bytes I reviewed at that moment" (see
    governance/schemas/artifact-manifest.schema.yaml). Only the newest one per subject is a
    promise about the present; older snapshots necessarily stop matching once the artifact
    legitimately evolves, so reporting them as drift turns 13 real findings into 153 noises.
    """
    bindings = defaultdict(list)
    errors = []
    for aid, item in by_id.items():
        subjects = item.get("subjectDigests")
        if subjects is None:
            continue
        if not isinstance(subjects, dict):
            add(errors, f"{aid}.subjectDigests must be a mapping of artifactId to sha256")
            continue
        for ref, declared in subjects.items():
            subject = by_id.get(str(ref))
            if not subject:
                add(errors, f"{aid}.subjectDigests references unknown artifact: {ref}")
                continue
            target, path_error = project_path(root, subject.get("path"))
            if path_error:
                add(errors, f"{aid}.subjectDigests cannot verify {ref}: {path_error}")
                continue
            if not target.is_file():
                add(errors, f"{aid}.subjectDigests cannot verify {ref}: file missing {subject.get('path')}")
                continue
            try:
                actual = sha256_file(target)
            except OSError as exc:
                add(errors, f"{aid}.subjectDigests cannot read {ref}: {exc}")
                continue
            bindings[str(ref)].append((attested_at(item.get("producedAt") or item.get("approvedAt")),
                                       aid, str(declared).removeprefix("sha256:"), actual))
    return bindings, errors

def attestation_drift(root):
    """Subjects whose newest attestation no longer matches disk — the re-sign queue.

    Read-only by design: re-signing is an approval act, so tooling lists the candidates and
    never rewrites the ledger (that would launder "changed after approval" into "approved").
    """
    manifest, by_id, errors = artifact_context(root)
    if not by_id:
        return [], errors
    bindings, structural = subject_bindings(root, by_id)
    rows = []
    for ref, bindings_for_ref in sorted(bindings.items()):
        latest = max(bindings_for_ref, key=lambda row: row[0])
        if latest[2] == latest[3]:
            continue
        subject = by_id.get(ref) or {}
        head = str(subject.get("sha256Head") or "")
        target, _ = project_path(root, subject.get("path"))
        disk = sha256_file(target) if target and target.is_file() else ""
        head_state = "head 也不一致" if head and not disk.startswith(head) else ("head 已跟新" if head else "无 head 字段")
        rows.append({"subject": ref, "path": subject.get("path"), "status": subject.get("status"),
                     "evidence": latest[1], "attestedAt": latest[0], "declared": latest[2], "actual": latest[3],
                     "headState": head_state,
                     "supersededBindings": sum(1 for row in bindings_for_ref if row[2] != row[3]) - 1})
    return rows, structural

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
            "node_modules", "_clones", "dist", "build", "assets",
            # 评测夹具里的 SKILL.md 是被测数据，不是本仓的 skill：它们自带一份迷你
            # governance/skill-registry.yaml，跑在临时复制出来的项目根里。把它们当 skill 清点，
            # 要么逼着真注册表登记假条目（污染 skill 名录），要么门禁永远红——两者都比这条规则本身坏。
            # 残留风险：把真 skill 藏进 fixtures/ 目录可以躲过这条清点，靠 registry 侧的
            # 「registry path is not a Skill directory」与 eval 用例的判绿对照兜。
            "fixtures"
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
        supersedes={str(x) for x in items(a.get("supersedes"))}
        if a.get("status")!="SUPERSEDED":
            for ref in items(a.get("sourceRefs")):
                origin=by_id.get(str(ref))
                if origin and origin.get("status")=="SUPERSEDED" and str(ref) not in supersedes:
                    add(errors,f"{aid} is built on a superseded baseline via sourceRefs: {ref}")
        for ref in items(a.get("decisionRefs")):
            if ref in by_id and by_id[ref].get("type")!="decision": add(errors,f"{aid}.decisionRefs must point to decision artifacts: {ref}")
    errors.extend(check_digests(root, by_id))
    return errors

def check_trace(root):
    errors=[]
    try: t=load_yaml(root/".spec/traceability.yaml")
    except ValueError as exc: return [str(exc)]
    body = t.get("traceability") if isinstance(t.get("traceability"), dict) else {}
    if not t.get("links") and not t.get("projectId") and body.get("requirements"):
        # knowledge-bases 交的是 REQ/AC 索引，与链路台账同名不同物。报三条"结构不合契约"
        # 会把人引去改索引文件，实际缺的是另一份台账 —— 判据要说清缺哪一份
        return ["traceability.yaml 是 REQ/AC 索引（requirements），不是链路台账：链路台账缺失（需 projectId + links）"]
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
    # Pre-handoff checkpoint must be falsifiable against bytes on disk: reviewers read `gate`,
    # so digest drift has to fail here too, not only in `artifact`.
    errors.extend(check_digests(root, by_id))
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
        "PRD_IN_PROGRESS": (None, PRODUCT_BASELINE_TYPES, set()),
        "PRD_REVIEW_IN_PROGRESS": (None, PRODUCT_BASELINE_TYPES | {"prd"}, set()),
        "PRD_APPROVED": ("prd-review", PRODUCT_BASELINE_TYPES | {"prd"}, {"prd-review"}),
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

# ── 进化台账 before/after 执法（plan v2 §3 台账规则 / §5 闭环「记 before→after」那一段）────────────
# 规则原文：每条进化必须挂 before/after，无指标一律标「未验证」，禁止写「已优化」。此前纯纸面。
# 判据全部在 governance/obs-registry.yaml 的 evolutionLedger 节（同「生效日从 schema 读」的先例），
# 代码只执行；本命令只读台账，绝不改写、绝不替人补指标。
EVOLUTION_KEYS = ("path", "entryHeading", "fields", "claimWords", "forbiddenWords", "beforePattern",
                  "afterPattern", "sourcePattern", "acceptedSources", "honestVerdict",
                  "claimingVerdict", "verdictValues", "reasons", "requiredFields",
                  "commitPointerPattern", "rollbackTargetPattern", "naToken", "naReasonPattern", "git")
_ENTRY_FIELD = re.compile(r"^\s*[-*]?\s*\**(?P<name>[^*：:]+?)\**\s*[:：]\s*(?P<value>.*)$")
_FENCE = re.compile(r"^\s*(```|~~~)")
# 只读 git 查询。写操作型 git 命令（add/commit/checkout/reset…）在本执法器里一律不存在：
# 台账只被读，回滚指针只被验真，回滚动作属人。
_GIT_CAT_FILE = "cat-file"
_GIT_REV_PARSE = "rev-parse"


def evolution_policy(root):
    path = root / "governance" / "obs-registry.yaml"
    if not path.is_file():
        raise ValueError("判据注册表 governance/obs-registry.yaml 不存在 ⇒ 无法执法，不猜口径")
    section = load_yaml(path).get("evolutionLedger")
    if not isinstance(section, dict):
        raise ValueError("governance/obs-registry.yaml 未声明 evolutionLedger 判据 ⇒ 不猜口径")
    missing = [key for key in EVOLUTION_KEYS if not section.get(key)]
    if missing:
        raise ValueError(f"evolutionLedger 缺必需判据键 {missing} ⇒ 拒绝用默认值冒充实装")
    return section


def git_repos(root):
    """commit 指针在哪些仓里验真：项目根优先，退回校验器所在仓根（台账记的多是本仓 commit）。"""
    repos = []
    for candidate in (Path(root), Path(__file__).resolve().parents[1]):
        if candidate not in repos and (candidate / ".git").exists():
            repos.append(candidate)
    return repos


def commit_exists(repos, sha):
    """只读 `git cat-file -e <sha>^{commit}`。返回 True/False；查不了返回 None（不是 False）。

    True/False/None 三态是刻意的：把「git 没装／两处都不是 git 仓」混成 False，
    报错就会指着一条合法 commit 说它不存在；混成 True 更糟——漂亮 sha 字符串直接过关。
    """
    git = shutil.which("git")
    if not git or not repos:
        return None
    answered = False
    for repo in repos:
        try:
            probe = subprocess.run([git, "-C", str(repo), _GIT_CAT_FILE, "-e", f"{sha}^{{commit}}"],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
        except (OSError, subprocess.SubprocessError):
            continue
        answered = True
        if probe.returncode == 0:
            return True
    return False if answered else None


def _sha_pointers(text, pattern):
    """台账字段值里所有像 commit 指针的连续十六进制串（7–40 位，带词边界）。"""
    return re.findall(str(pattern), str(text or ""))


def _dequote(text):
    """剥掉模板尖括号占位与「」角引号里的被禁止措辞：说明文字不是声称（防误伤模板自身）。"""
    stripped = re.sub(r"<[^>]*>", "", str(text or ""))
    return re.sub(r"「[^」]*」|“[^”]*”", "", stripped)


def _entry_field(body, name):
    for number, line in body:
        match = _ENTRY_FIELD.match(line)
        if match and match.group("name").strip() == name:
            return number, match.group("value").strip()
    return None, None


def _claim_lines(lines, words):
    """命中声称词的具体行号（行内先剥引号/占位，避免把模板说明读成声称）。"""
    hits = []
    for number, line in lines:
        cleaned = _dequote(line)
        hits += [(number, word) for word in words if word in cleaned]
    return hits


def _side_segment(text, token, stop_token):
    """取 `before …` / `after …` 各自那一段（before 段止于 after，after 段到行尾）。"""
    value = str(text or "")
    index = value.find(str(token))
    if index < 0:
        return None
    tail = value[index + len(str(token)):]
    if stop_token:
        cut = tail.find(str(stop_token))
        if cut >= 0:
            tail = tail[:cut]
    return tail


def _proof_side_errors(relative, proof_line, proof, proof_value, pol, state, reasons):
    """before/after 两侧：要么给可核数值＋允许量具，要么显式 N/A（并写清为什么取不到）。"""
    errors = []
    na_token = str(pol["naToken"])
    before_token = str(pol.get("beforeToken", "before"))
    after_token = str(pol.get("afterToken", "after"))
    absent = []
    if not re.search(r"[0-9]", proof_value) and na_token not in proof_value:
        absent.append(reasons["noNumber"])
    else:
        for token, pattern_key, reason_key in ((before_token, "beforePattern", "noBefore"),
                                               (after_token, "afterPattern", "noAfter")):
            segment = _side_segment(proof_value, token, after_token if token == before_token else None)
            if segment is None:
                absent.append(reasons[reason_key])
                continue
            if na_token in segment:
                if not re.search(str(pol["naReasonPattern"]), segment):
                    absent.append(f"{reasons['badNaWithoutReason']}（{token} 侧原文：{segment.strip()[:60]}）")
                if state == "claiming":
                    absent.append(f"{reasons['naWithClaimed']}（{token} 侧为 N/A）")
                continue
            if not re.search(str(pol[pattern_key]), f"{token}{segment}"):
                absent.append(f"{reasons[reason_key]}（{token} 侧原文：{segment.strip()[:60] or '空'}）")
    if not absent:
        sources = [str(src) for src in items(pol["acceptedSources"])]
        pointers = re.findall(str(pol["sourcePattern"]), proof)
        if not any(any(src in pointer for src in sources) for pointer in pointers):
            absent.append(f"{reasons['noSource']}（允许量具：{'、'.join(sources)}）")
    if absent:
        errors.append(f"{relative}:{proof_line}: " + "；".join(str(item) for item in absent)
                      + f"（本行原文：{(proof or '')[:120]}）")
    return errors


def _pointer_errors(relative, line, field_name, value, pol, repos, reasons, require_command):
    """commit／回滚指针验真：只读 git cat-file；sha 不存在必红，git 查不了也必红（不判绿）。"""
    commit_name = str(pol["fields"]["commit"])
    is_commit = str(field_name) == commit_name
    shas = _sha_pointers(value, pol["commitPointerPattern"])
    if not shutil.which("git") or not repos:
        return [f"{relative}:{line}: {reasons['gitUnavailable']}"
                f"（待验指针：{'、'.join(shas) or '无'}；本执法器只读，不会代跑 git init）"]
    errors = []
    if not shas:
        errors.append(f"{relative}:{line}: {reasons['noRollbackTarget' if not is_commit else 'noCommitPointer']}"
                      f"（本行原文：{(value or '')[:120]}）")
    if require_command and not re.search(str(pol["rollbackTargetPattern"]), str(value or "")):
        errors.append(f"{relative}:{line}: {reasons['noRollbackTarget']}"
                      f"（判据：需 `git revert`/`git checkout` 形式的可执行目标；本行原文：{(value or '')[:120]}）")
    probed = []
    for sha in shas:
        state = commit_exists(repos, sha)
        if state is None:
            errors.append(f"{relative}:{line}: {reasons['gitUnavailable']}（指针 {sha}）")
        elif state is False:
            errors.append(f"{relative}:{line}: 「{field_name}」{reasons['commitNotFound']}"
                          f"（指针 {sha}；查询：{pol['git']['verifyCommand']}）")
        else:
            probed.append(sha)
    if probed and not errors:
        return []
    return errors


def evolution_audit(root, ledger=None) -> dict:
    """逐条判定进化台账：声称生效必须挂 before+after 可核数值与出处；「未验证」是诚实态，放行。"""
    pol = evolution_policy(root)
    reasons = pol["reasons"]
    relative = str(ledger or pol["path"]).replace("\\", "/")
    path, error = project_path(root, relative)
    empty = {"file": relative, "entries": [], "errors": [], "counts": {}}
    if error:
        return {**empty, "errors": [f"{relative}: 台账路径非法：{error}"]}
    if not path.is_file():
        return {**empty, "errors": [f"{relative}: {reasons['missingLedger']}"]}
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        return {**empty, "errors": [f"{relative}: {reasons['unreadable']}（{exc}）"]}

    in_fence, scannable = False, []
    for number, line in enumerate(lines, 1):
        if _FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            scannable.append((number, line))

    heading = re.compile(str(pol["entryHeading"]))
    marks = [(number, line) for number, line in scannable if heading.match(line)]
    proof_name = str(pol["fields"]["proof"])
    verdict_name = str(pol["fields"]["verdict"])
    commit_name = str(pol["fields"]["commit"])
    rollback_name = str(pol["fields"]["rollback"])
    claims_words = [str(word) for word in items(pol["claimWords"])]
    forbidden_words = [str(word) for word in items(pol["forbiddenWords"])]
    repos = git_repos(root)
    entries = []
    for index, (start, title) in enumerate(marks):
        stop = marks[index + 1][0] - 1 if index + 1 < len(marks) else max(start, len(lines))
        body = [(number, line) for number, line in scannable if start < number <= stop]
        verdict_line, verdict = _entry_field(body, verdict_name)
        proof_line, proof = _entry_field(body, proof_name)
        commit_line, commit = _entry_field(body, commit_name)
        rollback_line, rollback = _entry_field(body, rollback_name)
        proof_value = _dequote(proof)
        verdict_clean = _dequote(verdict).strip() if verdict else ""
        if not (verdict_line and verdict_clean):
            state = "missing"
        elif str(pol["honestVerdict"]) in verdict_clean:
            state = "honest"
        elif str(pol["claimingVerdict"]) in verdict_clean:
            state = "claiming"
        else:
            state = "unknown"
        forbidden_hits = _claim_lines([(start, title)] + body, forbidden_words)
        claim_hits = [hit for hit in _claim_lines([(start, title)] + body, claims_words)
                      if hit[1] not in forbidden_words]
        errors = []
        demanding = state == "claiming" or bool(claim_hits) or bool(forbidden_hits)

        # ① 必需字段行本身不许缺——「未验证」是合法态，但合法不等于可以留白。
        for name in [str(field) for field in items(pol["requiredFields"])]:
            present = {"效果证据": proof_line, "判定": verdict_line,
                       "落账 commit": commit_line, "回滚方式": rollback_line}
            line = present.get(name)
            if line is not None:
                continue
            declared = next((key for key, value in (pol["fields"] or {}).items()
                             if str(value) == name), None)
            if declared == "proof" and line is None and (demanding or state == "claiming"):
                claimed = (verdict or "").strip() or "、".join(w for _, w in claim_hits + forbidden_hits)
                errors.append(f"{relative}:{start}: {reasons['noProofField']}（本条声称：{claimed[:80]}）")
                continue
            errors.append(f"{relative}:{start}: "
                          + str(reasons["missingField"]).replace("{field}", name))

        # ② before/after：两侧都要有可核数值；取不到只能写 N/A + 原因，且 N/A 不许配「已验证」。
        if proof_line is not None:
            errors += _proof_side_errors(relative, proof_line, proof, proof_value, pol, state, reasons)

        # ③ commit 指针与回滚指针：机械验真，引用不存在的 commit 必红。
        if commit_line is not None:
            errors += _pointer_errors(relative, commit_line, commit_name, commit, pol,
                                      repos, reasons, require_command=False)
        if rollback_line is not None:
            errors += _pointer_errors(relative, rollback_line, rollback_name, rollback, pol,
                                      repos, reasons, require_command=True)

        for number, word in forbidden_hits:
            errors.append(f"{relative}:{number}: {reasons['forbiddenWord']}（命中原词「{word}」）")
        if state == "honest" and claim_hits:
            number, word = claim_hits[0]
            errors.append(f"{relative}:{number}: {reasons['contradiction']}（命中原词「{word}」）")
        if state == "unknown" and not any(number == verdict_line for number, _ in forbidden_hits):
            # 同一行已经因禁词报红就不再叠一条「判定值非法」：两条同址的红只会淹没真问题
            errors.append(f"{relative}:{verdict_line}: {reasons['badVerdict']}"
                          f"（判定值：{(verdict or '')[:40]}）")
        pointer_keys = ("commitNotFound", "noCommitPointer", "noRollbackTarget", "gitUnavailable")
        pointer_issues = [error for error in errors
                          if any(str(reasons[key]) in error for key in pointer_keys)]
        entries.append({"line": start, "title": title.strip(), "state": state,
                        "verdict": (verdict or "")[:120], "verdictLine": verdict_line,
                        "proof": (proof or "")[:200], "proofLine": proof_line,
                        "commit": (commit or "")[:120], "commitLine": commit_line,
                        "rollback": (rollback or "")[:160], "rollbackLine": rollback_line,
                        "pointersVerified": bool(commit_line and rollback_line and not pointer_issues),
                        "claims": [f"{number}:{word}" for number, word in claim_hits],
                        "errors": errors})
    flagged = [error for entry in entries for error in entry["errors"]]
    counts = {
        "entries": len(entries),
        "withProof": sum(1 for entry in entries if entry["state"] == "claiming" and not entry["errors"]),
        "honest": sum(1 for entry in entries if entry["state"] == "honest" and not entry["errors"]),
        "silent": sum(1 for entry in entries if not entry["errors"] and entry["state"] == "missing"),
        "unknownVerdict": sum(1 for entry in entries if entry["state"] == "unknown"),
        "pointersVerified": sum(1 for entry in entries if entry["pointersVerified"]),
        "red": len(flagged),
    }
    return {"file": relative, "entries": entries, "errors": flagged, "counts": counts, "policy": pol}


def check_evolution(root, ledger=None):
    """门禁入口：红＝声称生效却无可核 before/after、写了禁词、判定自相矛盾、台账读不动。"""
    try:
        return evolution_audit(root, ledger)["errors"]
    except ValueError as exc:
        return [str(exc)]


def render_evolution(result) -> str:
    counts, entries = result["counts"], result["entries"]
    pol = result.get("policy") or {}
    buckets = (pol.get("verdictBuckets") or {}) if isinstance(pol, dict) else {}
    git = (pol.get("git") or {}) if isinstance(pol, dict) else {}
    lines = [f"# 进化台账 before/after 执法（{result['file']}）", ""]
    lines.append(f"- 台账条目 **{counts['entries']}** 条：挂 before/after 且判绿 **{counts['withProof']}** 条"
                 f"｜诚实「{pol.get('honestVerdict','未验证')}」**{counts['honest']}** 条"
                 f"｜commit＋回滚指针已机械验真 **{counts['pointersVerified']}** 条"
                 f"｜判据不合规 **{counts['red']}** 处（可能集中在同一条）"
                 f"｜未声称生效 {counts['silent']} 条｜判定值枚举外 {counts['unknownVerdict']} 条")
    lines.append(f"- 真相源：{pol.get('truthSource','') if isinstance(pol, dict) else ''}")
    lines.append(f"- commit 指针验真方式：`{git.get('verifyCommand','') if isinstance(git, dict) else ''}`"
                 f"（只读；本执法器不执行任何写操作型 git 命令、不自动回滚、不改写台账）")
    lines.append("")
    if entries:
        lines += ["| 行 | 条目 | 判定 | 效果证据 | 落账 commit | 回滚 | 本条结论 |",
                  "|---|---|---|---|---|---|---|"]
        for entry in entries:
            verdict = entry["verdict"] or "N/A（缺判定行）"
            proof = (entry["proof"] or "N/A（缺效果证据行）").replace("|", "／")
            commit = (entry.get("commit") or "N/A（缺落账 commit 行）").replace("|", "／")
            rollback = (entry.get("rollback") or "N/A（缺回滚方式行）").replace("|", "／")
            outcome = "⛔ 红" if entry["errors"] else ("✅ 绿" if entry["state"] != "missing" else "— 未声称生效")
            lines.append(f"| {entry['line']} | {entry['title'][:40]} | {verdict[:24]} | {proof[:60]} "
                         f"| {commit[:40]} | {rollback[:40]} | {outcome} |")
        lines.append("")
        for entry in entries:
            for error in entry["errors"]:
                lines.append(f"- ⛔ {error}")
        lines.append("")
        quiet = [entry for entry in entries if not entry["errors"] and entry["state"] in ("missing", "unknown")]
        if quiet:
            lines.append(f"不判红但如实报数（{len(quiet)} 条，既不默认它成立、也不默认它没事）：")
            lines += [f"- {result['file']}:{entry['line']}：{entry['title'][:40]}"
                      f"（{'判定值枚举外' if entry['state']=='unknown' else '没有判定值，也没有声称生效'}）"
                      for entry in quiet]
            lines.append("")
        for key in ("claimedWithProof", "honestUnverified", "silent", "unknownVerdict"):
            if buckets.get(key):
                lines.append(f"- 口径：{buckets[key]}")
        lines.append("")
    else:
        lines.append("台账里还没有任何进化条目（0 条）⇒ 没有可判对象。**这是「空集通过」，不是达标**：")
        lines.append("执法器本身由 `scripts/tests` 的合成夹具做反向对照钉住，真实条目一出现就按同一判据判。")
        lines.append("把 `passed` 读成「进化都验证过了」就是本仓要防的自欺——今天之前它正是这么骗过人的。")
        lines.append("")
    lines.append("复算：`./.venv/Scripts/python.exe scripts/validate_core.py evolution --project-root .`")
    return "\n".join(lines) + "\n"


# ── 目标台账执法：「忘记目标」不再靠人提醒，门禁直接失败（判据在 governance/goal-plan.yaml，代码只执行）。
GOALPLAN_FILE = "governance/goal-plan.yaml"
GOALPLAN_SECTIONS = ("purpose", "sources", "statuses", "proofRules", "countRules", "nextRules", "next", "goals")
GOAL_ENTRY_KEYS = ("id", "ledgerRow", "panelId", "layer", "label", "status", "criteria", "basis")
PROOF_RULE_KEYS = ("doneNeeds", "naIsNotProof", "unverifiableIsRed")
NEXT_RULE_KEYS = ("required", "cellMustExist", "doneCellIsRed", "ledgerMustQuoteTask")
STATUS_MARKS = {"done": "☑", "doing": "◐", "todo": "☐"}
_LEDGER_ROW = re.compile(r"^\|\s*(?P<row>\d+)\s*\|")
_COUNT_LINE = re.compile(r"☑\s*完成\s*(?P<done>\d+).*?◐\s*进行中\s*(?P<doing>\d+).*?☐\s*未完成\s*(?P<todo>\d+)")


def goalplan_policy(root):
    """别的项目没有长期目标台账 ⇒ 返回 None 判「不适用」；本仓缺这份文件由单测钉住（执法不绑宿主路径）。"""
    path = Path(root) / GOALPLAN_FILE
    if not path.is_file():
        return None
    data = load_yaml(path)
    missing = [key for key in GOALPLAN_SECTIONS if not data.get(key)]
    if missing:
        raise ValueError(f"{GOALPLAN_FILE} 缺必需节 {missing} ⇒ 不猜判据，也不猜状态枚举")
    unknown = [key for key in data["statuses"] if key not in STATUS_MARKS]
    if unknown:
        raise ValueError(f"{GOALPLAN_FILE}.statuses 出现三态之外的值 {unknown} ⇒ 不允许「部分完成算完成」")
    for section, keys in (("proofRules", PROOF_RULE_KEYS), ("nextRules", NEXT_RULE_KEYS)):
        absent = [key for key in keys if not (data.get(section) or {}).get(key)]
        if absent:
            raise ValueError(f"{GOALPLAN_FILE}.{section} 缺判据文案 {absent} ⇒ 拒绝执行没有凭据的红口")
    return data


def ledger_goal_rows(root, relative):
    """台账目标级表格 {行号: 状态符号} ＋计数行；第 4 列不是 ☑/◐/☐ 的行不认（排序表同形但无状态列）。"""
    path = Path(root) / str(relative)
    if not path.is_file():
        raise ValueError(f"台账读不动：{relative} 不存在 ⇒ 无法核对状态一致性，不判绿")
    rows, counts = {}, None
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    for line in lines:
        match = _LEDGER_ROW.match(line)
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if match and len(cells) >= 4 and cells[3][:1] in STATUS_MARKS.values():
            rows[int(match.group("row"))] = cells[3][:1]
        tally = _COUNT_LINE.search(line)
        if tally and counts is None:
            counts = {key: int(tally.group(key)) for key in ("done", "doing", "todo")}
    return rows, counts, lines


def goalproof_commit(repos, sha):
    """commit 依据只读验真：查得到才算；git 查不动一律判红，不读成通过。"""
    state = commit_exists(repos, sha)
    if state is True:
        return True, ""
    if state is None:
        return False, f"git 查不动（没装 git 或不在仓里）⇒ commit `{sha}` 不可回查，不判通过"
    return False, f"commit `{sha}` 在该仓不存在 ⇒ 依据回查失败"


def goalproof_file_line(root, token):
    path, _, number = str(token).rpartition(":")
    if not path or not number.isdigit():
        return False, f"依据 `{token}` 不是 path:行号 的写法 ⇒ 回查落点不唯一"
    target = Path(root) / path.replace("\\", "/")
    if not target.is_file():
        return False, f"依据 `{token}` 指的文件不存在 ⇒ 回查落点失效"
    total = len(target.read_text(encoding="utf-8", errors="replace").splitlines())
    line = int(number)
    if not 0 < line <= total:
        return False, f"依据 `{token}` 行号超出文件实际 {total} 行 ⇒ 指不到具体内容"
    return True, ""


def panel_goal_statuses(root, declared):
    """面板在用户目录、不随仓走（硬约束 A）：本机存在才按 panelId 逐条核状态，取 id 后第一个 status。

    相对路径按仓根解析——否则从别的 cwd 跑执法会把「面板读不到」误报成「面板不在本机」，
    一致性检查就悄悄不做了（这正是本文件要防的自欺）。
    """
    if not declared:
        return None
    path = Path(str(declared)).expanduser()
    if not path.is_absolute():
        path = Path(root) / path
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    found = {}
    for match in re.finditer(r"id:\s*'([^']+)'", text):
        status = re.search(r"status:\s*'(done|doing|todo)'", text[match.end():match.end() + 4000])
        if status:
            found[match.group(1)] = status.group(1)
    return found


def goalproof_machine(root, source, rules):
    """跑条目声明的检出面，返回 (状态, 说明)。

    状态：pass＝判满足；fail＝判未满足（标 ☑ 就是假绿）；red＝尺子取不到或没实现（也不许当通过）；
    na＝这一面对该仓不适用（只有显式声明了判据的仓才受检，业务仓不该被本仓纪律判红）。
    """
    named = rules.get("machineProofs") or {}
    if source not in named:
        return "red", (f"machineProof 源 `{source}` 未在 proofRules.machineProofs 声明"
                       " ⇒ 不猜该拿哪把尺子判这条 ☑")
    root = Path(root)
    try:
        scripts_dir = str(Path(__file__).resolve().parent)
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        import importlib
        metrics = importlib.import_module("obs.metrics")
        schema = importlib.import_module("obs.schema")
    except ImportError as exc:
        return "red", f"尺子模块导入不了：{exc}"
    if source == "objectiveData":
        try:
            status = metrics.objective_status(schema.read_events(root), metrics.load_objective_policy())
        except (ValueError, OSError) as exc:
            return "red", f"尺子跑不动：{exc}"
        return ("pass" if status["satisfied"] else "fail"), str(status["reason"])
    if source == "delivery":
        gitlog = importlib.import_module("obs.gitlog")
        try:
            pol = gitlog.delivery_policy(root)
        except ValueError as exc:
            return "red", f"交付判据读不动：{exc}"
        if pol is None:
            return "na", "该仓没有声明 delivery 节 ⇒ 交付面对它不适用（不判红也不判绿）"
        if not gitlog.is_repo(root):
            return "red", "声明了 delivery 判据但这里不是 git 仓 ⇒ 无法核对领先数，不当已通过"
        status = gitlog.delivery_status(root, pol)
        if not status["applicable"]:
            return "red", f"上游不存在：{pol['notApplicable']}"
        if status["count"] is None:
            return "red", pol["unreadable"]
        return (("pass", f"领先 {status['count']} 个提交＝已推齐（{status['upstream']}）")
                if status["count"] == 0 else
                ("fail", pol["aheadDetail"].format(count=status["count"], upstream=status["upstream"])))
    return "red", f"machineProof 源 `{source}` 已声明但执法器没实现它 ⇒ 拒绝当作已通过（宁可红在明处）"


def goalplan_audit(root, data=None):
    """逐条核对：状态枚举、与台账行/计数一致、☑ 依据可机器回查、◐/☐ 写了阻塞原因、next 指针有效。"""
    root = Path(root).resolve()
    data = data if data is not None else goalplan_policy(root)
    if data is None:
        return {"file": GOALPLAN_FILE, "applies": False, "entries": [], "errors": [], "counts": {},
                "panel": "", "policy": {}}
    goals = [entry for entry in data["goals"] if isinstance(entry, dict)]
    rules = data.get("proofRules") or {}
    pointer_rules = data.get("nextRules") or {}
    errors, entries, ids = [], [], [str(entry.get("id") or "") for entry in goals]
    notes = []
    if len(set(ids)) != len(ids) or "" in ids:
        errors.append(f"goal-plan: goals[].id 缺失或重复（{ids}）⇒ 指针与面板都无法唯一对号")
    ledger_rows, ledger_counts, ledger_lines = ledger_goal_rows(
        root, (data.get("sources") or {}).get("ledger", ""))
    real = {"done": 0, "doing": 0, "todo": 0}
    repos = git_repos(root)
    for entry in goals:
        absent = [key for key in GOAL_ENTRY_KEYS if entry.get(key) in (None, "")]
        if absent:
            errors.append(f"goal-plan: `{entry.get('id')}` 缺必需字段 {absent}"
                          " ⇒ 目标级条目不许把空值当已填（硬判据缺失就没法判 ☑）")
        mark = STATUS_MARKS.get(str(entry.get("status")))
        if mark is None:
            errors.append(f"goal-plan: `{entry.get('id')}` 的 status `{entry.get('status')}` 不在三态枚举内"
                          " ⇒ 不允许「部分完成算完成」")
            continue
        real[str(entry.get("status"))] += 1
        basis = entry.get("basis") or {}
        commits = [str(sha) for sha in (basis.get("commits") or []) if str(sha).strip()]
        files = [str(item) for item in (basis.get("files") or []) if str(item).strip()]
        problems, verified = [], 0
        for sha in commits:
            ok, why = goalproof_commit(repos, sha)
            verified += 1 if ok else 0
            problems += [why] if why else []
        for token in files:
            ok, why = goalproof_file_line(root, token)
            verified += 1 if ok else 0
            problems += [why] if why else []
        if mark == "☑" and not (commits or files):
            errors.append(f"goal-plan: `{entry.get('id')}` 标 ☑(done) 却没挂可回查依据（commit 或 path:行号都没有）"
                          f" ⇒ {rules.get('naIsNotProof', '')}")
        elif mark == "☑" and verified == 0:
            errors.append(f"goal-plan: `{entry.get('id')}` 标 ☑(done) 但依据全部回查失败：{'；'.join(problems)}"
                          f" ⇒ {rules.get('doneNeeds', '')}")
        elif problems:
            errors.append(f"goal-plan: `{entry.get('id')}` 的依据有 {len(problems)} 条回查失败"
                          f"（没标 ☑ 也如实报，别攒到收口才炸）：{'；'.join(problems)}")
        declared = str(entry.get("machineProof") or "").strip()
        if declared and mark == "☑":
            # 尺子只在「要标 ☑」时跑：◐ 的现值由看板自己报，这一条只防假绿、不催进度
            state, why = goalproof_machine(root, declared, rules)
            if state == "fail":
                errors.append(f"goal-plan: `{entry.get('id')}` 标 ☑(done) 而检出面判未满足：{why}"
                              f" ⇒ {rules.get('machineProofRule', '')}")
            elif state == "red":
                errors.append(f"goal-plan: `{entry.get('id')}` 声明了 machineProof `{declared}` 但尺子没跑成：{why}"
                              f" ⇒ {rules.get('machineProofRule', '')}")
            elif state == "na":
                notes.append(f"`{entry.get('id')}` 的 machineProof `{declared}`：{why}")
        if mark in ("◐", "☐") and not str(entry.get("blockedBy") or "").strip():
            errors.append(f"goal-plan: `{entry.get('id')}` 停在 {entry.get('status')} 却没写 blockedBy"
                          " ⇒ 没写原因的「进行中」等于没人认领")
        row = entry.get("ledgerRow")
        if row not in ledger_rows:
            errors.append(f"goal-plan: `{entry.get('id')}` 的 ledgerRow {row} 在台账里没有对应行 ⇒ 两处对不上号")
        elif ledger_rows[row] != mark:
            errors.append(f"goal-plan: `{entry.get('id')}` 状态 {entry.get('status')}（{mark}）"
                          f"与台账第 {row} 行的 `{ledger_rows[row]}` 不一致 ⇒ 历史快照当承诺的同族漂移")
        entries.append({"id": str(entry.get("id")), "status": str(entry.get("status")), "mark": mark,
                        "verified": verified, "problems": problems})
    if len(goals) != len(ledger_rows):
        errors.append(f"goal-plan: 条目 {len(goals)} 条 ≠ 台账目标级表格 {len(ledger_rows)} 行 ⇒ 有一处漏登记")
    if ledger_counts is None:
        errors.append("goal-plan: 台账里找不到「计数」行 ⇒ 没有可对账的汇总数，不判绿")
    elif ledger_counts != real:
        errors.append(f"goal-plan: 台账「计数」行 {ledger_counts} ≠ 逐条实算 {real}"
                      " ⇒ 计数行是抄的、行是源，抄错了就按行改计数")
    cell, task = str((data.get("next") or {}).get("cell") or "").strip(), \
        str((data.get("next") or {}).get("task") or "").strip()
    if not cell or not task:
        errors.append(f"goal-plan: next 指针缺失或为空（cell `{cell or 'N/A'}`／task `{task or 'N/A'}`）"
                      f" ⇒ {pointer_rules.get('required', '')}")
    elif cell not in ids:
        errors.append(f"goal-plan: next.cell `{cell}` 不是 goals[].id 之一 ⇒ {pointer_rules.get('cellMustExist', '')}")
    else:
        aimed = next((entry for entry in goals if str(entry.get("id")) == cell), {})
        if aimed.get("status") == "done":
            errors.append(f"goal-plan: next.cell `{cell}` 指向已 done 的条目 ⇒ {pointer_rules.get('doneCellIsRed', '')}")
    if task and not any(task in line for line in ledger_lines):
        errors.append(f"goal-plan: 台账「下一格」没逐字抄 next.task 原文（`{task[:40]}…`） ⇒ "
                      f"{pointer_rules.get('ledgerMustQuoteTask', '')}")
    panel_status = panel_goal_statuses(root, (data.get("sources") or {}).get("panel", ""))
    note = ""
    if panel_status is None:
        note = "面板不在本机 ⇒ 未核状态一致性（不判红也不判绿）"
    else:
        for entry in goals:
            key = str(entry.get("panelId") or "")
            if key not in panel_status:
                errors.append(f"goal-plan: `{entry.get('id')}` 的 panelId `{key}` 在面板里找不到 ⇒ 两处对不上号")
            elif panel_status[key] != entry.get("status"):
                errors.append(f"goal-plan: 面板 `{key}` 状态 {panel_status[key]} ≠ goal-plan {entry.get('status')}"
                              " ⇒ 面板与台账必须同批改（两处漂移已经骗过两轮）")
    return {"file": GOALPLAN_FILE, "applies": True, "entries": entries, "errors": errors,
            "machineNotes": notes,
            "counts": {**real, "goals": len(goals), "ledgerRows": len(ledger_rows),
                       "verified": sum(item["verified"] for item in entries)},
            "panel": note, "policy": data}


def check_goalplan(root):
    try:
        return goalplan_audit(root)["errors"]
    except (ValueError, OSError) as exc:
        return [f"goal-plan: invalid document: {exc}"]


def render_goalplan(result) -> str:
    counts, entries = result["counts"], result["entries"]
    lines = [f"# 目标台账执法（{result['file']}）", ""]
    if not result["applies"]:
        lines.append(f"- 该项目没有 {GOALPLAN_FILE} ⇒ 本执法不适用（不是通过，是没有长期目标台账）")
        return "\n".join(lines) + "\n"
    pointer = result["policy"].get("next") or {}
    lines += [f"- 条目 **{counts['goals']}** 条｜台账行 {counts['ledgerRows']} 行"
              f"｜☑ {counts['done']}｜◐ {counts['doing']}｜☐ {counts['todo']}"
              f"｜依据回查通过 {counts['verified']} 处",
              f"- 面板核对：{result['panel'] or '已按 panelId 逐条比对'}",
              f"- 检出面（machineProof）：{'；'.join(result.get('machineNotes') or []) or '声明了尺子的 ☑ 条目都已真跑并判满足'}",
              f"- 下一格：`{pointer.get('cell', 'N/A')}` —— {pointer.get('task', 'N/A')}", "",
              "| id | 状态 | 依据回查 | 备注 |", "|---|---|---|---|"]
    for entry in entries:
        lines.append(f"| `{entry['id']}` | {entry['status']}（{entry['mark']}） | {entry['verified']} 处 "
                     f"| {'；'.join(entry['problems']) or '—'} |")
    if result["errors"]:
        lines += ["", "## 红", *[f"- {error}" for error in result["errors"]]]
    lines += ["", "复算：`./.venv/Scripts/python.exe scripts/validate_core.py goalplan --project-root .`"]
    return "\n".join(lines) + "\n"


# ── 埋点主通道执法（回流 issue/Skill-Optimizer/2026-09-04/01）：各 skill 正文必须有自查上报的承接节。
# 该条现象是「埋点规范只是文档，12 个专业 skill 的 SKILL.md 里没有埋点节 ⇒ 监听主通道空转」，
# 今天这条义务的落地形态是 `## 问题记录与恢复（执行必需）` 承接节（45/45 active skill 已带）。
# 口径此前只活在 scripts/tests/test_problem_recording.py 里（单测能红，评测层没有判据入口），
# 现在提到校验器：同一份判据只写一次，单测与评测集都调它，不另造第二套。
RECORDING_HEADING = "## 问题记录与恢复（执行必需）"
RECORDING_OBLIGATIONS = ("下一安全节点", "根因未明", "恢复/交付前", "唯一索引")
RECORDING_DEFAULT_POLICY = "shared/problem-recording.md"
RECORDING_POINTER = re.compile(r"`([^`]*\.md)`")


def recording_section(text):
    """取承接节正文：声明标题到下一个二级标题之间；没有标题返回 None（空串会被读成「有节但没内容」）。"""
    if RECORDING_HEADING not in text:
        return None
    return text.split(RECORDING_HEADING, 1)[1].split("\n## ", 1)[0]


def check_recording(root):
    """每个 status=active 的 skill：承接节存在＋四个义务词逐字在场＋只指一个规范文件且解析得到。

    legacy／非 active 条目不罚（判据宁窄勿宽）；项目没有 skill-registry.yaml ⇒ 不适用，返回空。
    """
    registry = Path(root) / "governance/skill-registry.yaml"
    if not registry.is_file():
        return []
    errors = []
    for skill in items(load_yaml(registry).get("skills")):
        if skill.get("status") != "active":
            continue
        skill_id = str(skill.get("id") or skill.get("path") or "?")
        relative = str(skill.get("path") or "").replace("\\", "/")
        directory = Path(root) / relative
        entry = directory / "SKILL.md"
        if not entry.is_file():
            add(errors, f"skill {skill_id} has no SKILL.md at {relative}/SKILL.md")
            continue
        section = recording_section(entry.read_text(encoding="utf-8", errors="replace"))
        if section is None:
            add(errors, f"skill {skill_id} SKILL.md missing recording section: {RECORDING_HEADING}")
            continue
        for word in RECORDING_OBLIGATIONS:
            if word not in section:
                add(errors, f"skill {skill_id} recording section missing obligation keyword: {word}")
        refs = RECORDING_POINTER.findall(section)
        if len(refs) != 1:
            add(errors, f"skill {skill_id} recording section must declare exactly one policy pointer, "
                        f"found {len(refs)}")
            continue
        declared = skill.get("recordingPolicy")
        policy = Path(root) / str(declared or RECORDING_DEFAULT_POLICY)
        if not policy.is_file():
            add(errors, f"skill {skill_id} recording policy file does not exist: {policy.name}")
            continue
        if (directory / refs[0]).resolve() != policy.resolve():
            add(errors, f"skill {skill_id} recording pointer `{refs[0]}` does not resolve to the declared "
                        f"policy {str(declared or RECORDING_DEFAULT_POLICY)}")
            continue
        if declared and not policy.resolve().is_relative_to(directory.resolve()):
            add(errors, f"skill {skill_id} recordingPolicy must live inside the skill dir for portable "
                        f"packages: {policy.name}")
    return errors


CROSSREFS_SCRIPT = "scripts/check-installed-refs.py"


def check_crossrefs(root):
    """跨 skill 引用的两视图可达性：判据在 `shared/skill-contract.md` §1.4，实现只有一份。

    本函数只是适配器——按路径加载 `scripts/check-installed-refs.py` 并取它的 findings()，
    不在这里复写第二套路径解析/视图模拟规则（复写就会出现「单测绿、ps1 门禁红」那类分裂口径）。
    尺子取随仓发布的那一份：被测项目（评测夹具）只带 governance/，不带 scripts/，
    要求「被测目录里有这把尺子」会让所有红用例静默变绿——本仓真就这么错过一次。
    脚本或 registry 取不到 ⇒ 该项目不适用本检查，返回空；「量具缺失」由调用方如实标注，不读成通过。
    """
    script = Path(root) / CROSSREFS_SCRIPT
    if not script.is_file():
        script = Path(__file__).resolve().parents[1] / CROSSREFS_SCRIPT
    if not script.is_file() or not (Path(root) / "governance/skill-registry.yaml").is_file():
        return []
    import importlib.util
    spec = importlib.util.spec_from_file_location("check_installed_refs_adapter", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.findings(module.audit(str(Path(root).resolve())))


def check_system(root, skip_fixtures=False, skip_knowledge=False, strict=False):
    errors=[]
    for p in (".spec/manifest.yaml",".spec/traceability.yaml",".spec/workflow.yaml"):
        if not file_exists(root/p): add(errors,f"root self-spec is required: {p}")
    checks=[("registry",lambda:check_registry(root)),("skill-contract",lambda:check_skill_contract(root,True)),("graph",lambda:check_graph(root)),("transition",lambda:check_transitions(root)),("artifact",lambda:check_artifact(root)),("trace",lambda:check_trace(root)),("refs",lambda:check_refs(root)),("gate",lambda:check_gate(root)),("task",lambda:check_task(root)),("evolution",lambda:check_evolution(root)),("goalplan",lambda:check_goalplan(root)),("recording",lambda:check_recording(root)),("crossrefs",lambda:check_crossrefs(root))]
    if not skip_knowledge:
        knowledge_errors, warnings = check_knowledge(root, strict)
        errors.extend(f"knowledge: {e}" for e in knowledge_errors)
        for warning in warnings:
            print("WARNING: " + warning, file=sys.stderr)
    seen_messages = set()
    for name, fn in checks:
        try:
            for error in fn():
                # gate and artifact both enforce digests; a doubled line buries the real findings
                if error in seen_messages:
                    continue
                seen_messages.add(error)
                errors.append(f"{name}: {error}")
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
    if hasattr(sys.stdout, "reconfigure"):
        # Windows 控制台默认 GBK，中文判据会被打成乱码，读报告的人只能猜
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser()
    commands = {"registry": check_registry, "artifact": check_artifact, "trace": check_trace,
                "refs": check_refs, "gate": check_gate, "transition": check_transitions,
                "graph": check_graph, "task": check_task, "recording": check_recording,
                "crossrefs": check_crossrefs}
    parser.add_argument("command", choices=[*commands, "skill-contract", "knowledge", "system", "drift",
                                            "evolution", "goalplan"])
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--include-legacy", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--skip-fixtures", action="store_true")
    parser.add_argument("--skip-knowledge", action="store_true")
    parser.add_argument("--ledger", help="只覆盖台账路径；判据仍从 governance/obs-registry.yaml 读")
    args = parser.parse_args(argv)
    root = Path(args.project_root).resolve()
    try:
        if args.command in commands:
            errors = commands[args.command](root)
        elif args.command == "drift":
            rows, structural = attestation_drift(root)
            for error in structural:
                print(error, file=sys.stderr)
            print("| subject | status | 最新绑定证据 | 绑定时间 | 磁盘 | 台账 head | 已被取代的旧绑定 |")
            print("| --- | --- | --- | --- | --- | --- | --- |")
            for row in rows:
                print(f"| {row['subject']} | {row['status']} | {row['evidence']} | {row['attestedAt']} "
                      f"| {row['actual'][:12]}… | {row['headState']} | {row['supersededBindings']} |")
            print(f"待重签 {len(rows)} 条 ｜ 台账结构错误 {len(structural)} 条"
                  f" ｜ 重签需人工批准（decisionRefs），本命令不改写台账")
            return 1 if (rows or structural) else 0
        elif args.command == "evolution":
            result = evolution_audit(root, args.ledger)
            print(render_evolution(result))
            for error in result["errors"]:
                print(error, file=sys.stderr)
            counts = result["counts"]
            tally = (f"条目 {counts['entries']} 条｜指针验真 {counts['pointersVerified']} 条"
                     f"｜红 {counts['red']} 处")
            if not result["errors"]:
                print("evolution validation passed"
                      + (f"（空集通过：{tally} ⇒ 没有条目可判，不等于达标）" if not counts["entries"]
                         else f"（{tally}）"))
                return 0
            print(f"evolution validation failed: {len(result['errors'])} error(s)（{tally}）")
            return 1
        elif args.command == "goalplan":
            result = goalplan_audit(root)
            print(render_goalplan(result))
            for error in result["errors"]:
                print(error, file=sys.stderr)
            if not result["applies"]:
                print(f"goalplan not applicable: {GOALPLAN_FILE} 不存在（不是通过，是没有长期目标台账）")
                return 0
            tally = (f"条目 {result['counts']['goals']} 条｜☑ {result['counts']['done']}｜◐ {result['counts']['doing']}"
                     f"｜依据回查通过 {result['counts']['verified']} 处")
            if result["errors"]:
                print(f"goalplan validation failed: {len(result['errors'])} error(s)（{tally}）")
                return 1
            print(f"goalplan validation passed（{tally}）")
            return 0
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

