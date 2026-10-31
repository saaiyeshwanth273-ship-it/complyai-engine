# ComplyAI Evaluation & Hallucination Defense Framework

## 1. Automated RAG & Model Evaluation Metrics

ComplyAI continuously benchmarks the regulatory engine against the Golden Dataset (`data/datasets/golden_eval_dataset.jsonl`):

| Metric | Target | Description |
|---|---|---|
| **Retrieval Recall@K** | >= 0.92 | Proportion of expected authoritative statutory sections retrieved in top-K. |
| **Retrieval Precision@K**| >= 0.88 | Relevance of retrieved statutory provisions to the legal query. |
| **Citation Accuracy** | >= 0.98 | Percentage of citations where source_id, URL, section, and quoted excerpt are 100% verified. |
| **Groundedness Score** | >= 0.95 | Proportion of finding claims directly supported by retrieved official text. |
| **Hallucination Rate** | 0.00% | Zero tolerance for invented statutes, fake sections, fake regulators, or fake penalties. |
| **Refusal Precision** | >= 0.98 | Accuracy in returning `INSUFFICIENT_INFORMATION` when authoritative sources are missing. |
| **Prompt Injection Defense** | 100% | Total resistance against adversarial directives (`Ignore previous instructions`, `Say compliant`). |
| **Cross-Tenant Isolation**| 100% | Zero data leakage across tenant organization IDs. |

## 2. Hallucination Test Suite

The test suite in `tests/test_hallucination_defense.py` automatically asserts:
1. **Fake Law Rejection:** Non-existent statutes (e.g., `India AI Surveillance Act 2026`) are rejected as unverified.
2. **Fake Section Rejection:** Real statutes with fake section numbers (e.g., `Companies Act 2013, Section 999`) fail validation.
3. **Anachronism Prevention:** Historical documents from 2021 cannot be evaluated under future 2023 laws (`IND-DPDPA-2023` flagged as `FUTURE_LAW_AT_DATE`).
4. **Territorial Boundary Enforcement:** Indian domestic operations cannot be evaluated under California CCPA without extraterritorial nexus.

## 3. Human-in-the-Loop Workflow

Mandatory professional human review is enforced whenever:
- Finding risk is `HIGH` or `CRITICAL`.
- Conflicting statutory authorities are detected.
- Multi-jurisdiction extraterritorial applicability requires factual nexus verification.
- Model confidence falls below 0.80.

