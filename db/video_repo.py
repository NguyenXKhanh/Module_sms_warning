from db.mysql_pool import MySQLPool
from utils.system_logger import get_logger

logger = get_logger("VideoRepository")

class VideoRepository:

  @staticmethod
  def get_running_jobs(conn):
      cursor = conn.cursor(dictionary = True)

      try:
        sql = """
        SELECT id, csm_media_id, resolution, convert_start_time
        FROM pe_quality_metric.video
        WHERE status % 10 = 2
          AND convert_start_time IS NOT NULL
          AND convert_end_time IS NULL
        """
        cursor.execute(sql)
        return cursor.fetchall()
        
      except Exception as e:
        logger.exception(f"DB QUERY FAILED in get_running_jobs - Error type: {type(e).__name__}, Details: {str(e)}")
        raise

      finally:
        try:
          if cursor:
            cursor.close()
        except Exception as e:
            logger.exception("FAILED to release DB resources")
        
  @staticmethod
  def get_finished_jobs(conn, job_ids):
    cursor = conn.cursor(dictionary=True)

    try:
        format_strings = ",".join(["%s"] * len(job_ids))
        #Lấy các job nằm trong danh sách các jobs timeout trước đó nhưng đã hoàn thành
        cursor.execute(
            f"""
            SELECT id
            FROM pe_quality_metric.video
            WHERE id IN ({format_strings})
              AND convert_end_time IS NOT NULL
            """,
            tuple(job_ids)
        )
        return [row["id"] for row in cursor.fetchall()]
    except Exception as e:
      logger.exception(f"Failed to get finished jobs. Total jobs to check: {len(job_ids)}, Error: {str(e)}")
      raise
    finally:
        cursor.close()


  
