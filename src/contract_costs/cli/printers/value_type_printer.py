from contract_costs.services.value_types.query.dto.value_type_dto import ValueTypeDTO


class ValueTypePrinter:

    @staticmethod
    def print(items: list[ValueTypeDTO]) -> None:
        if not items:
            print("No value types found.")
            return
        # =====================
        # HEADER
        # =====================
        header = f"[{'CODE':^12}] {'NAME':<40} DESCRIPTION"
        print(header)
        print("-" * len(header))
        # =====================
        # ROWS
        # =====================
        items = sorted(items, key=lambda x: (not x.is_active, x.code))
        for ct in items:
            line = f"[{ct.code:^12}] {ct.name:<40} {ct.description}"

            if not ct.is_active:
                line += "  (inactive)"

            print(line)
