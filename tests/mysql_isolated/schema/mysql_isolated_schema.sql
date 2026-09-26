CREATE TABLE IF NOT EXISTS companies (
    id CHAR(36) NOT NULL,
    organization_id CHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT NULL,
    tax_number VARCHAR(32) NOT NULL,
    street VARCHAR(255) NULL,
    city VARCHAR(255) NULL,
    zip_code VARCHAR(64) NULL,
    country VARCHAR(128) NULL,
    phone_number VARCHAR(64) NULL,
    email VARCHAR(255) NULL,
    bank_account_number VARCHAR(64) NULL,
    bank_account_country_code VARCHAR(8) NULL,
    role VARCHAR(32) NOT NULL,
    is_active TINYINT(1) NOT NULL,
    created_at DATETIME NULL,
    created_by_user_id CHAR(36) NULL,
    updated_at DATETIME NULL,
    updated_by_user_id CHAR(36) NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_companies_org_tax (organization_id, tax_number),
    KEY idx_companies_org (organization_id),
    KEY idx_companies_org_role_active (organization_id, role, is_active),
    KEY idx_companies_org_email (organization_id, email),
    KEY idx_companies_org_phone (organization_id, phone_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS documents (
    id CHAR(36) NOT NULL,
    organization_id CHAR(36) NOT NULL,
    financial_record_id CHAR(36) NULL,
    document_source VARCHAR(32) NULL,
    document_type VARCHAR(32) NULL,
    document_number VARCHAR(255) NULL,
    seller_nip VARCHAR(64) NULL,
    parsed_payload JSON NULL,
    file_hash VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    filename VARCHAR(255) NOT NULL,
    mime_type VARCHAR(255) NULL,
    size BIGINT NULL,
    created_at DATETIME NULL,
    created_by_user_id CHAR(36) NULL,
    updated_at DATETIME NULL,
    updated_by_user_id CHAR(36) NULL,
    PRIMARY KEY (id),
    KEY idx_documents_org (organization_id),
    KEY idx_documents_org_record (organization_id, financial_record_id),
    KEY idx_documents_org_hash (organization_id, file_hash)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS value_types (
    id CHAR(36) NOT NULL,
    organization_id CHAR(36) NOT NULL,
    code VARCHAR(64) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT NULL,
    direction VARCHAR(32) NOT NULL,
    is_active TINYINT(1) NOT NULL,
    created_at DATETIME NULL,
    created_by_user_id CHAR(36) NULL,
    updated_at DATETIME NULL,
    updated_by_user_id CHAR(36) NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_value_types_org_code (organization_id, code),
    KEY idx_value_types_org (organization_id),
    KEY idx_value_types_org_active (organization_id, is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS number_sequences (
    organization_id CHAR(36) NOT NULL,
    scope_key VARCHAR(128) NOT NULL,
    current_value BIGINT NOT NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (organization_id, scope_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS financial_records (
    id CHAR(36) NOT NULL,
    organization_id CHAR(36) NOT NULL,
    reference VARCHAR(255) NOT NULL,
    invoice_date DATE NULL,
    selling_date DATE NULL,
    buyer_id CHAR(36) NOT NULL,
    seller_id CHAR(36) NOT NULL,
    payment_method VARCHAR(32) NOT NULL,
    due_date DATE NULL,
    paid_date DATE NULL,
    payment_status VARCHAR(32) NOT NULL,
    status VARCHAR(32) NOT NULL,
    timestamp DATETIME NULL,
    tags JSON NULL,
    created_at DATETIME NULL,
    created_by_user_id CHAR(36) NULL,
    updated_at DATETIME NULL,
    updated_by_user_id CHAR(36) NULL,
    PRIMARY KEY (id),
    KEY idx_fin_records_org (organization_id),
    KEY idx_fin_records_org_ref (organization_id, reference),
    KEY idx_fin_records_org_seller (organization_id, seller_id),
    KEY idx_fin_records_org_status (organization_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS financial_record_lines (
    id CHAR(36) NOT NULL,
    organization_id CHAR(36) NOT NULL,
    financial_record_id CHAR(36) NULL,
    contract_id CHAR(36) NULL,
    contract_node_id CHAR(36) NULL,
    value_type_id CHAR(36) NULL,
    item_name VARCHAR(255) NOT NULL,
    quantity DECIMAL(18,6) NULL,
    unit VARCHAR(32) NULL,
    amount_value DECIMAL(18,2) NOT NULL,
    amount_input_type VARCHAR(16) NOT NULL DEFAULT 'net',
    vat_rate DECIMAL(5,2) NOT NULL,
    tax_treatment VARCHAR(32) NOT NULL,
    description TEXT NULL,
    created_at DATETIME NULL,
    created_by_user_id CHAR(36) NULL,
    updated_at DATETIME NULL,
    updated_by_user_id CHAR(36) NULL,
    agreement_id CHAR(36) NULL,
    agreement_node_id CHAR(36) NULL,
    PRIMARY KEY (id),
    KEY idx_fin_lines_org (organization_id),
    KEY idx_fin_lines_org_record (organization_id, financial_record_id),
    KEY idx_fin_lines_org_contract (organization_id, contract_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS contracts (
    id CHAR(36) NOT NULL,
    organization_id CHAR(36) NOT NULL,
    code VARCHAR(128) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT NULL,
    owner_id CHAR(36) NOT NULL,
    client_id CHAR(36) NULL,
    start_date DATE NULL,
    end_date DATE NULL,
    budget DECIMAL(18,2) NULL,
    path TEXT NULL,
    status VARCHAR(32) NOT NULL,
    created_at DATETIME NULL,
    created_by_user_id CHAR(36) NULL,
    updated_at DATETIME NULL,
    updated_by_user_id CHAR(36) NULL,
    contract_type VARCHAR(32) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_contracts_org_code (organization_id, code),
    KEY idx_contracts_org (organization_id),
    KEY idx_contracts_org_owner_type (organization_id, owner_id, contract_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS contract_nodes (
    id CHAR(36) NOT NULL,
    organization_id CHAR(36) NOT NULL,
    contract_id CHAR(36) NOT NULL,
    parent_id CHAR(36) NULL,
    code VARCHAR(128) NOT NULL,
    name VARCHAR(255) NOT NULL,
    budget DECIMAL(18,2) NULL,
    quantity DECIMAL(18,6) NULL,
    unit VARCHAR(32) NULL,
    is_active TINYINT(1) NOT NULL,
    created_at DATETIME NULL,
    created_by_user_id CHAR(36) NULL,
    updated_at DATETIME NULL,
    updated_by_user_id CHAR(36) NULL,
    PRIMARY KEY (id),
    KEY idx_contract_nodes_org (organization_id),
    KEY idx_contract_nodes_org_contract (organization_id, contract_id),
    KEY idx_contract_nodes_org_parent (organization_id, parent_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS contract_node_progress (
    id CHAR(36) NOT NULL,
    organization_id CHAR(36) NOT NULL,
    contract_node_id CHAR(36) NOT NULL,
    progress_date DATE NOT NULL,
    progress DECIMAL(10,6) NOT NULL,
    created_at DATETIME NULL,
    created_by_user_id CHAR(36) NULL,
    updated_at DATETIME NULL,
    updated_by_user_id CHAR(36) NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_contract_node_progress (organization_id, contract_node_id, progress_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS contract_snapshots (
    id CHAR(36) NOT NULL,
    organization_id CHAR(36) NOT NULL,
    contract_id CHAR(36) NOT NULL,
    snapshot_date DATE NOT NULL,
    created_at DATETIME NULL,
    created_by_user_id CHAR(36) NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_contract_snapshots_org_contract_date (organization_id, contract_id, snapshot_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS contract_node_snapshots (
    id CHAR(36) NOT NULL,
    snapshot_id CHAR(36) NOT NULL,
    contract_node_id CHAR(36) NOT NULL,
    planned_budget DECIMAL(18,2) NOT NULL,
    progress DECIMAL(10,6) NOT NULL,
    PRIMARY KEY (id),
    KEY idx_node_snapshots_snapshot (snapshot_id),
    KEY idx_node_snapshots_contract_node (contract_node_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS contract_node_value_snapshots (
    id CHAR(36) NOT NULL,
    node_snapshot_id CHAR(36) NOT NULL,
    value_type_id CHAR(36) NOT NULL,
    net DECIMAL(18,2) NOT NULL,
    vat DECIMAL(18,2) NOT NULL,
    gross DECIMAL(18,2) NOT NULL,
    non_deductible DECIMAL(18,2) NOT NULL,
    PRIMARY KEY (id),
    KEY idx_node_value_snapshots_node_snapshot (node_snapshot_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS organizations (
    id CHAR(36) NOT NULL,
    code VARCHAR(128) NOT NULL,
    name VARCHAR(255) NOT NULL,
    is_active TINYINT(1) NOT NULL,
    created_at DATETIME NULL,
    created_by_user_id CHAR(36) NULL,
    updated_at DATETIME NULL,
    updated_by_user_id CHAR(36) NULL,
    settings JSON NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_organizations_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS users (
    id CHAR(36) NOT NULL,
    login VARCHAR(255) NOT NULL,
    email VARCHAR(255) NULL,
    full_name VARCHAR(255) NULL,
    is_active TINYINT(1) NOT NULL,
    created_at DATETIME NULL,
    created_by_user_id CHAR(36) NULL,
    updated_at DATETIME NULL,
    updated_by_user_id CHAR(36) NULL,
    password_hash VARCHAR(255) NULL,
    last_login_at DATETIME NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_users_login (login)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS organization_users (
    id CHAR(36) NOT NULL,
    organization_id CHAR(36) NOT NULL,
    user_id CHAR(36) NOT NULL,
    role VARCHAR(32) NOT NULL,
    is_active TINYINT(1) NOT NULL,
    created_at DATETIME NULL,
    created_by_user_id CHAR(36) NULL,
    updated_at DATETIME NULL,
    updated_by_user_id CHAR(36) NULL,
    invited_at DATETIME NULL,
    invited_by_user_id CHAR(36) NULL,
    accepted_at DATETIME NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_org_user (organization_id, user_id),
    KEY idx_org_users_org (organization_id),
    KEY idx_org_users_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Kopia widoku z migracji 5767976b729c (add_amount_input_type_to_financial_ledger)
CREATE OR REPLACE VIEW financial_ledger AS
SELECT
    frl.id AS line_id,
    frl.organization_id AS organization_id,
    frl.financial_record_id AS record_id,

    COALESCE(fr.selling_date, fr.invoice_date) AS record_date,
    YEAR(COALESCE(fr.selling_date, fr.invoice_date)) AS record_year,
    MONTH(COALESCE(fr.selling_date, fr.invoice_date)) AS record_month,

    fr.buyer_id AS buyer_id,
    fr.seller_id AS seller_id,

    vt.direction AS direction,

    frl.contract_id AS contract_id,
    c.code AS contract_code,
    c.contract_type AS contract_type,
    c.owner_id AS contract_owner_id,

    frl.value_type_id AS value_type_id,
    vt.code AS value_type_code,
    vt.name AS value_type_name,

    frl.item_name AS item_name,
    frl.description AS description,

    frl.amount_value AS amount_value,
    frl.amount_input_type AS amount_input_type,

    frl.vat_rate AS vat_rate,
    frl.tax_treatment AS tax_treatment,

    fr.payment_status AS payment_status,
    fr.paid_date AS paid_date,
    fr.status AS status

FROM financial_record_lines frl

JOIN financial_records fr
    ON fr.id = frl.financial_record_id

LEFT JOIN value_types vt
    ON vt.id = frl.value_type_id

LEFT JOIN contracts c
    ON c.id = frl.contract_id

WHERE fr.status <> 'deleted';
