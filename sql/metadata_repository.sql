CREATE CATALOG IF NOT EXISTS platform_metadata;

CREATE SCHEMA IF NOT EXISTS platform_metadata.default;

CREATE TABLE IF NOT EXISTS platform_metadata.default.schema_registry (
  object_name STRING,
  object_type STRING,
  catalog_name STRING,
  schema_name STRING,
  schema_hash STRING,
  schema_version STRING,
  ddl_definition STRING,
  environment STRING,
  extracted_on TIMESTAMP
) USING DELTA;

CREATE TABLE IF NOT EXISTS platform_metadata.default.deployment_history (
  deployment_id STRING,
  source_environment STRING,
  target_environment STRING,
  deployment_date TIMESTAMP,
  deployed_by STRING,
  deployment_status STRING
) USING DELTA;

CREATE TABLE IF NOT EXISTS platform_metadata.default.schema_drift_log (
  object_name STRING,
  source_hash STRING,
  target_hash STRING,
  drift_detected_on TIMESTAMP,
  status STRING
) USING DELTA;

