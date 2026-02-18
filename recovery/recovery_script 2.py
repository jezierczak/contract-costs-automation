from datetime import datetime
import re

INPUT_FILE = "deleted_items.txt"
OUTPUT_FILE = "contract_node_value_snapshots_recovery.sql"

TABLE_TO_INSERT = "contract_node_value_snapshots"

TABLE_MARKER = "DELETE FROM `contract_costs`.`contract_node_value_snapshots`"

columns = [
    "id",
    "node_snapshot_id",
    "value_type_id",
    "net",
    "vat",
    "gross",
    "non_deductible"

]

EXPECTED_COLUMNS = len(columns)

def clean_value(v):
    v = v.strip()

    if v == "NULL":
        return "NULL"

    raw = v.strip("'")
    if re.match(r"^\d{10}$", raw):
        dt = datetime.fromtimestamp(int(raw))
        return f"'{dt.strftime('%Y-%m-%d %H:%M:%S')}'"

    # data 2026:01:22
    if re.match(r"\d{4}:\d{2}:\d{2}$", raw):
        raw = raw.replace(":", "-")
        return f"'{raw}'"

    # liczba całkowita lub decimal
    if re.match(r"^-?\d+(\.\d+)?$", raw):
        return raw



    return f"'{raw}'"

def main():
    with open(INPUT_FILE, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    in_block = False
    current_values = []
    all_records = []

    for line in lines:
        if TABLE_MARKER in line:
            in_block = True
            current_values = []
            continue

        if in_block:
            if line.startswith("###   @"):
                value = line.split("=", 1)[1].strip()
                current_values.append(value)

                # financial_record_lines miało wtedy 17 kolumn
                if len(current_values) == EXPECTED_COLUMNS:
                    all_records.append(current_values)
                    in_block = False

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("SET FOREIGN_KEY_CHECKS=0;\n\n")

        for record in all_records:
            values = [clean_value(v) for v in record]
            insert = f"INSERT INTO {TABLE_TO_INSERT} ({', '.join(columns)}) VALUES ({', '.join(values)});\n"
            out.write(insert)

        out.write("\nSET FOREIGN_KEY_CHECKS=1;\n")

    print(f"Odzyskano {len(all_records)} rekordów.")
    print(f"Zapisano do: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()