import logging


def configure_logging():
    root_logging = logging.getLogger()
    if not root_logging.handlers:
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
    logging.getLogger("app").setLevel(logging.INFO)
