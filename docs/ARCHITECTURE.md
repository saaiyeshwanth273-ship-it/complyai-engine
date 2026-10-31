# ComplyAI — AI & Regulatory Intelligence Architecture

## 1. Core Architectural Principle

> **"Gemma is the reasoning layer. The regulatory database is the knowledge layer."**

ComplyAI strictly separates language reasoning from authoritative legal knowledge. Laws, statutory sections, notification numbers, effective dates, and official URLs are **never** trained into model weights to memorize them; they are ingested, verified, versioned, and retrieved through an authoritative RAG pipeline.

```text
                    ┌───────────────────────────┐
                    │  AUTHORITATIVE REGULATORY │
                    │   & STATUTE REPOSITORIES  │
                    └─────────────┬─────────────┘
                                  │
                                  ↓
                    ┌───────────────────────────┐
                    │ REGULATORY INGESTION      │
                    │ PIPELINE & VERIFICATION   │
                    └─────────────┬─────────────┘
                                  │
                                  ↓
                    ┌───────────────────────────┐
                    │  NORMALIZATION, HASHING,  │
                    │  & VERSIONING (1.0 -> 2.0)│
                    └─────────────┬─────────────┘
                                  │
                                  ↓
                    ┌───────────────────────────┐
                    │ CHUNKING, SECTION PARSING,│
                    │ & METADATA EXTRACTION     │
                    └─────────────┬─────────────┘
                                  │
                                  ↓
                    ┌───────────────────────────┐
                    │ EMBEDDINGS + POSTGRESQL   │
                    │ + PGVECTOR / REPOSITORY   │
                    └─────────────┬─────────────┘
                                  │
User Document / Query ────────────┤
                                  ↓
                    ┌───────────────────────────┐
                    │ LEGAL QUERY ROUTER        │
                    │ Domain, Intent, Entity    │
                    └─────────────┬─────────────┘
                                  │
                                  ↓
                    ┌───────────────────────────┐
                    │ HYBRID RETRIEVAL          │
                    │ Vector + BM25 + Filters   │
                    └─────────────┬─────────────┘
                                  │
                                  ↓
                    ┌───────────────────────────┐
                    │ STATUTORY RERANKER        │
                    │ Hierarchy & Status Weight │
                    └─────────────┬─────────────┘
                                  │
                                  ↓
                    ┌───────────────────────────┐
                    │ TEMPORAL VALIDITY FILTER  │
                    │ Law in force at doc date  │
                    └─────────────┬─────────────┘
                                  │
                                  ↓
                    ┌───────────────────────────┐
                    │ APPLICABILITY ENGINE      │
                    │ Turnover, Headcount, Geo  │
                    └─────────────┬─────────────┘
                                  │
                                  ↓
                    ┌───────────────────────────┐
                    │ DOCUMENT COMPARATOR       │
                    │ Requirement vs Observed   │
                    └─────────────┬─────────────┘
                                  │
                                  ↓
                    ┌───────────────────────────┐
                    │ GEMMA REASONING LAYER     │
                    │ Structured JSON Synthesis │
                    └─────────────┬─────────────┘
                                  │
                                  ↓
                    ┌───────────────────────────┐
                    │ CITATION VALIDATOR        │
                    │ Section & Text Overlap    │
                    └─────────────┬─────────────┘
                                  │
                                  ↓
                    ┌───────────────────────────┐
                    │ GROUNDING VALIDATOR       │
                    │ Claim Type & Confidence   │
                    └─────────────┬─────────────┘
                                  │
                                  ↓
                    ┌───────────────────────────┐
                    │ RISK & ACTION PLAN ENGINE │
                    │ Prioritized Remediations  │
                    └─────────────┬─────────────┘
                                  │
                                  ↓
                    ┌───────────────────────────┐
                    │ REPRODUCIBLE AUDIT RESULT │
                    └───────────────────────────┘
```

## 2. Regulatory Source Hierarchy

The engine enforces an uncompromising source hierarchy:

- **Level 1 — Official Legislation:** Acts, Codes, Treaties, Directives, Constitutions.
- **Level 2 — Official Regulators:** RBI, SEBI, MCA, MeitY, CERT-In, EPFO, EDPB, FTC, ICO, PDPC.
- **Level 3 — Official Courts / Tribunals:** Supreme Court, High Courts, NCLAT, CJEU rulings.
- **Level 4 — Official Government Guidance:** FAQs, Circulars, Notifications, SOPs.
- **Level 5 — Recognized Legal Databases:** Bar Council, Law Commission, Official Gazettes.
- **Level 6 — Academic & Professional Commentary:** Legal journals, Bar associations.
- **Level 7 — General Web:** Strictly disqualified from producing binding compliance gaps.

## 3. The 16-Step Compliance Reasoning Pipeline

1. **Understand Business Context:** Organization type, size, turnover, operational jurisdictions.
2. **Operations Mapping:** Build Jurisdiction Graph (incorporation, physical presence, customers, employees, cross-border flows).
3. **Legal Query Routing:** Classify into legal domains (Labour, Privacy, Corporate, Cyber, Tax, etc.).
4. **Authoritative Retrieval:** Dense cosine search + sparse BM25 keyword matching with Reciprocal Rank Fusion.
5. **Statutory Reranking:** Boost official Level 1 legislation and penalize repealed or secondary sources.
6. **Temporal Filtering:** Filter retrieved statutes by the document/event date (`effective_from`, `effective_to`, `repealed_date`).
7. **Applicability Determination:** Check statutory thresholds (headcount >= 10, turnover >= 1000 Cr, etc.).
8. **Document Clause Extraction:** Parse untrusted user documents into structured legal clause units.
9. **Document-to-Law Comparison:** Model `Requirement -> Expected Control -> Business Document -> Observed Control -> Gap`.
10. **Risk Prioritization:** Calculate multi-factor risk score [0–100] based on regulatory exposure, statutory penalties, and business profile.
11. **Gemma Reasoning Synthesis:** Generate cautious, citation-grounded finding statements.
12. **Action Plan Generation:** Translate findings into structured, prioritized remediation checklists.
13. **Strict Citation Validation:** Verify source ID, official URL, exact section number, and quote overlap against the repository.
14. **Grounding Validation:** Categorize AI statements (`DIRECT_QUOTE`, `LEGAL_REQUIREMENT`, `AI_INTERPRETATION`, `UNCERTAINTY`) and reject ungrounded statements.
15. **Multi-Dimensional Confidence Scoring:** Calculate weighted aggregate confidence (`retrieval`, `source`, `applicability`, `reasoning`, `citation`).
16. **Reproducible Audit Ledger:** Record prompt version, model version, source checksums, and audit metadata in immutable log.

