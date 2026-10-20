"""Injection probes: prove the harness can fail before trusting it to pass.

Each probe builds a throwaway project, deliberately breaks one invariant, and asserts that
the intended checker fires. A probe that does not fire is reported as a miss — the harness
is then advertised as having limited detection power instead of quietly grading itself.
Nothing here touches a real project; every case runs in a temporary directory.
"""
from __future__ import annotations
import json, sys, tempfile
from datetime import datetime
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from obs import schema, score

import tsr
import validate_core as core

ARTIFACT = {"artifactId": "PRD-V1", "type": "prd", "path": ".spec/prd/overview.md", "lifecycle": "CREATE",
            "owner": "pm", "status": "REVIEW", "producedBy": "prd-design",
            "producedAt": "2026-10-20T00:00:00+08:00", "sourceRefs": [], "evidenceRefs": [], "decisionRefs": []}
GOOD_DOC = "# PRD 总纲\n## 1. 元数据与变更记录\n## 2. 背景痛点\n## 3. 用户画像与 JTBD\n## 7. 模块清单\n"


def project(document=GOOD_DOC, manifest=None):
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    target = root / ".spec/prd/overview.md"
    target.parent.mkdir(parents=True)
    target.write_text(document, encoding="utf-8")
    ledger = manifest if manifest is not None else [dict(ARTIFACT)]
    (root / ".spec/manifest.yaml").write_text(
        yaml.safe_dump({"projectId": "probe", "artifacts": ledger}, allow_unicode=True), encoding="utf-8")
    return tmp, root


def ledger_with_digest():
    _, probe_root = project()
    digest = core.sha256_file(probe_root / ARTIFACT["path"])
    tmp, root = project(manifest=[dict(ARTIFACT, status="APPROVED", contentDigest=digest,
                                       decisionRefs=["DEC-1"])])
    return tmp, root


def PROBE_missing_sections():
    tmp, root = project(document="# PRD 总纲\n没有必需章节\n")
    result = score.d1_contract(root)
    tmp.cleanup()
    return result["value"] == 0.0, f"D1={result['value']}"


def PROBE_illegal_gate_field():
    tmp, root = project()
    (root / ".spec/workflow.yaml").write_text(yaml.safe_dump(
        {"projectId": "probe", "lifecycle": "CREATE", "state": "PRD_IN_PROGRESS",
         "gate": "PASSED", "allowDownstream": True}), encoding="utf-8")
    errors = core.check_gate(root)
    tmp.cleanup()
    return any("invalid gate" in error for error in errors), f"{len(errors)} 条"


def PROBE_unpaired_node_end():
    tmp, root = project()
    tsr.main(["--project-root", str(root), "--execution-id", "E", "--node", "prd-design",
              "--skill", "prd-design", "node-end", "--gate", "PASS", "--allow-downstream", "true"])
    errors = tsr.verify(root)
    tmp.cleanup()
    return any("node-end without matching node-start" in error for error in errors), f"{len(errors)} 条"


def PROBE_body_edited_after_ledger():
    tmp, root = ledger_with_digest()
    (root / ARTIFACT["path"]).write_text(GOOD_DOC + "\n> 批准后被人偷偷改写\n", encoding="utf-8")
    errors = core.check_artifact(root)
    tmp.cleanup()
    return any("contentDigest mismatch" in error for error in errors), f"{len(errors)} 条"


def PROBE_digest_is_deterministic_and_clock_bound():
    tmp, root = project()
    first = core.sha256_file(root / ARTIFACT["path"])
    second = core.sha256_file(root / ARTIFACT["path"])
    tsr.main(["--project-root", str(root), "--execution-id", "E", "--node", "prd-design",
              "--skill", "prd-design", "node-start"])
    stamped = schema.read_events(root)[0]["ts"]
    drift = abs((datetime.fromisoformat(stamped) - datetime.now().astimezone()).total_seconds())
    tmp.cleanup()
    return first == second and drift < 5, f"哈希一致，ts 与机器时钟差 {drift:.2f}s"


def PROBE_unregistered_node():
    tmp, root = project()
    tsr.main(["--project-root", str(root), "--execution-id", "E", "--node", "made-up",
              "--skill", "made-up", "node-start"])
    errors = tsr.verify(root)
    tmp.cleanup()
    return any("not registered" in error for error in errors), f"{len(errors)} 条"


def PROBE_closed_upstream_cannot_pass():
    tmp, root = project()
    common = ["--project-root", str(root), "--execution-id", "E", "--node", "prd-design", "--skill", "prd-design"]
    tsr.main(common + ["node-start"])
    tsr.main(common + ["node-end", "--gate", "PASS", "--allow-downstream", "true", "--upstream", "PRD-V1:BLOCKED"])
    errors = tsr.verify(root)
    tmp.cleanup()
    return any("upstream is closed" in error for error in errors), f"{len(errors)} 条"


PROBES = [
    ("必需章节缺失 → D1 扣分", PROBE_missing_sections),
    ("Gate 字段非法 → check_gate 红", PROBE_illegal_gate_field),
    ("node-end 无起点 → verify 红", PROBE_unpaired_node_end),
    ("批准后改正文不动台账 → check_artifact 红", PROBE_body_edited_after_ledger),
    ("哈希稳定且时间戳贴机器时钟", PROBE_digest_is_deterministic_and_clock_bound),
    ("未注册节点名 → verify 红", PROBE_unregistered_node),
    ("上游关闸却放行 → verify 红", PROBE_closed_upstream_cannot_pass),
]


def run() -> dict:
    fired, missed = 0, []
    for name, probe in PROBES:
        try:
            detected, detail = probe()
        except Exception as exc:  # a crashing probe is a missed probe, never a pass
            detected, detail = False, f"探针异常：{type(exc).__name__}: {exc}"
        fired += 1 if detected else 0
        if not detected:
            missed.append(f"{name} 未检出（{detail}）")
        print(f"  {'✅' if detected else '⛔'} {name} — {detail}")
    return {"fired": fired, "total": len(PROBES), "missed": missed,
            "ranAt": datetime.now().astimezone().isoformat(timespec="seconds")}


def main(argv=None) -> int:
    target = Path(argv[0]) if argv else Path(".")
    report = run()
    out = target / schema.RUN_LOG.replace("run.jsonl", "detection.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"检出力 {report['fired']}/{report['total']} → {out}")
    return 0 if not report["missed"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
