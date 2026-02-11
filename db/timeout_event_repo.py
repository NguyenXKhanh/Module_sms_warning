from sqlite3 import IntegrityError
from db.mysql_pool import MySQLPool
from utils.system_logger import get_logger
from mysql.connector import Error

logger = get_logger("TimeoutEventRepo")

class TimeoutEventRepo:

    @staticmethod
    def find_open_event(conn, job_id):
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                """SELECT * FROM video_timeout_event WHERE job_id=%s AND status='OPEN'""",(job_id,))
            return cursor.fetchone()
        
        except Error:
            logger.exception("Find event failed")
            raise
        finally:
            cursor.close()

    @staticmethod
    def get_open_events(conn):
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT job_id
                FROM video_timeout_event
                WHERE status = 'OPEN'
                """
            )
            return [row["job_id"] for row in cursor.fetchall()]
        finally:
            cursor.close()


    @staticmethod
    def insert_event(conn, job_id, media_id, resolution, limit, runtime, exceed):
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO video_timeout_event
                (
                    job_id,
                    media_id,
                    resolution,
                    time_limit,
                    first_detected_at,
                    last_detected_at,
                    runtime_minutes,
                    exceed_minutes,
                    detect_count,
                    status
                )
                VALUES (%s,%s,%s,%s,NOW(),NOW(),%s,%s,1,'OPEN')
                """,
                (job_id, media_id, resolution, limit, runtime, exceed)
            )
            conn.commit()
        except IntegrityError:
            logger.warning(f"Duplicate timeout event for job {job_id}, ignore")

        except Error:
            conn.rollback()
            logger.exception(f"Insert event failed for job {job_id}")
            raise

        finally:
            cursor.close()


    @staticmethod
    def update_event(conn, job_id, runtime, exceed):
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE video_timeout_event
                SET last_detected_at = NOW(),
                    runtime_minutes = %s,
                    exceed_minutes = %s,
                    detect_count = detect_count + 1
                WHERE job_id = %s
                  AND status = 'OPEN'
                """,
                (runtime, exceed, job_id)
            )

            conn.commit()

        except Error:
            conn.rollback()
            logger.exception(f"Update event failed for job {job_id}")
            raise

        finally:
            cursor.close()

    @staticmethod
    def close_event(conn, job_id):
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE video_timeout_event
                SET status = 'CLOSED'
                WHERE job_id = %s
                  AND status = 'OPEN'
                """,
                (job_id,)
            )

            conn.commit()

        except Error:
            conn.rollback()
            logger.exception(f"Close event failed for job {job_id}")
            raise

        finally:
            cursor.close()

    