from contract_costs.common.ids import new_uuid
from contract_costs.services.companies.providers.candidate_provider import CompanyCandidateProvider
from contract_costs.services.companies.providers.composite import CompositeCompanyCandidateProvider

from tests.builders.company_builder import CompanyBuilder


class FakeProvider(CompanyCandidateProvider):
    def __init__(self, companies):
        self._companies = companies

    def find_candidates(self, *, organization_id, input_):
        return self._companies


def test_merges_results_from_multiple_providers():
    org_id = new_uuid()

    c1 = CompanyBuilder().with_organization_id(org_id).build()
    c2 = CompanyBuilder().with_organization_id(org_id).build()

    p1 = FakeProvider([c1])
    p2 = FakeProvider([c2])

    composite = CompositeCompanyCandidateProvider([p1, p2])

    result = composite.find_candidates(
        organization_id=org_id,
        input_=None,
    )

    assert len(result) == 2


def test_deduplicates_by_id():
    org_id = new_uuid()

    c1 = CompanyBuilder().with_organization_id(org_id).build()

    p1 = FakeProvider([c1])
    p2 = FakeProvider([c1])  # ten sam obiekt

    composite = CompositeCompanyCandidateProvider([p1, p2])

    result = composite.find_candidates(
        organization_id=org_id,
        input_=None,
    )

    assert len(result) == 1
