import json
import os
import re
from openai import OpenAI


class OpenAIInvoiceClient:
    def __init__(self, schema: dict, prompt_template: str) -> None:
        self._schema = schema
        self._prompt_template = prompt_template

        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY not set")

        self._client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def extract(self, text: str) -> dict:
        prompt = self._prompt_template \
            .replace("{SCHEMA}", self._schema_as_text()) \
            .replace("{TEXT}", text[:6000])

        response = self._client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
        )

        return self._clean_json(response.output_text)

    def _schema_as_text(self) -> str:
        return ",\n".join(f"{k}: {v}" for k, v in self._schema.items())

    def _clean_json(self, raw: str) -> dict:
        match = re.search(r"```json(.*?)```", raw, re.S | re.I)
        if match:
            raw = match.group(1)

        match = re.search(r"\{.*}", raw, re.S)
        if not match:
            raise ValueError("No JSON in AI response")

        parsed = json.loads(match.group(0))
        return {k: parsed.get(k) for k in self._schema.keys()}
