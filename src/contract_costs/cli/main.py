import logging
import os
import sys

from contract_costs.cli.cli_builder import build_cli_parser

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

def log_unhandled_exception(exc_type, exc, tb):
    logging.critical(
        "UNHANDLED EXCEPTION",
        exc_info=(exc_type, exc, tb),
    )

sys.excepthook = log_unhandled_exception



def main(argv: list[str] | None = None) -> None:
    import contract_costs.config as cfg  # 🔥 JAWNE: config ładuje się TU
    logging.info("APP_ENV=%s | WORK_DIR=%s | DB=%s",
                 cfg.APP_ENV, cfg.WORK_DIR, cfg.DB_CONFIG["database"])

    if os.getenv("APP_ENV", "test") == "prod":
        print("⚠️  RUNNING IN PRODUCTION MODE ⚠️")
        confirm = input("Type 'PROD' to continue: ")
        if confirm != "PROD":
            print("Aborted.")
            exit(1)

    parser = build_cli_parser()
    args = parser.parse_args(argv)
    # ---------- ROUTING ----------
    if hasattr(args, "handler"):
        args.handler(args)
        return

if __name__ == "__main__":
    main(sys.argv[1:])
