import re

INPUT_FILE = "deleted_items.txt"
OUTPUT_FILE = "financial_records_recovery.sql"

COLUMNS = [
    "id",
    "organization_id",
    "reference",
    "invoice_date",
    "selling_date",
    "buyer_id",
    "seller_id",
    "payment_method",
    "due_date",
    "payment_status",
    "status",
    "timestamp",
    "created_at",
    "created_by_user_id",
    "updated_at",
    "updated_by_user_id",
    "scan_filename",
    "tags",
    "paid_date",
]

def normalize(value):
    if value == "NULL":
        return "NULL"
    value = value.strip("'")

    # fix date format 2026:01:22 -> 2026-01-22
    if re.match(r"\d{4}:\d{2}:\d{2}", value):
        value = value.replace(":", "-")

    return f"'{value}'"
def main():
    records = []
    current = []

    with open(INPUT_FILE, encoding="utf-8") as f:
        for line in f:
            if "DELETE FROM `contract_costs`.`financial_records`" in line:
                current = []
            elif line.strip().startswith("###   @"):
                value = line.split("=", 1)[1].strip()
                current.append(value)
            elif current and line.strip() == "":
                if len(current) == 19:
                    records.append(current)
                current = []

    # catch last one
    if len(current) == 19:
        records.append(current)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for r in records:
            values = ", ".join(normalize(v) for v in r)
            cols = ", ".join(COLUMNS)
            out.write(
                f"INSERT INTO contract_costs_recovery.financial_records ({cols}) VALUES ({values});\n"
            )

    print(f"Odzyskano {len(records)} rekordów.")
    print(f"Zapisano do: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()