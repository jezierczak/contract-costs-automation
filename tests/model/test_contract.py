from contract_costs.model.contract import Contract


class TestContract:

    def test_contract_from_contract_starter(self,contract_starter_1) -> None:

        contract = Contract.from_contract_starter(contract_starter_1)

        # --- identyfikacja ---
        assert contract.id is not None

        # --- podstawowe pola ---
        assert contract.name == contract_starter_1["name"]
        assert contract.description == contract_starter_1["description"]
        assert contract.budget == contract_starter_1["budget"]
        assert contract.status == contract_starter_1["status"]

        # --- daty ---
        assert contract.start_date == contract_starter_1["start_date"]
        assert contract.end_date == contract_starter_1["end_date"]

        # --- relacje ---
        assert contract.owner == contract_starter_1["contract_owner"]
        assert contract.client == contract_starter_1["client"]

        # --- ścieżka ---
        assert contract.path == contract_starter_1["path"]

        assert contract.status == contract_starter_1["status"]
