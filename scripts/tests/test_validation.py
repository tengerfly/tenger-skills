import copy
import hashlib
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import validate_core as core
import task_preflight as preflight

ROOT = Path(__file__).resolve().parents[2]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def grant(action="execute-task"):
    now = datetime.now(timezone.utc)
    return {"decisionId": "DEC-1", "status": "APPROVED", "decision": "approve",
            "projectId": "synthetic", "executionId": "EXEC-1", "owner": "reviewer",
            "approvedBy": "reviewer", "approvedAt": (now - timedelta(hours=1)).isoformat(),
            "expiresAt": (now + timedelta(days=1)).isoformat(),
            "scope": {"actions": [action], "actor": "workflow", "transitionIds": ["TR-039"],
                      "allowedPaths": [".spec"], "exceptionId": "EX-1"}}


def passing_gate():
    return {"gate": "PASS", "allowDownstream": True, "reason": "synthetic verification",
            "nextAction": "test", "evidenceRefs": ["EVID-1"], "decisionRefs": []}


class ValidationTests(unittest.TestCase):
    def test_duplicate_yaml_keys_are_rejected(self):
        with self.assertRaises(core.DuplicateKeyError):
            core.yaml.load("a: 1\na: 2\n", Loader=core.StrictLoader)

    def test_sourceRefs_binding_rejects_superseded_baseline(self):
        def entry(aid, status, sources=(), supersedes=None):
            item = {"artifactId": aid, "type": "prd", "status": status, "sourceRefs": list(sources),
                    "evidenceRefs": [], "decisionRefs": [aid + "-DEC"]}
            if supersedes:
                item["supersedes"] = supersedes
            return item

        by_id = {
            "PRD-OLD": entry("PRD-OLD", "SUPERSEDED"),
            "DESIGN-1": entry("DESIGN-1", "APPROVED", ["PRD-OLD"]),
            "DESIGN-2": entry("DESIGN-2", "SUPERSEDED", ["PRD-OLD"]),
            "REPL-1": entry("REPL-1", "APPROVED", ["PRD-OLD"], supersedes="PRD-OLD"),
        }
        with patch.object(core, "artifact_context", return_value=({"artifacts": []}, by_id, [])):
            errors = core.check_artifact(Path("."))
        # DESIGN-1 is current work bound to a retired baseline; DESIGN-2 is itself retired and
        # REPL-1 declares supersedes, so neither may be reported as drift.
        self.assertEqual({e.split(" ")[0] for e in errors if "superseded baseline" in e}, {"DESIGN-1"})

    def test_pass_rejects_p0_and_p1_but_allows_p2(self):
        evidence = {"EVID-1": {"type": "validation-report", "status": "REVIEW"}}
        for severity in ("P0", "P1", "P2"):
            with self.subTest(severity=severity):
                record = passing_gate()
                record["unresolvedRisks"] = [{"severity": severity}]
                self.assertEqual(bool(core.gate_check(record, "fixture", evidence)), severity != "P2")

    def test_boolean_string_and_blocked_downstream_are_rejected(self):
        for value in (True, "false"):
            errors = core.gate_check({"gate": "BLOCKED", "allowDownstream": value}, "fixture", {})
            self.assertTrue(any("allowDownstream" in e for e in errors))

    def test_conditional_requires_live_scoped_authorization(self):
        decision = grant("accept-risk")
        context = {"projectId": "synthetic", "executionId": "EXEC-1",
                   "approvers": [{"id": "reviewer", "actions": ["accept-risk"]}]}
        evidence = {"EVID-1": {"type": "validation-report", "status": "REVIEW"},
                    "DEC-1": {"type": "decision", "status": "APPROVED"}}
        record = passing_gate()
        record.update(gate="CONDITIONAL", exceptionId="EX-1", risk="P1 synthetic",
                      owner="reviewer", dueAt=decision["expiresAt"], remediation="repair",
                      approvalRef="DEC-1", decisionRefs=["DEC-1"])
        self.assertEqual(core.gate_check(record, "fixture", evidence, {"DEC-1": decision}, context), [])
        for mutation in ("absent", "expired", "wrong-scope", "untrusted", "P0", "wrong-execution"):
            with self.subTest(mutation=mutation):
                d, c, r = copy.deepcopy(decision), copy.deepcopy(context), copy.deepcopy(record)
                if mutation == "absent": d["status"] = "DRAFT"
                if mutation == "expired": d["expiresAt"] = d["approvedAt"]
                if mutation == "wrong-scope": d["scope"]["exceptionId"] = "OTHER"
                if mutation == "untrusted": c["approvers"] = []
                if mutation == "P0": r["unresolvedRisks"] = [{"severity": "P0"}]
                if mutation == "wrong-execution": d["executionId"] = "OTHER"
                self.assertTrue(core.gate_check(r, "fixture", evidence, {"DEC-1": d}, c))

    def test_reference_checker_checks_existing_endpoints_evidence(self):
        trace = core.load_yaml(ROOT / ".spec/traceability.yaml")
        _, by_id, _ = core.artifact_context(ROOT)
        trace["links"][0]["evidenceRefs"] = ["MISSING-EVIDENCE"]
        self.assertTrue(any("MISSING-EVIDENCE" in e for e in core.check_link_references(trace, by_id)))

    def test_current_graph_has_completion_and_review_test_dominators(self):
        self.assertEqual(core.check_graph(ROOT), [])

    def mutated_graph(self, mutate):
        original = core.load_yaml
        states = original(ROOT / "governance/state-registry.yaml")
        mutate(states)
        def load(path):
            return states if path.name == "state-registry.yaml" else original(path)
        with patch.object(core, "load_yaml", side_effect=load):
            return core.check_graph(ROOT)

    def test_graph_rejects_missing_product_baseline_on_every_prd_entry(self):
        states = core.load_yaml(ROOT / "governance/state-registry.yaml")
        ids = [t["id"] for t in states["transitions"] if t["to"] in core.PRD_BASELINE_STATES]
        self.assertTrue(ids)
        for tid in ids:
            with self.subTest(transition=tid):
                def mutate(data):
                    edge = next(t for t in data["transitions"] if t["id"] == tid)
                    edge["requiredArtifacts"].remove("feature-decision")
                self.assertTrue(any(tid in e and "bypasses" in e for e in self.mutated_graph(mutate)))

    def test_graph_rejects_test_bypass_even_with_required_evidence_fields(self):
        def mutate(states):
            edge = copy.deepcopy(next(t for t in states["transitions"] if t["to"] == "RELEASE_PLANNING_IN_PROGRESS"))
            edge.update(id="TR-BYPASS", **{"from": "INTAKE_REQUESTED"})
            states["transitions"].append(edge)
        self.assertTrue(any("bypass TEST_PASSED" in e for e in self.mutated_graph(mutate)))

    def test_graph_rejects_unknown_actor(self):
        errors = self.mutated_graph(lambda s: s["transitions"][0].update(actor="unregistered"))
        self.assertTrue(any("unknown actor" in e for e in errors))

    def test_graph_rejects_wrong_state_lifecycle(self):
        errors = self.mutated_graph(lambda s: s["states"][0].update(lifecycle=[]))
        self.assertTrue(any("outside state scope" in e for e in errors))

    def test_missing_self_spec_fails(self):
        with patch.object(core, "file_exists", return_value=False):
            with redirect_stderr(io.StringIO()):
                errors = core.check_system(ROOT, skip_fixtures=True, skip_knowledge=True)
        self.assertTrue(any("root self-spec is required" in e for e in errors))

    def test_knowledge_missing_is_visible_and_strict_fails(self):
        with patch.dict(core.os.environ, {}, clear=True):
            errors, warnings = core.check_knowledge(ROOT)
            self.assertFalse(errors)
            self.assertTrue(warnings)
            self.assertTrue(core.check_knowledge(ROOT, strict=True)[0])

    def test_malformed_document_cli_fails_without_traceback(self):
        with patch.object(core, "load_yaml", return_value=[]):
            with redirect_stderr(io.StringIO()), redirect_stdout(io.StringIO()):
                self.assertEqual(core.main(["gate", "--project-root", str(ROOT)]), 1)

    def test_legacy_fixture_checks_required_fields_not_just_nonempty(self):
        fixture = ROOT / "scripts/fixtures/create-web-app"
        original = core.load_yaml
        manifest = original(fixture / ".spec/manifest.yaml")
        del manifest["artifacts"][0]["owner"]
        with patch.object(core, "load_yaml", side_effect=lambda p: manifest if p.name == "manifest.yaml" else original(p)):
            self.assertTrue(any("owner" in e for e in core.check_fixture(fixture, "manifest")))


class TaskPreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix=".validation-test-", dir=ROOT)
        self.root = Path(self.temp.name).resolve()
        # Cleanup is confined to this test's freshly created directory inside the workspace.
        assert self.root.is_relative_to(ROOT.resolve()) and self.root.name.startswith(".validation-test-")
        self.addCleanup(self.temp.cleanup)
        self.product_artifacts = []
        self.decision = grant()
        self.workflow = dict(passing_gate(), projectId="synthetic", executionId="EXEC-1",
                             workflowId="WF-1", lifecycle="CHANGE", state="CODE_REVIEW_PASSED", revision="r1")
        self.code = b"synthetic source, never deployed"
        self.report = b"synthetic review PASS, not human approval"
        self.write_bytes("src/code.txt", self.code)
        self.write_bytes(".spec/review.md", self.report)
        def artifact(aid, typ, path):
            return {"artifactId": aid, "type": typ, "path": path, "lifecycle": "CHANGE", "owner": "reviewer",
                    "status": "REVIEW", "producedBy": "workflow", "producedAt": self.decision["approvedAt"]}
        self.code_artifact = artifact("CODE-1", "code-change", "src/code.txt")
        self.evidence = artifact("EVID-1", "validation-report", ".spec/review.md")
        self.evidence.update(executionId="EXEC-1", revision="r1", result="PASS", role="code-review",
                             subjectRefs=["CODE-1"], subjectDigests={"CODE-1": digest(self.code)},
                             contentDigest=digest(self.report))
        self.decision_artifact = artifact("DEC-1", "decision", ".spec/decisions/DEC-1.yaml")
        self.decision_artifact["status"] = "APPROVED"
        self.task = {"taskId": "TASK-1", "projectId": "synthetic", "executionId": "EXEC-1", "revision": "r1",
                     "lifecycle": "CHANGE", "currentState": "CODE_REVIEW_PASSED", "targetState": "TEST_IN_PROGRESS",
                     "transitionId": "TR-039", "requestedAction": "start-tests", "requiredSkill": "workflow",
                     "scope": {"allowedPaths": [".spec/tests"], "forbiddenPaths": [".spec/private"]},
                     "inputRefs": ["CODE-1"], "artifactRefs": [], "evidenceRefs": ["EVID-1"], "decisionRefs": ["DEC-1"],
                     "authorization": {"actor": "workflow", "approvalRef": "DEC-1", "grantedBy": "reviewer",
                                       "grantedAt": self.decision["approvedAt"]},
                     "expectedOutput": {"artifactType": "test-report", "path": ".spec/tests/result.md",
                                        "acceptanceChecks": ["record test outcome"]},
                     "gate": dict(passing_gate(), outcome="PASS"), "nextAction": "run tests"}
        self.task["gate"].pop("gate")
        self.policy = {"projectId": "synthetic", "approvers": [{"id": "reviewer", "actions": ["execute-task", "clear-block", "deploy"]}]}

    def write_bytes(self, name, content):
        target = self.root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)

    def write_yaml(self, name, obj):
        self.write_bytes(name, core.yaml.safe_dump(obj, sort_keys=False).encode())

    def run_plan(self):
        self.write_yaml(".spec/workflow.yaml", self.workflow)
        self.write_yaml(".spec/manifest.yaml", {"projectId": "synthetic", "artifacts": [self.code_artifact, self.evidence, self.decision_artifact] + self.product_artifacts})
        self.write_yaml(".spec/authorization.yaml", self.policy)
        self.write_yaml(".spec/decisions/DEC-1.yaml", self.decision)
        return preflight.plan(self.root, self.task)

    def prepare_product_baseline(self):
        self.workflow["state"] = "INTAKE_READY"
        self.task.update(currentState="INTAKE_READY", targetState="PRD_IN_PROGRESS", transitionId="TR-011")
        self.task["expectedOutput"].update(artifactType="prd", path=".spec/tests/prd.md")
        self.decision["scope"]["transitionIds"] = ["TR-011"]
        self.decision["scope"]["actions"].append("approve-artifact")
        self.policy["approvers"][0]["actions"].append("approve-artifact")
        subjects, digests = [], {}
        for typ in sorted(core.PRODUCT_BASELINE_TYPES):
            aid = "ART-" + typ
            content = ("synthetic approved baseline: " + typ).encode()
            location = f".spec/{typ}.md"
            self.write_bytes(location, content)
            digests[aid] = digest(content)
            self.product_artifacts.append({
                "artifactId": aid, "type": typ, "path": location, "lifecycle": "CHANGE",
                "owner": "reviewer", "status": "APPROVED", "producedBy": typ,
                "producedAt": self.decision["approvedAt"], "sourceRefs": [], "evidenceRefs": ["EVID-1"],
                "decisionRefs": ["DEC-1"],
                # an APPROVED ledger must be falsifiable against the bytes it approves
                "contentDigest": digests[aid],
            })
            subjects.append(aid)
        self.decision["scope"]["artifactIds"] = subjects.copy()
        self.task["inputRefs"] = subjects
        self.evidence.update(subjectRefs=subjects.copy(), subjectDigests=digests)

    def test_prd_can_reuse_approved_product_baseline(self):
        self.prepare_product_baseline()
        plan, errors = self.run_plan()
        self.assertEqual(errors, [])
        self.assertEqual(plan["to"], "PRD_IN_PROGRESS")
        self.assertFalse(plan["stateChanged"])

    def test_prd_rejects_reviewed_but_unapproved_baseline(self):
        self.prepare_product_baseline()
        for item in self.product_artifacts:
            with self.subTest(type=item["type"]):
                item["status"] = "REVIEW"
                plan, errors = self.run_plan()
                self.assertIsNone(plan)
                self.assertTrue(any("PRD product baseline must be APPROVED" in e for e in errors))
                item["status"] = "APPROVED"

    def test_prd_rejects_missing_feature_decision(self):
        self.prepare_product_baseline()
        self.task["inputRefs"].remove("ART-feature-decision")
        self.assertTrue(any("missing transition artifact types" in e and "feature-decision" in e
                            for e in self.run_plan()[1]))

    def test_prd_rejects_approval_label_without_scoped_decision(self):
        self.prepare_product_baseline()
        self.decision["scope"]["artifactIds"].remove("ART-feature-decision")
        self.assertTrue(any("approved artifact lacks valid scoped approval: ART-feature-decision" in e
                            for e in self.run_plan()[1]))

    def test_create_change_defect_positive_readiness(self):
        for lifecycle in ("CREATE", "CHANGE", "DEFECT"):
            with self.subTest(lifecycle=lifecycle):
                for obj in (self.workflow, self.task, self.code_artifact, self.evidence, self.decision_artifact):
                    obj["lifecycle"] = lifecycle
                plan, errors = self.run_plan()
                self.assertEqual(errors, [])
                self.assertFalse(plan["stateChanged"])
                self.assertFalse(plan["skillExecuted"])

    def test_ambiguous_gate_outcome_is_rejected(self):
        self.task["gate"]["gate"] = "BLOCKED"
        self.assertTrue(any("ambiguous" in e for e in self.run_plan()[1]))

    def test_mismatched_granter_is_rejected(self):
        self.task["authorization"]["grantedBy"] = "imposter"
        self.assertTrue(any("grantedBy" in e for e in self.run_plan()[1]))

    def test_deployment_requires_separate_deploy_authorization(self):
        self.workflow["state"] = "RELEASE_PLAN_READY"
        self.task.update(currentState="RELEASE_PLAN_READY", targetState="DEPLOYMENT_IN_PROGRESS", transitionId="TR-043")
        self.decision["scope"]["transitionIds"] = ["TR-043"]
        self.assertTrue(any("scope does not authorize deploy" in e for e in self.run_plan()[1]))

    def test_scalar_paths_and_acceptance_checks_are_rejected(self):
        self.task["scope"]["allowedPaths"] = ".spec"
        self.task["expectedOutput"]["acceptanceChecks"] = "looks good"
        errors = self.run_plan()[1]
        self.assertTrue(any("allowedPaths must be a list" in e for e in errors))
        self.assertTrue(any("acceptanceChecks must be a list" in e for e in errors))

    def test_wrong_execution_is_rejected(self):
        self.task["executionId"] = "OTHER"
        self.assertTrue(any("executionId" in e for e in self.run_plan()[1]))

    def test_stale_revision_is_rejected(self):
        self.evidence["revision"] = "old"
        self.assertTrue(any("revision" in e for e in self.run_plan()[1]))

    def test_changed_subject_content_is_rejected(self):
        self.write_bytes("src/code.txt", b"changed after review")
        self.assertTrue(any("subjectDigests" in e for e in self.run_plan()[1]))

    def test_changed_evidence_content_is_rejected(self):
        self.write_bytes(".spec/review.md", b"changed report")
        self.assertTrue(any("contentDigest" in e for e in self.run_plan()[1]))

    def test_wrong_evidence_role_is_rejected(self):
        self.evidence["role"] = "inspection"
        self.assertTrue(any("evidence roles" in e for e in self.run_plan()[1]))

    def test_forbidden_parent_takes_precedence(self):
        self.task["scope"]["forbiddenPaths"] = [".spec"]
        self.assertTrue(any("forbidden" in e for e in self.run_plan()[1]))

    def test_approval_cannot_grant_broader_paths(self):
        self.decision["scope"]["allowedPaths"] = ["docs"]
        self.assertTrue(any("exceeds approval" in e for e in self.run_plan()[1]))

    def test_portable_absolute_and_traversal_paths_are_rejected(self):
        for path in ("C:/secrets", "../secrets", "..\\secrets", "/etc/passwd"):
            with self.subTest(path=path):
                with self.assertRaises(ValueError): preflight.safe_path(self.root, path)

    def test_wrong_actor_and_lifecycle_are_rejected(self):
        self.task["requiredSkill"] = "auto-test"
        self.assertTrue(any("actor" in e for e in self.run_plan()[1]))
        self.task["lifecycle"] = "UNKNOWN"
        self.assertTrue(any("lifecycle" in e for e in self.run_plan()[1]))

    def test_blocked_cannot_be_cleared_by_task_pass_alone(self):
        self.workflow.update(gate="BLOCKED", allowDownstream=False, owner="reviewer",
                             requiredInput="new review", clearanceCondition="authorized clearance")
        self.assertTrue(any("clear-block" in e or "clearanceEvidenceRefs" in e for e in self.run_plan()[1]))
        self.decision["scope"]["actions"].append("clear-block")
        self.task["clearanceEvidenceRefs"] = ["EVID-1"]
        self.assertEqual(self.run_plan()[1], [])

    def test_absent_authority_fails_closed(self):
        self.policy["approvers"] = []
        self.assertTrue(any("not authorized" in e for e in self.run_plan()[1]))

    def test_lightweight_hint_cannot_bypass_formal_authority(self):
        # Profile hints are not a supported exemption from formal authorization.
        self.task["executionProfile"] = "light"
        self.policy["approvers"] = []
        plan, errors = self.run_plan()
        self.assertTrue(any("not authorized" in e for e in errors))
        self.assertIsNone(plan)

    def test_lightweight_hint_cannot_clear_existing_block(self):
        self.task["executionProfile"] = "light"
        self.workflow.update(gate="BLOCKED", allowDownstream=False, owner="reviewer",
                             requiredInput="new review", clearanceCondition="authorized clearance")
        plan, errors = self.run_plan()
        self.assertTrue(any("clear-block" in e or "clearanceEvidenceRefs" in e for e in errors))
        self.assertIsNone(plan)

    def test_cli_emits_read_only_plan_without_changing_workflow(self):
        self.assertEqual(self.run_plan()[1], [])
        self.write_yaml(".spec/task.yaml", {"task": self.task})
        before = (self.root / ".spec/workflow.yaml").read_bytes()
        output = io.StringIO()
        with redirect_stdout(output):
            result = preflight.main(["--project-root", str(self.root), "--task-file", ".spec/task.yaml"])
        self.assertEqual(result, 0)
        self.assertIn('"stateChanged": false', output.getvalue())
        self.assertEqual(before, (self.root / ".spec/workflow.yaml").read_bytes())


class ContentDigestEnforcementTests(unittest.TestCase):
    """Injection probes: a green ledger must be falsifiable against the bytes on disk."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def body(self, aid="PRD-1"):
        return self.root / ".spec" / "prd" / f"{aid}.md"

    def write_body(self, aid, data):
        target = self.body(aid)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    def artifact(self, aid="PRD-1", status="REVIEW", produced_at="2026-10-20", **extra):
        item = {"artifactId": aid, "type": "prd", "status": status, "producedAt": produced_at,
                "path": f".spec/prd/{aid}.md", "decisionRefs": [f"{aid}-DEC"]}
        item.update(extra)
        return item

    def check(self, by_id):
        with patch.object(core, "artifact_context", return_value=({"artifacts": []}, by_id, [])):
            return core.check_artifact(self.root)

    def test_tampered_body_with_stale_digest_is_detected(self):
        approved = b"# approved baseline\n"
        self.write_body("PRD-1", approved)
        item = self.artifact(status="APPROVED", contentDigest=digest(approved))
        self.write_body("PRD-1", approved + b"# sneakily rewritten without approval\n")
        errors = self.check({"PRD-1": item})
        self.assertTrue(any("contentDigest mismatch" in e for e in errors), errors)

    def test_matching_digest_adds_no_digest_error(self):
        data = b"# approved baseline\n"
        self.write_body("PRD-1", data)
        errors = self.check({"PRD-1": self.artifact(status="APPROVED", contentDigest=digest(data))})
        self.assertFalse([e for e in errors if "igest" in e], errors)

    def test_fresh_approval_must_declare_digest(self):
        self.write_body("PRD-1", b"# new baseline\n")
        errors = self.check({"PRD-1": self.artifact(status="APPROVED", produced_at="2026-10-20")})
        self.assertTrue(any("requires contentDigest" in e for e in errors), errors)

    def test_pre_cutoff_approval_is_not_rewritten_as_regression(self):
        self.write_body("PRD-1", b"# old baseline\n")
        errors = self.check({"PRD-1": self.artifact(status="APPROVED", produced_at="2026-01-05")})
        self.assertFalse([e for e in errors if "requires contentDigest" in e], errors)

    def test_subject_digest_drift_is_detected(self):
        subject = b"# subject v1\n"
        self.write_body("PRD-1", subject)
        self.write_body("TECH-1", b"# tech v1\n")
        by_id = {
            "PRD-1": self.artifact("PRD-1", status="APPROVED", contentDigest=digest(subject)),
            "TECH-1": self.artifact("TECH-1", status="APPROVED", contentDigest=digest(b"# tech v1\n"),
                                    subjectDigests={"PRD-1": digest(subject)}),
        }
        self.write_body("PRD-1", b"# subject silently reworded\n")
        errors = self.check(by_id)
        self.assertTrue(any("subjectDigests mismatch" in e for e in errors), errors)

    def test_superseded_attestation_is_not_reported_as_drift(self):
        """KB 事故复盘：153 条"漂移"里 140 条只是更早一次审查的快照被后续合法改动超越。
        subjectDigests 的定义是"当时看到的字节"，只有最新一条才是对当下的承诺。"""
        v1 = b"# subject v1\n"
        v2 = b"# subject v2 re-approved later\n"
        self.write_body("PRD-1", v2)
        self.write_body("EVID-OLD", b"# old review\n")
        self.write_body("EVID-NEW", b"# new review\n")
        by_id = {
            "PRD-1": self.artifact(status="APPROVED", contentDigest=digest(v2)),
            "EVID-OLD": self.artifact("EVID-OLD", produced_at="2026-10-11T09:00:00+08:00",
                                      subjectDigests={"PRD-1": digest(v1)}),
            "EVID-NEW": self.artifact("EVID-NEW", produced_at="2026-10-12T09:00:00+08:00",
                                      subjectDigests={"PRD-1": digest(v2)}),
        }
        errors = self.check(by_id)
        self.assertFalse([e for e in errors if "subjectDigests mismatch" in e], errors)

    def test_newest_attestation_survives_mixed_timestamp_styles(self):
        # 台账混用 "2026-10-12 09:34" 与 "2026-10-12T09:33"；纯字符串排序里空格排在 T 前面，
        # 会把更早的那条当成最新，于是合规台账被误判成漂移
        current = b"# subject now\n"
        self.write_body("PRD-1", current)
        self.write_body("EVID-A", b"# a\n")
        self.write_body("EVID-B", b"# b\n")
        by_id = {
            "PRD-1": self.artifact(status="APPROVED", contentDigest=digest(current)),
            "EVID-A": self.artifact("EVID-A", produced_at="2026-10-12 09:34:00+08:00",
                                    subjectDigests={"PRD-1": digest(current)}),
            "EVID-B": self.artifact("EVID-B", produced_at="2026-10-12T09:33:00+08:00",
                                    subjectDigests={"PRD-1": digest(b"# stale\n")}),
        }
        errors = self.check(by_id)
        self.assertFalse([e for e in errors if "subjectDigests mismatch" in e], errors)

    def test_drift_queue_lists_the_re_sign_candidates(self):
        current = b"# subject now\n"
        self.write_body("PRD-1", current)
        self.write_body("EVID-A", b"# a\n")
        by_id = {"PRD-1": self.artifact(status="APPROVED", contentDigest=digest(current)),
                 "EVID-A": self.artifact("EVID-A", subjectDigests={"PRD-1": digest(b"# was\n")})}
        with patch.object(core, "artifact_context", return_value=({"artifacts": []}, by_id, [])):
            rows, structural = core.attestation_drift(self.root)
        self.assertEqual([], structural)
        self.assertEqual(["PRD-1"], [row["subject"] for row in rows])

    def test_traversal_path_is_refused_not_hashed(self):
        outside = self.root.parent / "outside-baseline.md"
        outside.write_bytes(b"# outside\n")
        self.addCleanup(outside.unlink, missing_ok=True)
        item = self.artifact(status="APPROVED", path="../" + outside.name, contentDigest=digest(b"# outside\n"))
        errors = self.check({"PRD-1": item})
        self.assertTrue(any("without traversal" in e or "escapes project root" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
