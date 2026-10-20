# Governance schemas

These YAML files describe the minimum structure and enumerations for the repository governance records. The executable validator is scripts/validate_core.py; the engine reads required-field lists and relation enumerations from these files, but they are not passed to a generic JSON-Schema engine.

- artifact-manifest.schema.yaml: .spec/manifest.yaml artifact inventory
- workflow.schema.yaml: .spec/workflow.yaml state, Gate, and task-envelope fields
- traceability.schema.yaml: .spec/traceability.yaml link fields and relations
- task-envelope.schema.yaml: shared/templates/task-envelope.yaml execution boundary

The validator additionally enforces cross-file references, filesystem paths, duplicate-key rejection, lifecycle graph rules, Gate policy, and authorization semantics.
