# from dataclasses import dataclass
# from pathlib import Path
#
# from contract_costs.action_bus.action_type import ActionType, action_type
# from contract_costs.action_bus.command import Command
# from contract_costs.services.documents.prepare.dto.prepare_document_bundle import PrepareDocumentsBundle
#
#
# @dataclass(frozen=True, slots=True)
# @action_type(ActionType.DOCUMENT_MANAGEMENT)
# class DocumentPrepareExcelExportCommand(Command):
#     output_path: Path
#     bundle: PrepareDocumentsBundle
