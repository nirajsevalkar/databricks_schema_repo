# Databricks Job Setup

This project includes a Databricks Asset Bundle file at `databricks.yml`.

## 1. Install Databricks CLI

Install or update the Databricks CLI on your machine:

```powershell
winget install Databricks.DatabricksCLI
```

Verify:

```powershell
databricks --version
```

## 2. Authenticate

Run:

```powershell
databricks auth login --host https://YOUR-WORKSPACE-URL
```

Use your real Databricks workspace URL.

## 3. Update `databricks.yml`

Replace:

```yaml
host: https://YOUR-WORKSPACE-URL
```

with your workspace URL.

Do not commit private workspace URLs if this repo is public.

## 4. Find Cluster ID

In Databricks:

1. Open `Compute`.
2. Select the cluster you want to run the job on.
3. Copy the cluster ID from the browser URL or cluster details page.

## 5. Validate Bundle

From this repository root:

```powershell
databricks bundle validate `
  --var="cluster_id=YOUR_CLUSTER_ID"
```

## 6. Deploy Job

```powershell
databricks bundle deploy `
  --target dev `
  --var="cluster_id=YOUR_CLUSTER_ID"
```

## 7. Run Schema Export And Drift Detection

```powershell
databricks bundle run schema_governance_export `
  --target dev `
  --var="cluster_id=YOUR_CLUSTER_ID"
```

This job runs:

1. Export DEV schema snapshot.
2. Export UAT schema snapshot.
3. Compare DEV vs UAT.
4. Fail the job if drift exists.

## 8. Generate Release Package

After reviewing drift:

```powershell
databricks bundle run schema_governance_release_package `
  --target dev `
  --var="cluster_id=YOUR_CLUSTER_ID"
```

The release package is written under:

```text
${snapshot_root}/deployments
```

Default:

```text
/Workspace/Shared/databricks_schema_governance/output/deployments
```

## Important Notes

- First run `sql/metadata_repository.sql` in Databricks to create the metadata tables.
- Update `config/environments.example.json` with your real catalog and schema names.
- For production, use a Unity Catalog volume path for `snapshot_root`, such as:

```text
/Volumes/platform_metadata/default/schema_governance
```

Then pass it at runtime:

```powershell
databricks bundle run schema_governance_export `
  --target dev `
  --var="cluster_id=YOUR_CLUSTER_ID" `
  --var="snapshot_root=/Volumes/platform_metadata/default/schema_governance"
```

