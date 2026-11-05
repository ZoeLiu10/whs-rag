# Databricks notebook source
# MAGIC %pip install -U "mlflow[databricks]>=3.4" databricks-vectorsearch databricks-sdk openai

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

import os
import sys

sys.path.append(os.path.abspath("../src"))

import mlflow
from databricks.sdk import WorkspaceClient
from databricks.vector_search.client import VectorSearchClient
from mlflow.entities import Document, SpanType
from mlflow.genai.scorers import (
    Correctness,
    Guidelines,
    RelevanceToQuery,
    RetrievalGroundedness,
    RetrievalSufficiency,
    scorer,
)

from whs_rag import citation
from whs_rag.config import EVAL_GATES, RAG_CONFIG, SYSTEM_PROMPT, VS_ENDPOINT
from whs_rag.golden_set import in_scope, out_of_scope

dbutils.widgets.text("catalog", "workspace")
dbutils.widgets.text("schema", "rag_demo")
dbutils.widgets.text("git_commit", "local")
CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")
GIT_COMMIT = dbutils.widgets.get("git_commit")
INDEX_NAME = f"{CATALOG}.{SCHEMA}.chunks_index"
CONFIG = dict(RAG_CONFIG)

me = spark.sql("SELECT current_user()").first()[0]
mlflow.set_experiment(f"/Users/{me}/rag_demo")
mlflow.openai.autolog()

llm = WorkspaceClient().serving_endpoints.get_open_ai_client()
index = VectorSearchClient(disable_notice=True).get_index(endpoint_name=VS_ENDPOINT, index_name=INDEX_NAME)

# COMMAND ----------

# MAGIC %md
# MAGIC ## RAG app

# COMMAND ----------

COLUMNS = ["chunk_id", "file_name", "section", "page", "chunk_text"]


@mlflow.trace(span_type=SpanType.RETRIEVER)
def retrieve(question: str) -> list[Document]:
    res = index.similarity_search(
        query_text=question,
        columns=COLUMNS,
        num_results=CONFIG["top_k"],
        query_type=CONFIG["query_type"],
    )
    return [
        Document(
            id=chunk_id,
            page_content=text,
            metadata={"doc_uri": citation.source_label(file_name, page), "section": section, "score": score},
        )
        for chunk_id, file_name, section, page, text, score in res["result"]["data_array"]
    ]


def format_context(docs):
    return "\n\n---\n\n".join(f"[{d.metadata['doc_uri']}]\n{d.page_content}" for d in docs)


def message_text(message):
    c = message.content
    if isinstance(c, str):
        return c
    return "".join(p.get("text", "") for p in c if isinstance(p, dict) and p.get("type") == "text")


@mlflow.trace(span_type=SpanType.CHAIN)
def rag_app(question: str) -> str:
    mlflow.update_current_trace(tags={k: str(v) for k, v in CONFIG.items()})
    docs = retrieve(question)
    resp = llm.chat.completions.create(
        model=CONFIG["llm"],
        temperature=CONFIG["temperature"],
        max_tokens=800,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{format_context(docs)}\n\nQuestion: {question}"},
        ],
    )
    return citation.normalize_citations(message_text(resp.choices[0].message))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Scorers

# COMMAND ----------


@scorer
def has_citation(outputs) -> bool:
    return citation.has_citation(outputs)


@scorer
def source_hit(trace, expectations) -> bool:
    expected = expectations["expected_source"]
    span = trace.search_spans(span_type=SpanType.RETRIEVER)[0]
    return any(expected in d.get("metadata", {}).get("doc_uri", "") for d in (span.outputs or []))


IN_SCOPE_SCORERS = [
    source_hit,
    RetrievalSufficiency(),
    RetrievalGroundedness(),
    Correctness(),
    RelevanceToQuery(),
    has_citation,
]
OUT_OF_SCOPE_SCORERS = [
    Guidelines(
        name="refuses_out_of_scope",
        guidelines="The question is outside the WHS codes of practice. The response must say it does not know "
                   "or that the documents do not cover this, and must not answer from general knowledge.",
    ),
]

# COMMAND ----------

# MAGIC %md
# MAGIC ## Run the eval, tagged with the git commit

# COMMAND ----------

with mlflow.start_run(run_name=f"eval@{GIT_COMMIT[:7]}"):
    mlflow.log_params(CONFIG)
    mlflow.set_tags({"git_commit": GIT_COMMIT})
    r1 = mlflow.genai.evaluate(data=in_scope, predict_fn=rag_app, scorers=IN_SCOPE_SCORERS)
    r2 = mlflow.genai.evaluate(data=out_of_scope, predict_fn=rag_app, scorers=OUT_OF_SCOPE_SCORERS)

metrics = {**r1.metrics, **r2.metrics}
for k in sorted(metrics):
    print(f"{k:45s} {metrics[k]}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Eval gate: fail the job (and therefore CI) if quality dropped

# COMMAND ----------


def mean_score(name):
    for k, v in metrics.items():
        if k.startswith(name) and k.endswith("/mean"):
            return v
    raise KeyError(f"No '{name}/mean' metric. Available: {sorted(metrics)}")


failures = []
for name, threshold in EVAL_GATES.items():
    value = mean_score(name)
    status = "PASS" if value >= threshold else "FAIL"
    print(f"{status}  {name}: {value:.2f} (gate {threshold:.2f})")
    if value < threshold:
        failures.append(f"{name}={value:.2f} < {threshold:.2f}")

if failures:
    raise Exception("Eval gate failed: " + "; ".join(failures))
