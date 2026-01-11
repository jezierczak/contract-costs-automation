from contract_costs.services.companies.query.dto.company_dto import CompanyDTO


class CompanyTablePrinter:
    HEADERS = [
        "Q",
        "Name",
        "NIP",
        "Role",
        # "Status",
        "City",
        # "Street",
        "Bank Account",
        "Phone Number",
        "Email Address",
    ]

    @classmethod
    def print(cls, companies: list[CompanyDTO]) -> None:
        rows = [cls._row(c) for c in companies]
        cls._print_table(rows)

    # =====================
    # ROW MAPPING
    # =====================
    @staticmethod
    def _row(c: CompanyDTO) -> list[str]:
        return [
            str(c.quality_score) if c.quality_score is not None else "-",
            c.name,
            c.tax_number,
            c.role.value,
            # "ACTIVE" if c.is_active else "INACTIVE",
            c.address_city or "-",
            # c.address_street or "-",
            c.bank_account_number or "-",
            c.phone_number or "-",
            c.email or "-"
        ]

    # =====================
    # TABLE RENDER
    # =====================
    @classmethod
    def _print_table(cls, rows: list[list[str]]) -> None:
        widths = cls._column_widths([cls.HEADERS] + rows)

        cls._print_line(cls.HEADERS, widths)
        cls._print_separator(widths)

        for row in rows:
            cls._print_line(row, widths)

    @staticmethod
    def _column_widths(rows: list[list[str]]) -> list[int]:
        return [
            max(len(str(row[i])) for row in rows)
            for i in range(len(rows[0]))
        ]

    @staticmethod
    def _print_line(values: list[str], widths: list[int]) -> None:
        line = " | ".join(
            value.ljust(width)
            for value, width in zip(values, widths)
        )
        print(line)

    @staticmethod
    def _print_separator(widths: list[int]) -> None:
        sep = "-+-".join("-" * w for w in widths)
        print(sep)
