from dataclasses import dataclass
from enum import Enum
from decimal import Decimal


class TaxTreatment(Enum):
    TAX_DEDUCTIBLE = "tax_deductible"
    NON_DEDUCTIBLE = "non_deductible"


class VatRate(Enum):
    VAT_23 = Decimal("0.23")
    VAT_8 = Decimal("0.08")
    VAT_5 = Decimal("0.05")
    VAT_0 = Decimal("0.00")
    VAT_ZW = None


@dataclass(frozen=True)
class Amount:
    value: Decimal
    vat_rate: VatRate
    tax_treatment: TaxTreatment = TaxTreatment.TAX_DEDUCTIBLE

    @property
    def net(self) -> Decimal :
        if self.tax_treatment != TaxTreatment.TAX_DEDUCTIBLE:
            return Decimal("0.00")
        return self.value

    @property
    def tax(self) -> Decimal:
        if self.tax_treatment != TaxTreatment.TAX_DEDUCTIBLE:
            return Decimal("0.00")
        if self.vat_rate.value is None:
            return Decimal("0.00")
        return (self.value * self.vat_rate.value).quantize(Decimal("0.01"))

    @property
    def gross(self) -> Decimal:
        return self.value + self.tax

    @property
    def non_tax_cost(self) -> Decimal:
        if self.tax_treatment == TaxTreatment.NON_DEDUCTIBLE:
            return self.value
        return Decimal("0.00")

    @property
    def net_or_zero(self) -> Decimal:
        return self.net or Decimal("0.00")
