import os 
from dotenv import load_dotenv
from  pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

THREAD_POOL_SIZE = int(os.getenv("THREAD_POOL_SIZE"))

MYSQL_POOL={
    "pool_name": "pe_monitor_pool",
    "pool_size": int(os.getenv("MYSQL_POOL_SIZE")),
    "host": os.getenv("MYSQL_HOST"),
    "port": int(os.getenv("MYSQL_PORT")),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASS"),
    "database": os.getenv("MYSQL_DB"),
    "autocommit": True,
}

MONITOR_INTERVAL_SEC = int(os.getenv("MONITOR_INTERVAL_SEC"))
MONITOR_GRACE_MINUTES = int(os.getenv("MONITOR_GRACE_MINUTES"))

TIME_LIMIT_BY_RESOLUTION = {
    "720p": int(os.getenv("ENCODE_LIMIT_720P")),
    "1080p": int(os.getenv("ENCODE_LIMIT_1080P")),
    "1440p": int(os.getenv("ENCODE_LIMIT_1440P")),
    "2160p": int(os.getenv("ENCODE_LIMIT_2160P")),
}
DEFAULT_LIMIT = int(os.getenv("ENCODE_LIMIT_720P"))


LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))
SYSTEM_LOG_FILE = LOG_DIR / os.getenv("SYSTEM_LOG_FILE", "system.log")
BUSINESS_LOG_FILE = LOG_DIR / os.getenv("BUSINESS_LOG_FILE", "encode_monitor.log")