from datetime import datetime
from threading import Lock
from config.settings import BUSINESS_LOG_FILE, LOG_DIR

_log_lock = Lock()

def log_timeout_job(job_id, media_id, resolution, runtime, limit, exceed):
    LOG_DIR.mkdir(exist_ok=True)

    log_line = (
        f"[{datetime.now()}] "
        f"JOB_ID={job_id} | "
        f"MEDIA_ID={media_id} | "
        f"RULE=TIME_LIMIT_{resolution} | "
        f"RUNTIME={runtime}p | "
        f"LIMIT={limit}p | "
        f"EXCEED=+{exceed}p\n"
    )

    with _log_lock:
        with open(BUSINESS_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_line)
