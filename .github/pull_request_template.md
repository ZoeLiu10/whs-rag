## What changed and why
<!-- One or two sentences. Link the failing traces or eval rows that motivated it. -->

## Type of change
- [ ] Prompt / generation config (`config.py`)
- [ ] Retrieval config (top_k, query_type, filters)
- [ ] Chunking or ingestion (needs `ingest_job` re-run: run CD manually with "run_ingest")
- [ ] Golden set (keep test changes in their own PR)
- [ ] Pipeline / CI only

## Eval results (from the `eval` check's MLflow run)
| Metric | main | this PR |
| --- | --- | --- |
| correctness | | |
| retrieval_groundedness | | |
| source_hit | | |
| has_citation | | |
| refuses_out_of_scope | | |

## Reviewer checklist
- [ ] CI green, including the eval gate
- [ ] No metric dropped by more than ~2 questions (0.10) without an explanation
- [ ] Golden set and app code are not changed in the same PR
- [ ] No hosts, tokens or personal paths in code
- [ ] Cost/latency impact considered (model, top_k, extra LLM calls)
