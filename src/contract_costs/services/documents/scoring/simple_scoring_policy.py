from contract_costs.model.document import ScoringResult
from contract_costs.services.companies.validators.company import CompanyValidator


class SimpleScoringPolicy:
    """
    Confidence scoring 0–100
    - kompletność danych
    - lekkie bonusy jakości
    - kara za brak linii
    - kara za podejrzane ilości (OCR shift)
    - umiarkowany bonus XML (+10)
    """

    @staticmethod
    def calculate(payload: dict, is_structured_xml: bool = False) -> ScoringResult:
        score = 0
        breakdown: dict[str, int] = {}

        def reward(reason: str, points: int):
            nonlocal score
            score += points
            breakdown[reason] = breakdown.get(reason, 0) + points

        def penalize(reason: str, points: int):
            nonlocal score
            score -= points
            breakdown[reason] = -points

        seller = payload.get("seller") or {}
        buyer = payload.get("buyer") or {}
        record = payload.get("record") or {}
        lines = payload.get("lines") or []

        # ==========================================
        # 1️⃣ MATCH KEY
        # ==========================================

        seller_nip = seller.get("tax_number")
        buyer_nip = buyer.get("tax_number")
        reference = record.get("reference") or ""

        if reference:
            reward("reference_present", 12)

            reference = record.get("reference") or ""
            if reference.startswith(("AI-", "TMP-")):
                penalize("synthetic_reference_detected", 15)

        if seller_nip:
            reward("seller_tax_number_present", 7)

            if CompanyValidator.validate_nip(seller_nip):
                reward("seller_nip_valid", 5)
            else:
                penalize("seller_nip_invalid", 10)

        if buyer_nip:
            if CompanyValidator.validate_nip(buyer_nip):
                reward("buyer_nip_valid", 3)
            else:
                penalize("buyer_nip_invalid", 5)

        if buyer_nip and seller_nip:
            reward("match_key_complete", 8)

        # ==========================================
        # 2️⃣ SPRZEDAWCA
        # ==========================================

        seller_fields = [
            seller.get("name"),
            seller.get("tax_number"),
            seller.get("city"),
            seller.get("street"),
        ]

        seller_filled = sum(1 for f in seller_fields if f)

        if seller_filled >= 3:
            reward("seller_section_complete", 8)
        elif seller_filled == 2:
            reward("seller_section_partial", 4)

        # ==========================================
        # 3️⃣ NABYWCA
        # ==========================================

        buyer_fields = [
            buyer.get("name"),
            buyer.get("tax_number"),
            buyer.get("city"),
        ]

        buyer_filled = sum(1 for f in buyer_fields if f)

        if buyer_filled >= 2:
            reward("buyer_section_complete", 8)
        elif buyer_filled == 1:
            reward("buyer_section_partial", 4)

        # ==========================================
        # 4️⃣ DATY I TYP
        # ==========================================

        if record.get("invoice_date"):
            reward("invoice_date_present", 10)

        if record.get("due_date"):
            reward("due_date_present", 4)

        if payload.get("document_type"):
            reward("document_type_present", 5)

        # ==========================================
        # 5️⃣ LINIE
        # ==========================================

        valid_lines = 0

        for line in lines:
            quantity = line.get("quantity")
            amount = (line.get("amount") or {}).get("value")
            name = line.get("item_name") or ""
            unit = line.get("unit")

            try:
                quantity_val = float(quantity)
            except (TypeError, ValueError):
                quantity_val = 0

            if quantity_val > 0 and amount:
                valid_lines += 1

                # mały bonus jakości nazwy
                if len(name) > 5:
                    reward("line_name_quality_bonus", 1)

                reward("positive_quantity_bonus", 1)

                # 🔴 detekcja podejrzanie dużej ilości (OCR shift)
                if quantity_val >= 1000 and unit not in ["m2", "kg"]:
                    penalize("suspicious_large_quantity", 8)

                # 🔴 klasyczny shift typu 1000 / 5000
                if str(quantity).endswith("000") and quantity_val >= 1000:
                    penalize("ocr_quantity_shift_detected", 5)

        if valid_lines >= 1:
            reward("valid_line_present", 8)
        else:
            penalize("no_valid_lines_penalty", 12)

        # ==========================================
        # 6️⃣ SPÓJNOŚĆ NIP
        # ==========================================

        if (
            record.get("seller_tax_number")
            and seller.get("tax_number")
            and record.get("seller_tax_number") == seller.get("tax_number")
        ):
            reward("seller_tax_consistent", 5)

        # ==========================================
        # 7️⃣ XML BONUS
        # ==========================================

        if is_structured_xml:
            reward("structured_xml_bonus", 10)

        # ==========================================
        # LIMIT 0–100
        # ==========================================

        score = max(0, min(score, 100))

        return ScoringResult(
            score=score,
            breakdown=breakdown,
        )