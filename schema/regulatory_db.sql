-- ====================================================================
-- COMPLYAI REGULATORY INTELLIGENCE ENGINE - DATABASE SCHEMA
-- PostgreSQL 15+ with pgvector extension
-- Authoritative Legal Knowledge Store & Compliance Audit Audit Trail
-- ====================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Enum types for status, hierarchy, and legal instrument types
CREATE TYPE source_hierarchy_enum AS ENUM (
    'LEVEL_1_OFFICIAL_LEGISLATION',
    'LEVEL_2_OFFICIAL_REGULATOR',
    'LEVEL_3_OFFICIAL_COURT_TRIBUNAL',
    'LEVEL_4_OFFICIAL_GOV_GUIDANCE',
    'LEVEL_5_RECOGNIZED_LEGAL_DATABASE',
    'LEVEL_6_ACADEMIC_COMMENTARY',
    'LEVEL_7_GENERAL_WEB'
);

CREATE TYPE instrument_type_enum AS ENUM (
    'CONSTITUTION',
    'ACT',
    'CODE',
    'RULE',
    'REGULATION',
    'NOTIFICATION',
    'CIRCULAR',
    'GOV_ORDER',
    'ORDINANCE',
    'DIRECTIVE',
    'TREATY',
    'CONVENTION',
    'RECOMMENDATION',
    'STANDARD',
    'FRAMEWORK',
    'GUIDELINE',
    'ADVISORY',
    'CONTRACTUAL_CLAUSE',
    'BEST_PRACTICE'
);

CREATE TYPE source_status_enum AS ENUM (
    'DRAFT',
    'PENDING_REVIEW',
    'VERIFIED',
    'SUPERSEDED',
    'REPEALED',
    'ARCHIVED'
);

CREATE TYPE risk_level_enum AS ENUM (
    'LOW',
    'MEDIUM',
    'HIGH',
    'CRITICAL'
);

-- 1. REGULATORY SOURCES (Authoritative Documents)
CREATE TABLE IF NOT EXISTS regulatory_sources (
    document_id VARCHAR(120) PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    short_title VARCHAR(255) NOT NULL,
    jurisdiction VARCHAR(100) NOT NULL, -- e.g., 'India', 'India:Karnataka', 'EU', 'US:Federal', 'US:California'
    state_or_province VARCHAR(100),
    authority VARCHAR(255) NOT NULL, -- e.g., 'Ministry of Corporate Affairs', 'EDPB', 'FTC'
    instrument_type instrument_type_enum NOT NULL DEFAULT 'ACT',
    domain VARCHAR(100) NOT NULL, -- e.g., 'LABOUR_EMPLOYMENT', 'PRIVACY_DATA_PROTECTION', 'TAX_DIRECT'
    hierarchy source_hierarchy_enum NOT NULL DEFAULT 'LEVEL_1_OFFICIAL_LEGISLATION',
    status source_status_enum NOT NULL DEFAULT 'PENDING_REVIEW',
    publication_date DATE,
    effective_date DATE,
    repealed_date DATE,
    superseded_by VARCHAR(120),
    version VARCHAR(50) NOT NULL DEFAULT '1.0',
    source_url TEXT NOT NULL,
    source_hash VARCHAR(64) NOT NULL,
    is_demo BOOLEAN NOT NULL DEFAULT FALSE,
    verified_at TIMESTAMPTZ,
    verified_by VARCHAR(100),
    last_checked_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sources_jurisdiction ON regulatory_sources(jurisdiction);
CREATE INDEX idx_sources_domain ON regulatory_sources(domain);
CREATE INDEX idx_sources_status ON regulatory_sources(status);
CREATE INDEX idx_sources_effective ON regulatory_sources(effective_date, repealed_date);

-- 2. LEGAL SECTIONS (Parsed Structural Units)
CREATE TABLE IF NOT EXISTS legal_sections (
    section_id VARCHAR(160) PRIMARY KEY,
    document_id VARCHAR(120) NOT NULL REFERENCES regulatory_sources(document_id) ON DELETE CASCADE,
    section_number VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL,
    text TEXT NOT NULL,
    penalties_text TEXT,
    exceptions_text TEXT,
    effective_from DATE,
    effective_to DATE,
    embedding vector(384), -- 384 or 768 dimensions based on embedding model
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sections_document ON legal_sections(document_id);
CREATE INDEX idx_sections_number ON legal_sections(section_number);
-- HNSW Vector Index for fast semantic retrieval
CREATE INDEX idx_sections_embedding ON legal_sections USING hnsw (embedding vector_cosine_ops);

-- 3. LEGAL REQUIREMENTS (Extracted Atomic Obligations)
CREATE TABLE IF NOT EXISTS legal_requirements (
    requirement_id VARCHAR(180) PRIMARY KEY,
    section_id VARCHAR(160) NOT NULL REFERENCES legal_sections(section_id) ON DELETE CASCADE,
    document_id VARCHAR(120) NOT NULL REFERENCES regulatory_sources(document_id) ON DELETE CASCADE,
    obligation TEXT NOT NULL,
    subject VARCHAR(150) NOT NULL, -- e.g., 'Employer', 'Data Fiduciary', 'Company'
    action VARCHAR(100) NOT NULL,  -- e.g., 'maintain', 'furnish', 'appoint'
    object VARCHAR(255) NOT NULL,  -- e.g., 'register of wages', 'audit report'
    condition TEXT,
    exception TEXT,
    deadline_rule TEXT,
    penalties TEXT,
    jurisdiction VARCHAR(100) NOT NULL,
    territorial_scope VARCHAR(100) NOT NULL DEFAULT 'National',
    confidence NUMERIC(4, 3) NOT NULL DEFAULT 0.95,
    embedding vector(384),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_requirements_doc ON legal_requirements(document_id);
CREATE INDEX idx_requirements_subject ON legal_requirements(subject);
CREATE INDEX idx_requirements_embedding ON legal_requirements USING hnsw (embedding vector_cosine_ops);

-- 4. APPLICABILITY RULES
CREATE TABLE IF NOT EXISTS applicability_rules (
    rule_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    requirement_id VARCHAR(180) NOT NULL REFERENCES legal_requirements(requirement_id) ON DELETE CASCADE,
    min_employee_count INT DEFAULT 0,
    max_employee_count INT,
    min_turnover_inr NUMERIC(15, 2) DEFAULT 0,
    max_turnover_inr NUMERIC(15, 2),
    industry_whitelist TEXT[], -- e.g., {'IT', 'Manufacturing', 'Finance'}
    entity_types TEXT[],      -- e.g., {'Pvt Ltd', 'LLP', 'Public Ltd'}
    state_applicability TEXT[],
    cross_border_data_trigger BOOLEAN DEFAULT FALSE,
    regulated_activity_trigger TEXT[],
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 5. LEGAL DEFINITIONS
CREATE TABLE IF NOT EXISTS legal_definitions (
    definition_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id VARCHAR(120) NOT NULL REFERENCES regulatory_sources(document_id) ON DELETE CASCADE,
    term VARCHAR(200) NOT NULL,
    definition TEXT NOT NULL,
    source_section VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_definitions_term ON legal_definitions(term);

-- 6. REGULATORY VERSIONS & AMENDMENTS
CREATE TABLE IF NOT EXISTS regulatory_versions (
    version_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id VARCHAR(120) NOT NULL REFERENCES regulatory_sources(document_id) ON DELETE CASCADE,
    version_number VARCHAR(50) NOT NULL,
    amendment_name VARCHAR(500),
    notification_number VARCHAR(255),
    amendment_date DATE NOT NULL,
    summary_of_changes TEXT NOT NULL,
    previous_checksum VARCHAR(64),
    new_checksum VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 7. AUDIT LOGS (Reproducible Compliance Records)
CREATE TABLE IF NOT EXISTS audit_logs (
    audit_id VARCHAR(120) PRIMARY KEY,
    organization_id VARCHAR(120) NOT NULL,
    business_context JSONB NOT NULL,
    status VARCHAR(50) NOT NULL,
    findings JSONB NOT NULL,
    action_plans JSONB NOT NULL,
    sources_cited JSONB NOT NULL,
    confidence_scores JSONB NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    prompt_version VARCHAR(50) NOT NULL,
    knowledge_base_version VARCHAR(50) NOT NULL,
    requires_professional_review BOOLEAN NOT NULL DEFAULT TRUE,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_org ON audit_logs(organization_id);

-- 8. PROFESSIONAL REVIEWER FEEDBACK
CREATE TABLE IF NOT EXISTS reviewer_feedback (
    feedback_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audit_id VARCHAR(120) NOT NULL REFERENCES audit_logs(audit_id) ON DELETE CASCADE,
    finding_id VARCHAR(120) NOT NULL,
    reviewer_id VARCHAR(120) NOT NULL,
    reviewer_decision VARCHAR(50) NOT NULL, -- 'APPROVED', 'MODIFIED', 'REJECTED', 'INFO_REQUESTED'
    reviewer_notes TEXT,
    corrected_risk risk_level_enum,
    corrected_citations JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 9. SOURCE MONITORING & FRESHNESS
CREATE TABLE IF NOT EXISTS source_monitoring (
    monitor_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id VARCHAR(120) NOT NULL REFERENCES regulatory_sources(document_id) ON DELETE CASCADE,
    last_checked_at TIMESTAMPTZ NOT NULL,
    last_changed_at TIMESTAMPTZ,
    current_hash VARCHAR(64) NOT NULL,
    previous_hash VARCHAR(64),
    change_detected BOOLEAN NOT NULL DEFAULT FALSE,
    change_summary TEXT,
    review_status VARCHAR(50) NOT NULL DEFAULT 'CURRENT'
);

-- 10. COMPLIANCE CALENDAR EVENTS
CREATE TABLE IF NOT EXISTS compliance_calendar_events (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id VARCHAR(120) NOT NULL,
    obligation_name VARCHAR(500) NOT NULL,
    authority VARCHAR(255) NOT NULL,
    source_id VARCHAR(120) NOT NULL,
    due_date DATE NOT NULL,
    recurrence VARCHAR(50), -- 'MONTHLY', 'QUARTERLY', 'ANNUAL', 'ONE_TIME'
    responsible_person VARCHAR(150),
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING'
);

