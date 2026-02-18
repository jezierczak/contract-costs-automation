import re
from pathlib import Path
from collections import defaultdict

INPUT_FILE = "deleted_items.txt"
OUTPUT_FILE = "recovery_fin_record_lines.sql"

# 🔥 DOPASUJ DO SWOJEJ STRUKTURY
TABLE_COLUMNS = {
    "financial_record_lines": [
        "contract_id",
        "contract_node_id",
        "value_type_id",
        "item_name",
        "quantity",
        "unit",
        "amount_value",
        "vat_rate",
        "tax_treatment",
        "description",
        "created_at",
        "created_by_user_id",
        "updated_at",
        "updated_by_user_id",
    ],
    # "contract_node_value_snapshots": [
    #     "snapshot_id",
    #     "contract_node_id",
    #     "contract_id",
    #     "net",
    #     "vat",
    #     "gross",
    #     "non_tax",
    # ],
    # 🔥 DODAJ KOLEJNE TABELE TUTAJ
}

delete_pattern = re.compile(r"### DELETE FROM `[^`]+`\.`([^`]+)`")
value_pattern = re.compile(r"###\s+@\d+=(.*)")

def clean_value(v: str) -> str:
    v = v.strip()
    if v == "NULL":
        return "NULL"
    return v

def main():
    content = Path(INPUT_FILE).read_text(encoding="utf-8", errors="ignore")
    lines = content.splitlines()

    inserts_by_table = defaultdict(list)

    current_table = None
    current_values = []

    for line in lines:
        table_match = delete_pattern.search(line)
        if table_match:
            current_table = table_match.group(1)
            current_values = []
            continue

        if current_table:
            value_match = value_pattern.search(line)
            if value_match:
                value = clean_value(value_match.group(1))
                current_values.append(value)
                continue

            if not line.startswith("###"):
                # koniec bloku
                if current_table in TABLE_COLUMNS:
                    columns = TABLE_COLUMNS[current_table]
                    if len(columns) <= len(current_values):
                        values = ", ".join(current_values[:len(columns)])
                        col_str = ", ".join(columns)

                        sql = f"INSERT INTO {current_table} ({col_str}) VALUES ({values});"
                        inserts_by_table[current_table].append(sql)

                current_table = None
                current_values = []

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("SET foreign_key_checks=0;\n\n")

        for table, inserts in inserts_by_table.items():
            f.write(f"-- TABLE: {table}\n")
            for ins in inserts:
                f.write(ins + "\n")
            f.write("\n")

        f.write("SET foreign_key_checks=1;\n")

    print(f"Generated {OUTPUT_FILE}")
    total = sum(len(v) for v in inserts_by_table.values())
    print(f"Total INSERTS: {total}")

if __name__ == "__main__":
    main()