# contract_costs/cli/prompts/interactive.py

def interactive_prompt(fields: list[dict]) -> dict:
    data = {}

    for field in fields:
        name = field["name"]
        prompt = field["prompt"]
        required = field.get("required", True)
        field_type = field.get("type", str)
        choices = field.get("choices")

        default = field.get("default")

        if default is not None:
            print(f"(default: {default})")

        while True:
            print(f"{prompt}:")

            if choices:
                for key, value in choices.items():
                    label = value.name if hasattr(value, "name") else str(value)
                    print(f"  {key}. {label}")

            raw = input("-> ").strip()

            if not raw:
                if default is not None:
                    data[name] = default
                    break
                if required:
                    print("Value required.")
                    continue
                data[name] = None
                break

            if choices:
                if raw not in choices:
                    print("Invalid choice.")
                    continue
                data[name] = choices[raw]
                break

            try:
                data[name] = field_type(raw)
                break
            except ValueError:
                print(f"Invalid value for {name}.")

    return data
