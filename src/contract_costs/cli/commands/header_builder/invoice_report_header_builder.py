from datetime import datetime

from contract_costs.cli.commands.header_builder.report_header_builder import ReportHeaderBuilder
from contract_costs.model.invoice import PaymentStatus


class InvoiceReportHeaderBuilder(ReportHeaderBuilder):

    @classmethod
    def from_args(cls, args) -> dict[str, list[str]]:
        return cls.build(
            mappings=[
                ("Contract", args.contract),
                ("Direction", args.direction),
                (
                    "Payment",
                    (
                        [p.name for p in [
                            PaymentStatus.UNPAID,
                            PaymentStatus.PARTIALLY_PAID,
                            PaymentStatus.UNKNOWN
                        ]]
                        if args.unpaid
                        else None
                    ),
                ),
                ("From", args.from_date),
                ("To", args.to_date),
                ("Last", args.last),
                ("Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            ]
        )
