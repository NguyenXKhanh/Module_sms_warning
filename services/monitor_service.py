from concurrent.futures import ThreadPoolExecutor
import time as time_module

from db.video_repo import VideoRepository
from services.rule_engine import get_time_limit, calc_runtime, map_resolution
from utils.business_logger import log_timeout_job
from config.settings import THREAD_POOL_SIZE, MONITOR_INTERVAL_SEC
from utils.system_logger import get_logger
from db.timeout_event_repo import TimeoutEventRepo
from db.mysql_pool import MySQLPool

logger = get_logger("MonitorService")

class MonitorService:

    #hàm thực hiện kiểm tra xem job có time out không
    def process_job(self, job):
        job_id = job["id"]
        conn = None

        try:
            runtime = calc_runtime(job["convert_start_time"])

            height = int(job["resolution"].split("x")[1])
            resolution = map_resolution(height)
            limit = get_time_limit(resolution)

            if runtime < limit:
                return

            exceed = runtime - limit
            logger.info(f"Found job {job_id} timeout")

            conn = MySQLPool.get_conn()

            event = TimeoutEventRepo.find_open_event(conn, job_id)

            if not event:
                logger.info(f"Create timeout event for job {job_id}")

                TimeoutEventRepo.insert_event(
                    conn,
                    job_id=job["id"],
                    media_id=job["csm_media_id"],
                    resolution=resolution,
                    limit=limit,
                    runtime=runtime,
                    exceed=exceed
                )

                log_timeout_job(
                    job_id=job["id"],
                    media_id=job["csm_media_id"],
                    resolution=resolution,
                    runtime=runtime,
                    limit=limit,
                    exceed=exceed
                )

            else:
                logger.info(f"Update timeout event for job {job_id}")
                TimeoutEventRepo.update_event(
                    conn,
                    job_id=job_id,
                    runtime=runtime,
                    exceed=exceed
                )

        except Exception:
            if conn and conn.is_connected():
                try:
                    conn.rollback()
                except Exception as rollback_error:
                    logger.exception(f"Error during rollback: {rollback_error}")
            logger.exception(f"Job {job_id} error while processing")

        finally:
            if conn and conn.is_connected():
                MySQLPool.release_conn(conn)


    def run_once(self, executor):

        conn = None
        try:
            conn = MySQLPool.get_conn()
            jobs = VideoRepository.get_running_jobs(conn)
            logger.info(f"{len(jobs)} running jobs")

        finally:
            if conn and conn.is_connected():
                MySQLPool.release_conn(conn)

        if not jobs:
            return

        #sử dụng threadpoll cho đa luồng
        for job in jobs:
            try:
                job_id = job["id"]
                executor.submit(self.process_job, job)
            except Exception as e:
                logger.error(f"Failded to submit job{job_id}")

                
    def close_finished_events(self):
        conn = None
        try:
            conn = MySQLPool.get_conn()

            open_jobs = TimeoutEventRepo.get_open_events(conn)

            if not open_jobs:
                return

            finished_jobs = VideoRepository.get_finished_jobs(conn, open_jobs)

            for job_id in finished_jobs:
                logger.info(f"Close timeout event for job {job_id}")
                TimeoutEventRepo.close_event(conn, job_id)

            conn.commit()

        except Exception:
            if conn and conn.is_connected():
                try:
                    conn.rollback()
                except Exception as rollback_error:
                    logger.exception(f"Error during rollback: {rollback_error}")
            logger.exception("Close finished events failed")

        finally:
            if conn and conn.is_connected():
                MySQLPool.release_conn(conn)


    def run_forever(self):

        logger.info("Encode Monitor Service started")

        executor = ThreadPoolExecutor(max_workers= THREAD_POOL_SIZE)

        try:
            while True:
                try:
                    self.run_once(executor)
                    self.close_finished_events()
                except Exception as e:
                    logger.error(f"[SYSTEM ERROR] {e}")

                logger.info(f"Scan completed, sleeping {MONITOR_INTERVAL_SEC}s...\n")
                #mỗi lần sẽ quét lại sau thời gian cố định
                time_module.sleep(MONITOR_INTERVAL_SEC)

        except KeyboardInterrupt:
            logger.info("\nService stopped")

        finally:
            executor.shutdown(wait=True)
            logger.info("ThreadPollExecutor shutdown completed")
