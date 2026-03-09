"""initial schema

Revision ID: 22448d13d143
Revises: 
Create Date: 2026-02-27 20:04:13.003512

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '22448d13d143'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE companies (
          id char(36) NOT NULL,
          organization_id char(36) DEFAULT NULL,
          name varchar(255) NOT NULL,
          description text,
          tax_number varchar(32) NOT NULL,
          street varchar(255) DEFAULT NULL,
          city varchar(255) DEFAULT NULL,
          zip_code varchar(255) DEFAULT NULL,
          country varchar(255) DEFAULT NULL,
          bank_account_number varchar(64) DEFAULT NULL,
          bank_account_country_code varchar(2) DEFAULT NULL,
          role varchar(32) NOT NULL,
          is_active tinyint(1) NOT NULL,
          created_at datetime NOT NULL,
          created_by_user_id char(36) DEFAULT NULL,
          updated_at datetime DEFAULT NULL,
          updated_by_user_id char(36) DEFAULT NULL,
          phone_number varchar(20) DEFAULT NULL,
          email varchar(64) DEFAULT NULL,

          PRIMARY KEY (id),
          UNIQUE KEY uq_companies_org_tax (organization_id, tax_number),
          KEY idx_companies_org_role (organization_id, role),
          KEY idx_companies_org_name (organization_id, name)
        ) ENGINE=InnoDB
          DEFAULT CHARSET=utf8mb4
          COLLATE=utf8mb4_0900_ai_ci
        """
    )
    op.execute(
        """
        CREATE TABLE contracts
        (
            id                 char(36)     NOT NULL,
            organization_id    char(36)              DEFAULT NULL,
            code               varchar(64)  NOT NULL,
            name               varchar(255) NOT NULL,
            description        text,
            owner_id           char(36)     NOT NULL,
            client_id          char(36)              DEFAULT NULL,
            start_date         date                  DEFAULT NULL,
            end_date           date                  DEFAULT NULL,
            budget             decimal(14, 2)        DEFAULT NULL,
            path               varchar(512) NOT NULL,
            status             varchar(32)  NOT NULL,
            created_at         datetime              DEFAULT NULL,
            created_by_user_id char(36)              DEFAULT NULL,
            updated_at         datetime              DEFAULT NULL,
            updated_by_user_id char(36)              DEFAULT NULL,
            contract_type      varchar(20)  NOT NULL DEFAULT 'project',
            parent_project_id  char(34)              DEFAULT NULL,

            PRIMARY KEY (id),

            UNIQUE KEY uk_contract_org_code (organization_id, code),

            KEY fk_contract_owner (owner_id),
            KEY fk_contract_client (client_id),
            KEY idx_contracts_organization (organization_id),
            KEY idx_contracts_parent_project_id (parent_project_id),

            CONSTRAINT fk_contract_client
                FOREIGN KEY (client_id)
                    REFERENCES companies (id),

            CONSTRAINT fk_contract_owner
                FOREIGN KEY (owner_id)
                    REFERENCES companies (id)
        ) ENGINE = InnoDB
          DEFAULT CHARSET = utf8mb4
          COLLATE = utf8mb4_0900_ai_ci
        """
    )
    op.execute(
        """
        CREATE TABLE contract_nodes
        (
            id                 char(36)     NOT NULL,
            organization_id    char(36)          DEFAULT NULL,
            contract_id        char(36)     NOT NULL,
            parent_id          char(36)          DEFAULT NULL,
            code               varchar(64)  NOT NULL,
            name               varchar(255) NOT NULL,
            budget             decimal(15, 2)    DEFAULT NULL,
            quantity           decimal(15, 4)    DEFAULT NULL,
            unit               varchar(32)       DEFAULT NULL,
            created_at         timestamp    NULL DEFAULT NULL,
            created_by_user_id char(36)          DEFAULT NULL,
            updated_at         timestamp    NULL DEFAULT NULL,
            updated_by_user_id char(36)          DEFAULT NULL,
            is_active          tinyint(1)        DEFAULT NULL,

            PRIMARY KEY (id),

            UNIQUE KEY uq_contract_code (contract_id, code),

            KEY fk_cost_nodes_parent (parent_id),
            KEY idx_contract_nodes_org_contract (organization_id, contract_id),
            KEY idx_contract_nodes_org_parent (organization_id, parent_id),

            CONSTRAINT fk_cost_nodes_contract
                FOREIGN KEY (contract_id)
                    REFERENCES contracts (id)
                    ON DELETE CASCADE,

            CONSTRAINT fk_cost_nodes_parent
                FOREIGN KEY (parent_id)
                    REFERENCES contract_nodes (id)
                    ON DELETE CASCADE
        ) ENGINE = InnoDB
          DEFAULT CHARSET = utf8mb4
          COLLATE = utf8mb4_0900_ai_ci
        """
    )
    op.execute(
        """
        CREATE TABLE contract_node_progress (
          id char(36) NOT NULL,
          organization_id char(36) DEFAULT NULL,
          contract_node_id char(36) NOT NULL,
          progress_date date NOT NULL,
          progress decimal(5,4) NOT NULL,
          created_at timestamp NOT NULL,
          created_by_user_id char(36) DEFAULT NULL,
          updated_at timestamp NULL DEFAULT NULL,
          updated_by_user_id char(36) DEFAULT NULL,

          PRIMARY KEY (id),

          UNIQUE KEY uq_contract_node_progress
              (contract_node_id, progress_date),

          KEY idx_contract_node_progress_node (contract_node_id),
          KEY idx_contract_node_progress_node_date
              (contract_node_id, progress_date),
          KEY idx_contract_node_progress_org_node
              (organization_id, contract_node_id),

          CONSTRAINT fk_contract_node_progress_node
              FOREIGN KEY (contract_node_id)
              REFERENCES contract_nodes (id)
              ON DELETE CASCADE
        ) ENGINE=InnoDB
          DEFAULT CHARSET=utf8mb4
          COLLATE=utf8mb4_0900_ai_ci
        """
    )
    op.execute(
        """
        CREATE TABLE contract_snapshots
        (
            id                 char(36) NOT NULL,
            organization_id    char(36) DEFAULT NULL,
            contract_id        char(36) NOT NULL,
            snapshot_date      date     NOT NULL,
            created_at         datetime NOT NULL,
            created_by_user_id char(36) DEFAULT NULL,
            updated_at         datetime DEFAULT NULL,
            updated_by_user_id char(36) DEFAULT NULL,

            PRIMARY KEY (id),

            KEY idx_contract_snapshots_contract_date
                (contract_id, snapshot_date),

            KEY idx_contract_snapshots_org_contract_date
                (organization_id, contract_id, snapshot_date),

            CONSTRAINT fk_contract_snapshots_contract
                FOREIGN KEY (contract_id)
                    REFERENCES contracts (id)
                    ON DELETE CASCADE
        ) ENGINE = InnoDB
          DEFAULT CHARSET = utf8mb4
          COLLATE = utf8mb4_0900_ai_ci
        """
    )
    op.execute(
        """
        CREATE TABLE contract_node_snapshots
        (
            id               char(36)       NOT NULL,
            snapshot_id      char(36)       NOT NULL,
            contract_node_id char(36)       NOT NULL,
            planned_budget   decimal(18, 2) NOT NULL,
            progress         decimal(5, 4)  NOT NULL,

            PRIMARY KEY (id),

            UNIQUE KEY uq_snapshot_node
                (snapshot_id, contract_node_id),

            KEY idx_node_snapshots_node (contract_node_id),
            KEY idx_node_snapshots_snapshot (snapshot_id),

            CONSTRAINT fk_node_snapshots_node
                FOREIGN KEY (contract_node_id)
                    REFERENCES contract_nodes (id)
                    ON DELETE CASCADE,

            CONSTRAINT fk_node_snapshots_snapshot
                FOREIGN KEY (snapshot_id)
                    REFERENCES contract_snapshots (id)
                    ON DELETE CASCADE
        ) ENGINE = InnoDB
          DEFAULT CHARSET = utf8mb4
          COLLATE = utf8mb4_0900_ai_ci
        """
    )
    op.execute(
        """
        CREATE TABLE contract_node_value_snapshots (
          id char(36) NOT NULL,
          node_snapshot_id char(36) NOT NULL,
          value_type_id char(36) NOT NULL,
          net decimal(18,2) NOT NULL,
          vat decimal(18,2) NOT NULL,
          gross decimal(18,2) NOT NULL,
          non_deductible decimal(18,2) NOT NULL,

          PRIMARY KEY (id),

          UNIQUE KEY uq_node_snapshot_value_type
              (node_snapshot_id, value_type_id),

          KEY idx_value_snapshots_value_type (value_type_id),

          CONSTRAINT fk_value_snapshots_node_snapshot
              FOREIGN KEY (node_snapshot_id)
              REFERENCES contract_node_snapshots (id)
              ON DELETE CASCADE,

          CONSTRAINT fk_value_snapshots_value_type
              FOREIGN KEY (value_type_id)
              REFERENCES value_types (id)
        ) ENGINE=InnoDB
          DEFAULT CHARSET=utf8mb4
          COLLATE=utf8mb4_0900_ai_ci
        """
    )
    op.execute(
        """
        CREATE TABLE financial_records
        (
            id                 char(36)     NOT NULL,
            organization_id    char(36)     NOT NULL,
            reference          varchar(128) NOT NULL,
            invoice_date       date         DEFAULT NULL,
            selling_date       date         DEFAULT NULL,
            buyer_id           char(36)     DEFAULT NULL,
            seller_id          char(36)     DEFAULT NULL,
            payment_method     varchar(32)  DEFAULT NULL,
            due_date           date         DEFAULT NULL,
            payment_status     varchar(32)  DEFAULT NULL,
            status             varchar(32)  NOT NULL,
            timestamp          datetime     DEFAULT NULL,
            created_at         datetime     NOT NULL,
            created_by_user_id char(36)     DEFAULT NULL,
            updated_at         datetime     DEFAULT NULL,
            updated_by_user_id char(36)     DEFAULT NULL,
            scan_filename      varchar(255) DEFAULT NULL,
            tags               json         DEFAULT NULL,
            paid_date          date         DEFAULT NULL,

            PRIMARY KEY (id),

            KEY fk_invoice_buyer (buyer_id),
            KEY fk_invoice_seller (seller_id),
            KEY idx_financial_records_org (organization_id),
            KEY idx_fr_org_status_invoice_ts
                (organization_id, status, invoice_date DESC, timestamp DESC),
            KEY idx_fr_org_payment_due_ts
                (organization_id, payment_status, due_date, timestamp),
            KEY idx_fr_org_invoice_date
                (organization_id, invoice_date),

            CONSTRAINT fk_invoice_buyer
                FOREIGN KEY (buyer_id)
                    REFERENCES companies (id)
                    ON DELETE SET NULL
                    ON UPDATE CASCADE,

            CONSTRAINT fk_invoice_seller
                FOREIGN KEY (seller_id)
                    REFERENCES companies (id)
                    ON DELETE SET NULL
                    ON UPDATE CASCADE
        ) ENGINE = InnoDB
          DEFAULT CHARSET = utf8mb4
          COLLATE = utf8mb4_0900_ai_ci
        """
    )
    op.execute(
        """
        CREATE TABLE financial_record_lines (
          id char(36) NOT NULL,
          organization_id char(36) DEFAULT NULL,
          financial_record_id char(36) DEFAULT NULL,
          contract_id char(36) DEFAULT NULL,
          contract_node_id char(36) DEFAULT NULL,
          value_type_id char(36) DEFAULT NULL,
          item_name varchar(255) NOT NULL,
          quantity decimal(15,4) DEFAULT NULL,
          unit varchar(32) DEFAULT NULL,
          amount_value decimal(15,2) NOT NULL,
          vat_rate varchar(16) NOT NULL,
          tax_treatment varchar(32) NOT NULL,
          description text,
          created_at datetime DEFAULT NULL,
          created_by_user_id char(36) DEFAULT NULL,
          updated_at datetime DEFAULT NULL,
          updated_by_user_id char(36) DEFAULT NULL,
          agreement_id char(34) DEFAULT NULL,
          agreement_node_id char(34) DEFAULT NULL,

          PRIMARY KEY (id),

          KEY fk_fin_record_line_contract_node (contract_node_id),
          KEY fk_fin_record_line_value_type (value_type_id),
          KEY idx_frl_agreement_id (agreement_id),
          KEY idx_frl_agreement_node_id (agreement_node_id),
          KEY idx_frl_contract_record (contract_id, financial_record_id),
          KEY idx_frl_record_contract (financial_record_id, contract_id),
          KEY idx_frl_org_contract_record
              (organization_id, contract_id, financial_record_id),

          CONSTRAINT fk_fin_record_line_contract_node
              FOREIGN KEY (contract_node_id)
              REFERENCES contract_nodes (id)
              ON DELETE SET NULL,

          CONSTRAINT fk_fin_record_line_value_type
              FOREIGN KEY (value_type_id)
              REFERENCES value_types (id)
              ON DELETE SET NULL,

          CONSTRAINT fk_invoice_line_contract
              FOREIGN KEY (contract_id)
              REFERENCES contracts (id)
              ON DELETE SET NULL,

          CONSTRAINT fk_invoice_line_invoice
              FOREIGN KEY (financial_record_id)
              REFERENCES financial_records (id)
              ON DELETE SET NULL
        ) ENGINE=InnoDB
          DEFAULT CHARSET=utf8mb4
          COLLATE=utf8mb4_0900_ai_ci
        """
    )
    op.execute(
        """
        CREATE TABLE documents
        (
            id                  char(36)     NOT NULL,
            organization_id     char(36)     NOT NULL,
            financial_record_id char(36)              DEFAULT NULL,
            document_source     varchar(32)  NOT NULL,
            document_type       varchar(32)           DEFAULT NULL,
            filename            varchar(255) NOT NULL,
            mime_type           varchar(128)          DEFAULT NULL,
            size                bigint                DEFAULT NULL,
            created_at          datetime     NOT NULL,
            created_by_user_id  char(36)              DEFAULT NULL,
            updated_at          datetime              DEFAULT NULL,
            updated_by_user_id  char(36)              DEFAULT NULL,
            document_number     varchar(128)          DEFAULT NULL,
            seller_nip          varchar(32)           DEFAULT NULL,
            parsed_payload      json                  DEFAULT NULL,
            file_hash           char(64)     NOT NULL,
            file_path           varchar(512) NOT NULL,
            document_status     varchar(32)  NOT NULL DEFAULT 'NEW',

            PRIMARY KEY (id),

            KEY idx_documents_record (financial_record_id),
            KEY idx_documents_org (organization_id),
            KEY idx_documents_hash (organization_id, file_hash),
            KEY idx_documents_business_lookup
                (organization_id, seller_nip, document_number),

            CONSTRAINT fk_documents_org
                FOREIGN KEY (organization_id)
                    REFERENCES organizations (id)
                    ON DELETE CASCADE,

            CONSTRAINT fk_documents_record
                FOREIGN KEY (financial_record_id)
                    REFERENCES financial_records (id)
                    ON DELETE SET NULL
        ) ENGINE = InnoDB
          DEFAULT CHARSET = utf8mb4
          COLLATE = utf8mb4_0900_ai_ci
        """
    )
    op.execute(
        """
        CREATE TABLE number_sequences
        (
            id              bigint unsigned NOT NULL AUTO_INCREMENT,
            organization_id char(36)        NOT NULL,
            scope_key       varchar(100)    NOT NULL,
            current_value   bigint unsigned NOT NULL,
            created_at      datetime(6)     NOT NULL
                DEFAULT CURRENT_TIMESTAMP(6),
            updated_at      datetime(6)     NOT NULL
                DEFAULT CURRENT_TIMESTAMP(6)
                ON UPDATE CURRENT_TIMESTAMP(6),

            PRIMARY KEY (id),

            UNIQUE KEY uq_number_sequences_org_scope
                (organization_id, scope_key),

            KEY idx_number_sequences_org (organization_id)
        ) ENGINE = InnoDB
          DEFAULT CHARSET = utf8mb4
          COLLATE = utf8mb4_0900_ai_ci
        """
    )
    op.execute(
        """
        CREATE TABLE value_types
        (
            id                 char(36)     NOT NULL,
            organization_id    char(36)              DEFAULT NULL,
            code               varchar(32)  NOT NULL,
            name               varchar(255) NOT NULL,
            description        text,
            is_active          tinyint(1)   NOT NULL DEFAULT '1',
            direction          varchar(10)  NOT NULL DEFAULT 'COST',
            created_at         timestamp    NULL     DEFAULT NULL,
            created_by_user_id char(36)              DEFAULT NULL,
            updated_at         timestamp    NULL     DEFAULT NULL,
            updated_by_user_id char(36)              DEFAULT NULL,

            PRIMARY KEY (id),

            UNIQUE KEY uq_value_types_org_code
                (organization_id, code),

            KEY idx_value_types_org (organization_id),
            KEY idx_value_types_org_active
                (organization_id, is_active),

            CONSTRAINT chk_value_types_direction
                CHECK (
                    direction IN ('COST', 'REVENUE', 'INTERNAL')
                    )
        ) ENGINE = InnoDB
          DEFAULT CHARSET = utf8mb4
          COLLATE = utf8mb4_0900_ai_ci
        """
    )
    op.execute(
        """
        CREATE TABLE users
        (
            id                 char(36)     NOT NULL,
            login              varchar(255) NOT NULL,
            email              varchar(255)          DEFAULT NULL,
            full_name          varchar(255)          DEFAULT NULL,
            is_active          tinyint(1)   NOT NULL DEFAULT '1',
            created_at         datetime     NOT NULL,
            created_by_user_id char(36)              DEFAULT NULL,
            updated_at         datetime              DEFAULT NULL,
            updated_by_user_id char(36)              DEFAULT NULL,
            password_hash      varchar(255)          DEFAULT NULL,
            last_login_at      datetime              DEFAULT NULL,

            PRIMARY KEY (id),

            UNIQUE KEY uq_users_login (login)
        ) ENGINE = InnoDB
          DEFAULT CHARSET = utf8mb4
          COLLATE = utf8mb4_0900_ai_ci
        """
    )
    op.execute(
        """
        CREATE TABLE organizations
        (
            id                 char(36)     NOT NULL,
            code               varchar(50)  NOT NULL,
            name               varchar(255) NOT NULL,
            is_active          tinyint(1)   NOT NULL DEFAULT '1',
            created_at         datetime     NOT NULL,
            created_by_user_id char(36)              DEFAULT NULL,
            updated_at         datetime              DEFAULT NULL,
            updated_by_user_id char(36)              DEFAULT NULL,
            settings           json                  DEFAULT NULL,

            PRIMARY KEY (id),

            UNIQUE KEY uq_organizations_code (code),
            UNIQUE KEY ux_organizations_code (code)
        ) ENGINE = InnoDB
          DEFAULT CHARSET = utf8mb4
          COLLATE = utf8mb4_0900_ai_ci
        """
    )

    op.execute(
        """
        CREATE TABLE organization_users
        (
            id                 char(36)    NOT NULL,
            organization_id    char(36)    NOT NULL,
            user_id            char(36)    NOT NULL,
            role               varchar(30) NOT NULL,
            is_active          tinyint(1)  NOT NULL DEFAULT '1',
            created_at         datetime    NOT NULL,
            created_by_user_id char(36)             DEFAULT NULL,
            updated_at         datetime             DEFAULT NULL,
            updated_by_user_id char(36)             DEFAULT NULL,
            invited_at         datetime             DEFAULT NULL,
            invited_by_user_id char(36)             DEFAULT NULL,
            accepted_at        datetime             DEFAULT NULL,

            PRIMARY KEY (id),

            UNIQUE KEY uq_org_user (organization_id, user_id),

            KEY fk_ou_user (user_id),

            CONSTRAINT fk_ou_org
                FOREIGN KEY (organization_id)
                    REFERENCES organizations (id),

            CONSTRAINT fk_ou_user
                FOREIGN KEY (user_id)
                    REFERENCES users (id)
        ) ENGINE = InnoDB
          DEFAULT CHARSET = utf8mb4
          COLLATE = utf8mb4_0900_ai_ci
        """
    )
    op.execute(
        """
        CREATE TABLE sessions (
          id varchar(36) NOT NULL,
          user_id varchar(36) NOT NULL,
          organization_id varchar(36) DEFAULT NULL,
          created_at datetime NOT NULL,
          expires_at datetime NOT NULL,

          PRIMARY KEY (id)
        ) ENGINE=InnoDB
          DEFAULT CHARSET=utf8mb4
          COLLATE=utf8mb4_0900_ai_ci
        """
    )

def downgrade() -> None:
    op.execute("DROP TABLE companies")
    op.execute("DROP TABLE contracts")
    op.execute("DROP TABLE contract_nodes")
    op.execute("DROP TABLE contract_node_progress")
    op.execute("DROP TABLE contract_snapshots")
    op.execute("DROP TABLE contract_node_snapshots")
    op.execute("DROP TABLE contract_node_value_snapshots")
    op.execute("DROP TABLE financial_records")
    op.execute("DROP TABLE financial_record_lines")
    op.execute("DROP TABLE documents")
    op.execute("DROP TABLE number_sequences")
    op.execute("DROP TABLE value_types")
    op.execute("DROP TABLE users")
    op.execute("DROP TABLE organizations")
    op.execute("DROP TABLE organization_users")
    op.execute("DROP TABLE sessions")