# whs-rag

Retrieval-augmented Q&A over Australian WHS model Codes of Practice, built on Databricks
(Unity Catalog, `ai_parse_document`, AI Search, Foundation Model APIs, MLflow 3 tracing and evaluation).

## Layout
| Path | What |
| --- | --- |
| `src/whs_rag/` | Pure-Python logic (chunking, citation check), config and prompt, golden set |
| `notebooks/` | 01 ingest, 02 index, 03 RAG + eval + quality gate |
| `resources/rag_jobs.yml` | Jobs deployed by the bundle |
| `tests/` | Unit tests and golden-set data tests (run in CI) |
| `.github/workflows/` | CI on PRs (lint, tests, bundle validate, eval gate), CD on main (deploy) |

## Local
```bash
python -m venv .venv && source .venv/bin/activate
make install      # dev deps + git pre-commit hook (ruff fix + format on every commit)
make lint-fix     # auto-fix lint and reformat
make check        # lint + format check + tests (what CI runs)
databricks bundle validate && databricks bundle deploy
databricks bundle run ingest_job    # after chunking/document changes
databricks bundle run eval_job
```
