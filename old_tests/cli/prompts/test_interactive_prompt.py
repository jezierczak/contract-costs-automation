import builtins

from contract_costs.cli.prompts.interactive import interactive_prompt


def test_interactive_prompt_simple_fields(monkeypatch):
    fields = [
        {"name": "name", "prompt": "Name", "type": str, "required": True},
        {"name": "city", "prompt": "City", "type": str, "required": True},
    ]

    inputs = iter(["Company A", "Krakow"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    result = interactive_prompt(fields)

    assert result == {
        "name": "Company A",
        "city": "Krakow",
    }

def test_interactive_prompt_optional_field(monkeypatch):
    fields = [
        {"name": "description", "prompt": "Description", "type": str, "required": False},
    ]

    inputs = iter([""])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    result = interactive_prompt(fields)

    assert result == {
        "description": None,
    }
from enum import Enum


class Role(Enum):
    OWNER = "OWN"
    CLIENT = "CLIENT"


def test_interactive_prompt_choices(monkeypatch):
    fields = [
        {
            "name": "role",
            "prompt": "Role",
            "type": Role,
            "choices": {
                "1": Role.OWNER,
                "2": Role.CLIENT,
            },
            "required": True,
        }
    ]

    inputs = iter(["1"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    result = interactive_prompt(fields)

    assert result == {
        "role": Role.OWNER,
    }

def test_interactive_prompt_required_retry(monkeypatch):
    fields = [
        {"name": "name", "prompt": "Name", "type": str, "required": True},
    ]

    inputs = iter(["", "Company B"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    result = interactive_prompt(fields)

    assert result == {
        "name": "Company B",
    }

def test_interactive_prompt_invalid_choice_retry(monkeypatch):
    fields = [
        {
            "name": "role",
            "prompt": "Role",
            "type": str,
            "choices": {
                "1": "A",
                "2": "B",
            },
            "required": True,
        }
    ]

    inputs = iter(["9", "2"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    result = interactive_prompt(fields)

    assert result == {
        "role": "B",
    }

