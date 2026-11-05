# Databricks notebook source
# MAGIC %pip install -U databricks-vectorsearch

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

import os
import sys
import time

sys.path.append(os.path.abspath("../src"))

from databricks.vector_search.client import VectorSearchClient
from whs_rag.config import EMBEDDING_MODEL, VS_ENDPOINT

dbutils.widgets.text("catalog", "workspace")
dbutils.widgets.text("schema", "rag_demo")
CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")
SOURCE_TABLE = f"{CATALOG}.{SCHEMA}.chunks"
INDEX_NAME = f"{CATALOG}.{SCHEMA}.chunks_index"

vsc = VectorSearchClient(disable_notice=True)

# COMMAND ----------

existing = [e["name"] for e in vsc.list_endpoints().get("endpoints", [])]
if VS_ENDPOINT not in existing:
    vsc.create_endpoint(name=VS_ENDPOINT, endpoint_type="STANDARD")

while vsc.get_endpoint(VS_ENDPOINT).get("endpoint_status", {}).get("state") != "ONLINE":
    print("waiting for endpoint...")
    time.sleep(30)

# COMMAND ----------

try:
    index = vsc.get_index(endpoint_name=VS_ENDPOINT, index_name=INDEX_NAME)
    index.sync()  # index exists: pick up the rebuilt chunks table (TRIGGERED pipeline)
    print("sync started")
except Exception:
    index = vsc.create_delta_sync_index(
        endpoint_name=VS_ENDPOINT,
        index_name=INDEX_NAME,
        source_table_name=SOURCE_TABLE,
        primary_key="chunk_id",
        pipeline_type="TRIGGERED",
        embedding_source_column="chunk_text",
        embedding_model_endpoint_name=EMBEDDING_MODEL,
        columns_to_sync=["chunk_id", "file_name", "section", "page", "chunk_text"],
    )

while not index.describe().get("status", {}).get("ready"):
    print(index.describe()["status"]["message"])
    time.sleep(30)
print("index ready")
