# import contract_costs.config as cfg
#
from contract_costs.cli.context import get_services
from contract_costs.runner.watcher import run_watcher
# from contract_costs.services.watcher.invoice_watcher_service import (
#     InvoiceWatcherService,
# )


def handle_run() -> None:
    services = get_services()
    run_watcher(services)
    # \services = get_services()



    # watch_dir = cfg.INVOICE_INPUT_DIR
    #
    # print(f"Watching directory: {watch_dir}")
    #
    # watcher = InvoiceWatcherService(
    #     watch_dir=watch_dir,
    #     parse_invoice_service=services.parse_invoice_from_file,
    # )
    #
    # watcher.run()
