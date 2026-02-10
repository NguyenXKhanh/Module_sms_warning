from db.mysql_pool import MySQLPool
from services.monitor_service import MonitorService
from config.settings import MONITOR_GRACE_MINUTES
from config.logging_config import setup_system_logging
from utils.system_logger import get_logger

logger = get_logger("Main")

if __name__ == "__main__":
    setup_system_logging()

    try:        
        MySQLPool.init_pool()
        MonitorService().run_forever(MONITOR_GRACE_MINUTES)
    
    finally:
        logger.info("Releasing resources")
        MySQLPool.close_pool()