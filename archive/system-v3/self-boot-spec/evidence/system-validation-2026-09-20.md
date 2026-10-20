# System validation evidence — updated 2026-09-21

This report retains its original 2026-09-20 filename/record identity; the validation below was performed on September 21, 2026. This is an execution record, not an approval.

## Actual local results

| Command | Result |
|---|---|
| scripts/run-tests.ps1 | Exit 0 — 30 tests passed, including subcases |
| scripts/validate.ps1 (final run) | Exit 0 — system validation passed; 30 tests passed in 12.673 seconds; explicit external-knowledge warning |
| scripts/bootstrap.ps1 | Exit 0 — repaired incomplete ensurepip setup, installed PyYAML 6.0.3 in .venv, ran system validation and the then-current 29 tests |
| scripts/validate-skill-contract.ps1 -IncludeLegacy | Exit 0 |
| python scripts/validate_core.py graph | Exit 0 |
| git diff --check | Exit 0; only CRLF normalization warnings |

Environment: Windows PowerShell 5, Python 3.11.15, PyYAML 6.0.3. Sandbox ACLs prevented writes inside tempfile-created directories; after approval, tests were rerun outside the sandbox and passed. The 13 empty failed-test directories were verified and removed. These failures were not counted as passes.

## Regression coverage

- Strict duplicate YAML key rejection and malformed document diagnostics.
- Root self-spec, historical fixture required fields and dangling evidence references.
- Whole-graph completion/handoff reachability and review/test bypass rejection.
- PASS P0/P1 rejection, boolean types, CONDITIONAL authorization, scope, expiry and execution binding.
- Synthetic CREATE/CHANGE/DEFECT task readiness, without claiming a real project pilot.
- Task actor/state/execution/revision binding, path scopes and forbidden-parent precedence.
- Separate deploy and clear-block authorization; ambiguous Gate/outcome rejection.
- Current evidence roles, source/content SHA-256 digests and stale revision rejection.
- Read-only CLI: no state change or Skill execution.
- Knowledge missing-policy warnings and strict-mode failure.

## Limits and acceptance

SKILLS_KNOWLEDGE_ROOT was not configured: local system validation was intentionally degraded with an explicit warning, not a full external-knowledge validation.

Remote Windows/Linux CI, independent acceptance, real project pilot, production deployment and rollback drills have not been performed. YAML policy and digests enforce consistency only; trusted approvals require external protected review/signing.

DEC-SYSTEM-001 stays DRAFT, and GATE-SYSTEM-001/workflow stay BLOCKED pending independent acceptance and a real project pilot. Automated checks do not approve this engineering system.
