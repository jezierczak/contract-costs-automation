from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.utils.context_helpers import require_organization_id
from contract_costs.common.context.exceptions import ContextError
from contract_costs.services.documents.scoring.document_decision_service import DocumentDecisionService
from contract_costs.services.documents.scoring.find_matching_record_service import FindMatchingRecordService
from contract_costs.services.financial_records.assigment.invoice_sources.normalization.invoice_parser_normalizer import (
    DocumentParseNormalizer,
)


def build_show_document_matches(subparsers):
    p = subparsers.add_parser(
        "document-matches",
        help="Show matching records (with reasons) and the automatic decision for unattached documents",
    )
    p.add_argument("--last", type=int, help="Only the last N documents")
    p.set_defaults(handler=handle_show_document_matches)


REGISTRY.register_group("show", build_show_document_matches)


def _company_label(company, tax_number) -> str:
    if company is not None:
        return f"{company.name} ({company.tax_number})"
    return f"NIEZNANY ({tax_number or 'brak NIP'})"


def handle_show_document_matches(args) -> None:
    services = get_services()
    try:
        organization_id = require_organization_id(services.context)
    except ContextError:
        return

    matching = FindMatchingRecordService(document_parse_normalizer=DocumentParseNormalizer())
    decisions = DocumentDecisionService(matching_service=matching)

    with services._factory.unit_of_work() as uow:
        documents = uow.documents.list_filtered(
            organization_id=organization_id,
            has_payload=True,
            has_record=False,
        )
        if args.last:
            documents = documents[-args.last:]

        for document in documents:
            result = matching.find(document=document, uow=uow)
            decision = decisions.decide(document=document, uow=uow)
            score = document.scoring.score if document.scoring else "-"
            source = document.document_source.value if document.document_source else "-"

            print(f"{document.document_number or '—'}  [{source}, score {score}]  → {decision.decision.value}")
            print(f"    sprzedawca: {_company_label(result.seller, result.seller_tax_number)}")
            print(f"    nabywca:    {_company_label(result.buyer, result.buyer_tax_number)}")
            for match in result.matches:
                reasons = ", ".join(sorted(r.value for r in match.reasons))
                print(f"    - {match.record.reference:<30} {str(match.record.invoice_date or '—'):<10} {reasons}")

        print(f"----- Dokumentów bez rekordu: {len(documents)} -----")
