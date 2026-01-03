import json
import os
import re
from openai import OpenAI


import json
import os
import re
import time
import logging
from openai import OpenAI
from openai import RateLimitError

from contract_costs.model.company import Company
from contract_costs.services.invoices.dto.parse import CompanyInput

logger = logging.getLogger(__name__)


class OpenAIInvoiceClient:
    def __init__(self, schema: dict | None =None, prompt_template: str | None=None) -> None:
        self._schema = schema
        self._prompt_template = prompt_template

        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY not set")

        self._client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def extract(self, text: str) -> dict:
        if not self._prompt_template or not self._schema:
            raise RuntimeError("Prompt template or schema not set!")
        prompt = (
            self._prompt_template
            .replace("{SCHEMA}", self._schema_as_text())
            .replace("{TEXT}", text[:6000])
        )

        try:
            response = self._client.responses.create(
                model="gpt-4.1-mini",
                input=prompt,
            )
        except RateLimitError as e:
            logger.warning(
                "OpenAI rate limit hit, backing off for 20s"
            )
            time.sleep(20)
            raise  # WAŻNE – worker musi to zobaczyć
        except Exception:
            logger.exception("OpenAI request failed")
            raise

        return self._clean_json(response.output_text)

    def _schema_as_text(self) -> str:
        if not self._schema:
            return ""
        return ",\n".join(f"{k}: {v}" for k, v in self._schema.items())

    def _clean_json(self, raw: str) -> dict:
        match = re.search(r"```json(.*?)```", raw, re.S | re.I)
        if match:
            raw = match.group(1)

        match = re.search(r"\{.*}", raw, re.S)
        if not match:
            raise ValueError("No JSON in AI response")

        parsed = json.loads(match.group(0))
        if self._schema:
            return {k: parsed.get(k) for k in self._schema.keys()}
        else: raise AttributeError("No schema found")

    def resolve_company(
            self,
            input_company: CompanyInput,
            companies: list[Company],
            *,
            min_confidence: float = 0.85,
    ) -> CompanyInput | None:
        """
        Tries to resolve input_company against known companies using LLM.
        Returns resolved CompanyInput or None if no confident match.
        """

        input_payload = self._company_input_for_llm(input_company)
        candidates_payload = [
            self._company_candidate_for_llm(c)
            for c in companies
        ]

        if not candidates_payload:
            return None

        prompt = self._build_company_resolution_prompt(
            input_payload,
            candidates_payload,
        )

        response = self._call_llm(prompt)

        result = self._parse_company_resolution(response)

        if not result:
            return None

        if result["company_id"] is None:
            return None

        if result["confidence"] < min_confidence:
            logger.info(
                "Company resolution confidence too low: %.2f (%s)",
                result["confidence"],
                result["reason"],
            )
            return None

        matched = next(
            c for c in companies
            if str(c.id) == result["company_id"]
        )

        return self._company_to_input(matched, input_company.role)

    @staticmethod
    def _company_input_for_llm( c: CompanyInput) -> dict:
        return {
            "name": c.name,
            "tax_number": c.tax_number,
            "street": c.street,
            "city": c.city,
            "zip_code": c.zip_code,
            "country": c.country,
            "phone_number": c.phone_number,
            "email": c.email,
            "bank_account": c.bank_account,
        }
    @staticmethod
    def _company_candidate_for_llm( c: Company) -> dict:
        return {
            "id": str(c.id),
            "name": c.name,
            "tax_number": c.tax_number,
            "street": c.address.street if c.address else None,
            "city": c.address.city if c.address else None,
            "zip_code": c.address.zip_code if c.address else None,
            "country": c.address.country if c.address else None,
            "phone_number": c.contact.phone_number if c.contact else None,
            "email": c.contact.email if c.contact else None,
            "bank_account": c.bank_account.number if c.bank_account else None,
            # "role": c.role.value,
            # "is_active": c.is_active,
        }
    @staticmethod
    def _build_company_resolution_prompt(
            input_company: dict,
            candidates: list[dict],
    ) -> str:
        return f"""
    You are resolving whether INPUT_COMPANY matches any of the CANDIDATE_COMPANIES.

    INPUT_COMPANY:
    {json.dumps(input_company, ensure_ascii=False, indent=2)}

    CANDIDATE_COMPANIES:
    {json.dumps(candidates, ensure_ascii=False, indent=2)}

    Rules:
    - Tax number may be missing or incorrect.
    - Company names may differ due to OCR errors or abbreviations.
    - Address, phone number and bank account are strong identifiers.
    - Match ONLY if you are confident it is the same real-world company.
    - If no company matches, return null.

    Return JSON ONLY in the following format:

    {{
      "company_id": "<id or null>",
      "confidence": 0.0,
      "reason": "short explanation"
    }}
    """

    def _call_llm(self, prompt: str) -> str:
        response = self._client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
        )
        return response.output_text
    @staticmethod
    def _parse_company_resolution(raw: str) -> dict | None:
        match = re.search(r"\{.*}", raw, re.S)
        if not match:
            return None

        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            logger.exception("Invalid JSON from LLM")
            return None
    @staticmethod
    def _company_to_input(
            c: Company,
            role: str,
    ) -> CompanyInput:
        return CompanyInput(
            name=c.name,
            tax_number=c.tax_number,
            street=c.address.street if c.address else None,
            city=c.address.city if c.address else None,
            state=None,
            zip_code=c.address.zip_code if c.address else None,
            country=c.address.country if c.address else None,
            phone_number=c.contact.phone_number if c.contact else None,
            email=c.contact.email if c.contact else None,
            bank_account=c.bank_account.number if c.bank_account else None,
            role=role,
        )
