from concurrent.futures import ThreadPoolExecutor
import time as time_module

from db.video_repo import VideoRepository
from services.rule_engine import get_time_limit, calc_runtime, map_resolution
from utils.business_logger import log_timeout_job
from config.settings import THREAD_POOL_SIZE, MONITOR_INTERVAL_SEC
from utils.system_logger import get_logger

logger = get_logger("MonitorService")

class MonitorService:

    #hàm thực hiện kiểm tra xem job có time out không
    def process_job(self, job, window_minutes):
        job_id = job["id"]
        try:
            runtime = calc_runtime(job["convert_start_time"])

            height = int(job["resolution"].split("x")[1])
            resolution = map_resolution(height)
            limit = get_time_limit(resolution)

            #chỉ ghi nhận job time out 1 lần ngay lần quét đầu phát hiện 
            if limit <= runtime < limit + window_minutes:

                exceed = runtime - limit
                logger.info(f"Found job{job_id} time out")
                log_timeout_job(
                    job_id=job["id"],
                    media_id=job["csm_media_id"],
                    resolution=resolution,
                    runtime=runtime,
                    limit=limit,
                    exceed=exceed
                )

        except Exception as e:
            logger.exception(f"Job{job_id} error while processing")


    def run_once(self, executor, window_minutes):

        jobs = VideoRepository.get_running_jobs()
        logger.info(f"{len(jobs)} running jobs")

        if not jobs:
            return

        #sử dụng threadpoll cho đa luồng
        for job in jobs:
            try:
                job_id = job["id"]
                executor.submit(self.process_job, job, window_minutes)
            except Exception as e:
                logger.error(f"Failded to submit job{job_id}")

    def run_forever(self, window_minutes):

        logger.info("Encode Monitor Service started")

        executor = ThreadPoolExecutor(max_workers= THREAD_POOL_SIZE)

        try:
            while True:
                try:
                    self.run_once(executor, window_minutes)
                except Exception as e:
                    logger.error(f"[SYSTEM ERROR] {e}")

                logger.info(f"Scan completed, sleeping {MONITOR_INTERVAL_SEC}s...\n")
                #mỗi lần sẽ quét lại sau thời gian cố định
                time_module.sleep(MONITOR_INTERVAL_SEC)

        except KeyboardInterrupt:
            logger.info("\nService stopped")
            executor.shutdown(wait=True)
