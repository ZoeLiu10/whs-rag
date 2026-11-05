"""Everything you tune lives here, so every change shows up as a reviewable diff in a PR."""

# ---- Ingestion / index (changing these needs the ingest job to run again) ----
MAX_CHARS = 2000
VS_ENDPOINT = "rag-demo-endpoint"
EMBEDDING_MODEL = "databricks-gte-large-en"  # use a model listed on your Serving page

# ---- Retrieval + generation (picked up by the next eval run) ----
RAG_CONFIG = {
    "top_k": 5,
    "query_type": "HYBRID",
    "llm": "databricks-gpt-oss-120b",  # use a chat model listed on your Serving page
    "temperature": 0.0,
}

SYSTEM_PROMPT = """You answer questions about Australian WHS model Codes of Practice.
Use ONLY the context provided. If the context does not contain the answer, say you don't know.
After each claim, cite the source in the form [file_name#pN]."""

# ---- Eval gate: the eval job fails if any mean score is below its threshold ----
# Set each one a little below your baseline. With 20 in-scope questions, one question is 0.05,
# so leave about two questions of slack to avoid failing on judge noise.
EVAL_GATES = {
    "correctness": 0.50,
    "retrieval_groundedness": 0.50,
    "has_citation": 0.50,
    "refuses_out_of_scope": 0.50,
}
