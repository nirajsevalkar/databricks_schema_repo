# Databricks Schema Governance Framework

This repository is a starter codebase for a DACPAC-like Databricks schema governance process.
It is based on the attached process document and covers:

- Metadata repository setup
- Automatic schema export from Databricks
- Stable DDL hashing and object versioning
- Git-friendly schema file export
- Environment drift detection
- Deployment package generation with release notes and rollback placeholders
- Master data deployment examples

## Repository Layout

```text
config/                     Environment and object selection examples
examples/                   Sample schema, view, master data, and snapshot files
scripts/                    Databricks-ready entry points
sql/                        Metadata repository DDL
src/dsgf/                   Reusable framework code
tests/                      Lightweight local tests
```

## Phase 1 MVP Flow

1. Run `sql/metadata_repository.sql` in Databricks.
2. Update `config/environments.example.json` for DEV, UAT, and PROD.
3. Run `scripts/schema_export.py` as a Databricks job in DEV.
4. Commit the generated `schema/` and `master_data/` files to Git.
5. Run `scripts/detect_drift.py` before promoting to UAT or PROD.

## Local Example Commands

Use the bundled or system Python from the repository root:

```powershell
python scripts/detect_drift.py `
  --source examples/snapshots/dev_snapshot.json `
  --target examples/snapshots/uat_snapshot.json `
  --output examples/output/drift_report.json
```

Generate a deployment package:

```powershell
python scripts/generate_deployment.py `
  --source examples/snapshots/dev_snapshot.json `
  --target examples/snapshots/uat_snapshot.json `
  --release-id Release_2026_06_20 `
  --output-dir deployments
```

## Databricks Job Examples

Schema export:

```python
dbutils.widgets.text("environment", "DEV")
dbutils.widgets.text("config_path", "/Workspace/Repos/team/schema-governance/config/environments.example.json")
%run ./scripts/schema_export
```

Drift detection:

```bash
python scripts/detect_drift.py --source-env DEV --target-env UAT --fail-on-drift
```

## Versioning

Object versions follow `MAJOR.MINOR.PATCH`:

- `1.0.0`: initial release
- `1.1.0`: additive schema change, such as `ADD COLUMN`
- `2.0.0`: breaking change

The MVP bumps minor versions automatically when a hash changes. Breaking-change classification can be extended in `src/dsgf/versioning.py`.

