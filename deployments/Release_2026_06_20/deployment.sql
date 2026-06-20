-- Generated deployment script
-- Review before executing in UAT or PROD.

-- MISSING_IN_TARGET: sample_catalog.reporting_schema.reporting_entity_details
CREATE VIEW sample_catalog.reporting_schema.reporting_entity_details AS SELECT entity_id, entity_name, score_value FROM sample_catalog.gold_schema.entity_details;

-- HASH_MISMATCH: sample_catalog.gold_schema.entity_details
CREATE TABLE sample_catalog.gold_schema.entity_details (entity_id STRING, entity_name STRING, score_value DOUBLE) USING DELTA;
