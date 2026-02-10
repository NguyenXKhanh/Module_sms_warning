import mysql.connector
from mysql.connector import pooling, Error
from config.settings import MYSQL_POOL
from utils.system_logger import get_logger

logger = get_logger("MySQLPool")

class MySQLPool:
    _pool = None

    @classmethod
    def init_pool(cls):
        if cls._pool is None:
            logger.info("Initializing MySQL connection pool")
            try:
                cls._pool = pooling.MySQLConnectionPool(**MYSQL_POOL)
                logger.info(f"Initializing success ")
            except Error as e:
                logger.exception("FAILED to initialize MySQL pool")
                raise

    @classmethod
    def get_conn(cls):
        if cls._pool is None:
            cls.init_pool()

        try:
            conn = cls._pool.get_connection()
            return conn
        except Error as e:
            logger.exception("FAILED to get MySQL connection from pool")
            raise

    @staticmethod
    def release_conn(conn):
        try:
            if conn:
                conn.close()
                logger.debug("Connection return to pool")
        except Exception as e:
            logger.exception("Failed to release connect")

    @classmethod
    def close_pool(cls):
        if cls._pool:
            logger.info("Closing MySQL pool")
            cls._pool = None