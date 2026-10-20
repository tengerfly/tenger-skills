import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tsr
from obs import selfcheck, score


class SelfCheckTests(unittest.TestCase):
    """The harness must fail when it stops being able to detect, not report a clean bill."""

    def test_every_probe_fires(self):
        with redirect_stdout(io.StringIO()) as out:
            report = selfcheck.run()
        self.assertEqual(report["missed"], [], out.getvalue())
        self.assertEqual(report["fired"], len(selfcheck.PROBES))

    def test_a_clean_project_produces_no_findings(self):
        # without this control a probe could "detect" breakage that is always present
        tmp, root = selfcheck.project()
        self.addCleanup(tmp.cleanup)
        self.assertEqual(selfcheck.core.check_artifact(root), [])
        self.assertEqual(score.d1_contract(root)["value"], 100.0)
        common = ["--project-root", str(root), "--execution-id", "E", "--node", "prd-design", "--skill", "prd-design"]
        tsr.main(common + ["node-start"])
        tsr.main(common + ["node-end", "--gate", "PASS", "--allow-downstream", "true",
                           "--artifact", ".spec/prd/overview.md"])
        self.assertEqual(tsr.verify(root), [])


if __name__ == "__main__":
    unittest.main()
