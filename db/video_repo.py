from db.mysql_pool import MySQLPool
from utils.system_logger import get_logger

logger = get_logger("VideoRepository")

class VideoRepository:

    @staticmethod
    def get_running_jobs():
        conn = MySQLPool.get_conn()
        cursor = conn.cursor(dictionary = True)

        try:
          sql = """
          SELECT id, csm_media_id, resolution, convert_start_time
          FROM pe_quality_metric.video
          WHERE status %10 = 2
            AND convert_start_time IS NOT NULL
            AND convert_end_time IS NULL
          """
          cursor.execute(sql)
          return cursor.fetchall()
        
        except Exception as e:
          logger.exception("DB QUERY FAILED in get_running_jobs")
          raise

        finally:
          try:
            if cursor:
              cursor.close()
            if conn:
              MySQLPool.release_conn(conn)
          except Exception as e:
              logger.exception("FAILED to release DB resources")
        
