# Databricks notebook source
# MAGIC %md
# MAGIC # 01 Ingest
# MAGIC Parse new PDFs in the volume, explode them into elements, and rebuild the `chunks` table.

# COMMAND ----------

import os
import sys

sys.path.append(os.path.abspath("../src"))  # the repo's src/, works in a Git folder and in a bundle deploy

from whs_rag.chunking import chunk_elements, format_chunk
from whs_rag.config import MAX_CHARS

dbutils.widgets.text("catalog", "workspace")
dbutils.widgets.text("schema", "rag_demo")
CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")
VOLUME_PATH = f"/Volumes/{CATALOG}/{SCHEMA}/raw_docs"
T = f"{CATALOG}.{SCHEMA}"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Parse only files that haven't been parsed yet
# MAGIC Parsing is the paid step, so it's incremental: re-running the job doesn't re-parse old PDFs.

# COMMAND ----------

spark.sql(f"CREATE TABLE IF NOT EXISTS {T}.parsed_docs (path STRING, parsed VARIANT)")

spark.sql(f"""
INSERT INTO {T}.parsed_docs
SELECT f.path,
       ai_parse_document(f.content, map('version', '2.0', 'descriptionElementTypes', '')) AS parsed
FROM READ_FILES('{VOLUME_PATH}/', format => 'binaryFile') AS f
LEFT ANTI JOIN {T}.parsed_docs AS p ON f.path = p.path
""")

display(spark.sql(f"SELECT path, parsed:error_status FROM {T}.parsed_docs"))

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE TABLE {T}.doc_elements AS
SELECT
  regexp_extract(p.path, '[^/]+$', 0)  AS file_name,
  e.pos                                AS element_id,
  e.value:type::string                 AS type,
  e.value:content::string              AS content,
  e.value:bbox[0]:page_id::int         AS page
FROM {T}.parsed_docs p,
     LATERAL variant_explode(p.parsed:document:elements) AS e
WHERE e.value:type::string IN ('title', 'section_header', 'text', 'table', 'caption', 'footnote')
  AND e.value:content::string IS NOT NULL
""")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Chunk (logic lives in `src/whs_rag/chunking.py` and is unit-tested in CI)

# COMMAND ----------

elements = spark.table(f"{T}.doc_elements").orderBy("file_name", "element_id").toPandas()

rows = []
for file_name, g in elements.groupby("file_name", sort=False):
    for i, c in enumerate(chunk_elements(g.to_dict("records"), MAX_CHARS)):
        rows.append((
            f"{file_name}::{i:04d}",
            file_name,
            c["section"],
            c["page"],
            format_chunk(file_name, c["section"], c["text"]),
        ))

chunks_df = spark.createDataFrame(
    rows, schema="chunk_id string, file_name string, section string, page int, chunk_text string"
)
chunks_df.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{T}.chunks")
spark.sql(f"ALTER TABLE {T}.chunks SET TBLPROPERTIES (delta.enableChangeDataFeed = true)")

display(spark.sql(f"""
  SELECT file_name, count(*) AS n_chunks, round(avg(length(chunk_text))) AS avg_chars
  FROM {T}.chunks GROUP BY file_name
"""))
