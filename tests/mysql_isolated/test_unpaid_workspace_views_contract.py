"""Kafelki „niezapłacone”: każdy nierozliczony status (UNPAID, PARTIALLY_PAID, UNKNOWN) + widok INTERNAL."""
from datetime import date

import pytest

from contract_costs.common.ids import new_uuid
from contract_costs.model.company import CompanyType
from contract_costs.model.financial_record import FinancialRecordStatus, PaymentStatus
from contract_costs.model.record_workspace_view import RecordWorkspaceView
from contract_costs.model.value_direction import ValueDirection
from contract_costs.repository.mysql.company_repository import MySQLCompanyRepository
from contract_costs.repository.mysql.financial_record_line_repository import MySQLFinancialRecordLineRepository
from contract_costs.repository.mysql.financial_record_repository import MySQLFinancialRecordRepository
from contract_costs.repository.mysql.value_type_repository import MySQLValueTypeRepository
from contract_costs.services.financial_records.review.workspace_query_factory import RecordWorkspaceQueryFactory
from tests.builders.company_builder import CompanyBuilder
from tests.builders.financial_record_builder import FinancialRecordBuilder
from tests.builders.financial_record_line_builder import FinancialRecordLineBuilder
from tests.builders.value_type_builder import ValueTypeBuilder


# Tylko MySQL: filtr kierunku (vt.direction / role firm) jest w SQL, in-memory go nie ma.
@pytest.fixture(params=["mysql"], ids=["mysql"])
def env(request):
    conn = request.getfixturevalue("mysql_contract_connection")
    org_id = new_uuid()

    companies = MySQLCompanyRepository(connection=conn)
    own_a = CompanyBuilder().with_organization_id(org_id).with_tax_number("1111111111").with_role(CompanyType.OWN).build()
    own_b = CompanyBuilder().with_organization_id(org_id).with_tax_number("2222222222").with_role(CompanyType.OWN).build()
    external = CompanyBuilder().with_organization_id(org_id).with_tax_number("3333333333").with_role(CompanyType.SUPPLIER).build()
    for c in (own_a, own_b, external):
        companies.add(c)

    value_types = MySQLValueTypeRepository(connection=conn)
    vts = {}
    for direction in (ValueDirection.COST, ValueDirection.REVENUE, ValueDirection.INTERNAL):
        vt = ValueTypeBuilder().with_organization_id(org_id).with_code(direction.value).with_direction(direction).build()
        value_types.add(vt)
        vts[direction] = vt

    return {
        "org_id": org_id,
        "records": MySQLFinancialRecordRepository(connection=conn),
        "lines": MySQLFinancialRecordLineRepository(connection=conn),
        "own_a": own_a, "own_b": own_b, "external": external,
        "vts": vts,
    }


def _add(env, *, buyer, seller, direction, payment_status):
    record = (
        FinancialRecordBuilder()
        .with_organization_id(env["org_id"])
        .with_buyer_id(buyer.id)
        .with_seller_id(seller.id)
        .with_invoice_date(date(2026, 5, 1))
        .with_status(FinancialRecordStatus.PROCESSED)
        .with_payment_status(payment_status)
        .build()
    )
    env["records"].add(record)
    env["lines"].add(
        organization_id=env["org_id"],
        line=(
            FinancialRecordLineBuilder()
            .with_organization_id(env["org_id"])
            .with_financial_record_id(record.id)
            .with_value_type_id(env["vts"][direction].id)
            .build()
        ),
    )


def _count(env, view):
    query = RecordWorkspaceQueryFactory.build(
        organization_id=env["org_id"], actor_user_id=new_uuid(), view=view,
    )
    return env["records"].count_for_review(organization_id=env["org_id"], query=query)


def test_unpaid_views_include_partially_paid_and_unknown(env):
    for status in (PaymentStatus.UNPAID, PaymentStatus.PARTIALLY_PAID, PaymentStatus.UNKNOWN, PaymentStatus.PAID):
        _add(env, buyer=env["own_a"], seller=env["external"], direction=ValueDirection.COST, payment_status=status)
        _add(env, buyer=env["external"], seller=env["own_a"], direction=ValueDirection.REVENUE, payment_status=status)

    assert _count(env, RecordWorkspaceView.UNPAID_COSTS) == 3
    assert _count(env, RecordWorkspaceView.UNPAID_REVENUE) == 3
    assert _count(env, RecordWorkspaceView.UNPAID_INTERNAL) == 0


def test_unpaid_internal_view_lists_only_internal_documents(env):
    _add(env, buyer=env["own_a"], seller=env["own_b"], direction=ValueDirection.INTERNAL, payment_status=PaymentStatus.UNPAID)
    _add(env, buyer=env["own_b"], seller=env["own_a"], direction=ValueDirection.INTERNAL, payment_status=PaymentStatus.PARTIALLY_PAID)
    _add(env, buyer=env["own_a"], seller=env["own_b"], direction=ValueDirection.INTERNAL, payment_status=PaymentStatus.PAID)
    _add(env, buyer=env["own_a"], seller=env["external"], direction=ValueDirection.COST, payment_status=PaymentStatus.UNPAID)

    assert _count(env, RecordWorkspaceView.UNPAID_INTERNAL) == 2
    assert _count(env, RecordWorkspaceView.UNPAID_COSTS) == 1
