"""Regresja #1: agregaty firm nie mogą liczyć rekordów ze statusem DELETED."""
from datetime import date
from decimal import Decimal

import pytest

from contract_costs.common.ids import new_uuid
from contract_costs.model.amount import Amount, AmountInputType, TaxTreatment, VatRate
from contract_costs.model.financial_record import FinancialRecordStatus
from contract_costs.model.value_direction import ValueDirection
from contract_costs.repository.mysql.company_dashboard.company_dashboard_repository import (
    MySQLCompanyDashboardRepository,
)
from contract_costs.repository.mysql.financial_record_line_repository import MySQLFinancialRecordLineRepository
from contract_costs.repository.mysql.financial_record_repository import MySQLFinancialRecordRepository
from contract_costs.repository.mysql.value_type_repository import MySQLValueTypeRepository
from tests.builders.financial_record_builder import FinancialRecordBuilder
from tests.builders.financial_record_line_builder import FinancialRecordLineBuilder
from tests.builders.value_type_builder import ValueTypeBuilder

YEAR = 2026


# Tylko MySQL: widok financial_ledger nie ma odpowiednika in-memory.
# Parametryzacja jest potrzebna, żeby zadziałał autouse cleanup z conftest.
@pytest.fixture(params=["mysql"], ids=["mysql"])
def ledger_env(request):
    conn = request.getfixturevalue("mysql_contract_connection")
    return {
        "dashboard": MySQLCompanyDashboardRepository(connection=conn),
        "records": MySQLFinancialRecordRepository(connection=conn),
        "lines": MySQLFinancialRecordLineRepository(connection=conn),
        "value_types": MySQLValueTypeRepository(connection=conn),
    }


def _add_cost_record(env, *, org_id, value_type_id, buyer_id, seller_id, value, status):
    record = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_buyer_id(buyer_id)
        .with_seller_id(seller_id)
        .with_invoice_date(date(YEAR, 3, 10))
        .with_selling_date(date(YEAR, 3, 10))
        .with_status(status)
        .build()
    )
    env["records"].add(record)

    line = (
        FinancialRecordLineBuilder()
        .with_organization_id(org_id)
        .with_financial_record_id(record.id)
        .with_value_type_id(value_type_id)
        .with_amount(
            Amount(
                value=value,
                input_type=AmountInputType.NET,
                vat_rate=VatRate.VAT_23,
                tax_treatment=TaxTreatment.TAX_DEDUCTIBLE,
            )
        )
        .build()
    )
    env["lines"].add(organization_id=org_id, line=line)
    return record


@pytest.fixture
def seeded(ledger_env):
    org_id = new_uuid()
    company_id = new_uuid()
    supplier_id = new_uuid()

    value_type = (
        ValueTypeBuilder()
        .with_organization_id(org_id)
        .with_direction(ValueDirection.COST)
        .build()
    )
    ledger_env["value_types"].add(value_type)

    active = _add_cost_record(
        ledger_env,
        org_id=org_id,
        value_type_id=value_type.id,
        buyer_id=company_id,
        seller_id=supplier_id,
        value=Decimal("100.00"),
        status=FinancialRecordStatus.PROCESSED,
    )
    _add_cost_record(
        ledger_env,
        org_id=org_id,
        value_type_id=value_type.id,
        buyer_id=company_id,
        seller_id=supplier_id,
        value=Decimal("999.00"),
        status=FinancialRecordStatus.DELETED,
    )

    return {
        "dashboard": ledger_env["dashboard"],
        "org_id": org_id,
        "company_id": company_id,
        "supplier_id": supplier_id,
        "active_record_id": active.id,
    }


def test_dashboard_data_excludes_deleted_records(seeded):
    data = seeded["dashboard"].fetch_dashboard_data(
        organization_id=seeded["org_id"],
        company_id=seeded["company_id"],
        year=YEAR,
    )

    assert data.year_costs == Decimal("100.00")
    assert [m.costs for m in data.months] == [Decimal("100.00")]


def test_month_breakdown_excludes_deleted_records(seeded):
    rows = seeded["dashboard"].fetch_month_breakdown(
        organization_id=seeded["org_id"],
        company_id=seeded["company_id"],
        year=YEAR,
        month=3,
    )

    assert sum(r.costs for r in rows) == Decimal("100.00")


def test_counterparty_lines_exclude_deleted_records(seeded):
    lines = seeded["dashboard"].fetch_counterparty_lines(
        organization_id=seeded["org_id"],
        counterparty_id=seeded["supplier_id"],
        owner_company_id=seeded["company_id"],
    )

    assert [str(line.record_id) for line in lines] == [str(seeded["active_record_id"])]
