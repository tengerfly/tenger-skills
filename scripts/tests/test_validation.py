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
        self.write_yaml(".spec/manifest.yaml", {"projectId": "synthetic", "artifacts": [self.code_artifact, self.evidence, self.decision_artifact]})
        self.write_yaml(".spec/authorization.yaml", self.policy)
        self.write_yaml(".spec/decisions/DEC-1.yaml", self.decision)
        return preflight.plan(self.root, self.task)

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


if __name__ == "__main__":
    unittest.main()
