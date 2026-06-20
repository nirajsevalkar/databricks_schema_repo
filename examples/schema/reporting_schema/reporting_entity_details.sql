CREATE VIEW sample_catalog_dev.reporting_schema.reporting_entity_details AS
SELECT
  entity_id,
  entity_name,
  score_value
FROM sample_catalog_dev.gold_schema.entity_details;

