class CostNodeStructureValidator:

    @staticmethod
    def validate(rows: list[dict]) -> None:
        codes = [row["code"] for row in rows]

        # unique codes
        if len(codes) != len(set(codes)):
            raise ValueError("Duplicate cost node codes found")

        # parents exist
        code_set = set(codes)
        for row in rows:
            parent = row.get("parent_code")
            if parent and parent not in code_set:
                raise ValueError(
                    f"Parent code '{parent}' does not exist for node '{row['code']}'"
                )

        # single root
        roots = [row for row in rows if not row.get("parent_code")]
        if len(roots) != 1:
            raise ValueError("Exactly one root cost node is required")

        #  cycle detection
        CostNodeStructureValidator._check_cycles(rows)

    @staticmethod
    def _check_cycles(rows: list[dict]) -> None:
        graph = {row["code"]: row.get("parent_code") for row in rows}

        for code in graph:
            visited = set()
            current = code
            while current:
                if current in visited:
                    raise ValueError(f"Cycle detected at node '{code}'")
                visited.add(current)
                current = graph.get(current)
