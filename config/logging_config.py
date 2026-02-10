import logging
from config.settings import LOG_DIR, SYSTEM_LOG_FILE

def setup_system_logging():
    LOG_DIR.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(SYSTEM_LOG_FILE, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
