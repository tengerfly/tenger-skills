import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import yaml
from obs import score

ARTIFACT = {"artifactId": "PRD-V1", "type": "prd", "path": ".spec/prd/overview.md", "lifecycle": "CREATE",
            "owner": "pm", "status": "REVIEW", "producedBy": "prd-design", "producedAt": "2026-10-20T00:00:00+08:00",
            "sourceRefs": [], "evidenceRefs": [], "decisionRefs": []}


class ScoreTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def ledger(self, artifacts):
        (self.root / ".spec").mkdir(exist_ok=True)
        (self.root / ".spec/manifest.yaml").write_text(
            yaml.safe_dump({"projectId": "synthetic", "artifacts": artifacts}, allow_unicode=True), encoding="utf-8")

    def write(self, relative, text):
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        return target

    def test_d1_judges_only_path_matched_documents(self):
        self.write(".spec/prd/overview.md", "# 标题\n## 1. 元数据与变更记录\n## 2. 背景痛点\n## 3. 用户画像与 JTBD\n## 7. 模块清单与范围边界\n")
        self.write(".spec/prd/M01.md", "# 模块一\n## 功能点\n")
        self.ledger([ARTIFACT, dict(ARTIFACT, artifactId="PRD-M01", path=".spec/prd/M01.md")])
        result = score.d1_contract(self.root)
        self.assertEqual(result["value"], 100.0)
        self.assertIn("1/1", result["detail"])

    def test_d1_penalises_a_document_missing_its_headings(self):
        self.write(".spec/prd/overview.md", "# 随便写了点东西\n没有章节结构\n")
        self.ledger([ARTIFACT])
        result = score.d1_contract(self.root)
        self.assertEqual(result["value"], 0.0)
        self.assertIn("缺章节关键词", result["failures"][0])

    def test_d1_without_ledger_is_na_not_zero(self):
        self.assertEqual(score.d1_contract(self.root)["value"], None)

    def test_broken_traceability_costs_points_instead_of_disappearing(self):
        self.ledger([ARTIFACT])
        self.write(".spec/traceability.yaml", "traceability:\n  requirements: []\n")
        result = score.d2_traceability(self.root)
        self.assertEqual(result["value"], 0.0)
        self.assertIn("读不到 links", result["detail"])

    def test_resolvable_links_score(self):
        self.ledger([ARTIFACT])
        self.write(".spec/traceability.yaml", yaml.safe_dump(
            {"projectId": "synthetic", "links": [
                {"linkId": "L1", "from": "REQ-M01-001", "to": "PRD-V1", "relation": "implements", "lifecycle": "CREATE"},
                {"linkId": "L2", "from": "GHOST", "to": "NOWHERE", "relation": "implements", "lifecycle": "CREATE"}]},
            allow_unicode=True))
        result = score.d2_traceability(self.root)
        self.assertEqual(result["value"], 50.0)

    def test_red_line_forces_total_to_zero_not_none(self):
        self.write(".spec/prd/overview.md", "# 无章节\n")
        self.ledger([dict(ARTIFACT, contentDigest="0" * 64)])
        self.write(".spec/prd/M01.md", "# placeholder\n")
        result = score.score_project(self.root)
        self.assertTrue(result["redLines"])
        self.assertEqual(result["total"], 0.0)

    def test_unmeasured_dimensions_are_dropped_from_the_denominator(self):
        result = score.score_project(self.root)
        self.assertEqual(result["total"], None)
        self.assertEqual(result["weightUsed"], 0)
        self.assertIn("D5", result["dimensions"])

    def test_anchor_records_what_a_score_is_comparable_to(self):
        result = score.score_project(self.root)
        self.assertEqual(set(result["anchor"]), {"scoringVersion", "skillRevision"})


if __name__ == "__main__":
    unittest.main()
