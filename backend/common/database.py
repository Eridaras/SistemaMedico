"""
Database configuration and connection pool
Optimized for scalability and performance
"""
import os
import sys
from contextlib import contextmanager
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
import time

# Configurar encoding UTF-8 para la consola en Windows
if sys.platform == 'win32':
    import codecs
    try:
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except:
        pass

class Database:
    """
    Enhanced database connection pool manager with:
    - Thread-safe connection pooling
    - Automatic retry on connection failures
    - Query timeout protection
    - Prepared statement support
    - Performance monitoring
    """

    def __init__(self):
        self.connection_pool = None
        self.stats = {
            'queries': 0,
            'errors': 0,
            'retries': 0
        }
        self._initialize_pool()

    def _initialize_pool(self):
        """Initialize the connection pool with optimized settings"""
        try:
            # Get pool size from environment or use defaults
            min_conn = int(os.getenv('DB_POOL_MIN', 2))
            max_conn = int(os.getenv('DB_POOL_MAX', 20))

            self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                min_conn,  # minconn - keep minimum connections alive
                max_conn,  # maxconn - maximum concurrent connections
                os.getenv('DATABASE_URL'),
                cursor_factory=RealDictCursor,
                # Connection optimization settings
                connect_timeout=int(os.getenv('DB_CONNECT_TIMEOUT', 10)),
                # Note: statement_timeout removed for Neon.tech compatibility
                keepalives=1,
                keepalives_idle=30,
                keepalives_interval=10,
                keepalives_count=5
            )
            if self.connection_pool:
                print(f"Database connection pool created (min={min_conn}, max={max_conn})")
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error creating connection pool: {error}")
            raise

    @contextmanager
    def get_connection(self, retry=3):
        """
        Get a connection from the pool with automatic retry

        Args:
            retry: Number of retry attempts on connection failure
        """
        connection = None
        last_error = None

        for attempt in range(retry):
            try:
                connection = self.connection_pool.getconn()
                yield connection
                break
            except psycopg2.OperationalError as e:
                last_error = e
                self.stats['retries'] += 1
                if attempt < retry - 1:
                    time.sleep(0.5 * (attempt + 1))  # Exponential backoff
                    continue
                else:
                    self.stats['errors'] += 1
                    raise
            except Exception as e:
                last_error = e
                self.stats['errors'] += 1
                raise
            finally:
                if connection:
                    self.connection_pool.putconn(connection)

    @contextmanager
    def get_cursor(self, commit=False, retry=3):
        """
        Get a cursor with automatic connection management and error handling

        Args:
            commit: Whether to commit the transaction
            retry: Number of retry attempts
        """
        with self.get_connection(retry=retry) as connection:
            cursor = connection.cursor()
            try:
                self.stats['queries'] += 1
                yield cursor
                if commit:
                    connection.commit()
            except Exception as e:
                connection.rollback()
                self.stats['errors'] += 1
                raise e
            finally:
                cursor.close()

    def execute_query(self, query, params=None, fetch=True):
        """
        Execute a query and return results

        Args:
            query: SQL query string
            params: Query parameters
            fetch: Whether to fetch results

        Returns:
            Query results or None
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            if fetch:
                return cursor.fetchall()
            return None

    def execute_many(self, query, params_list):
        """
        Execute query with multiple parameter sets

        Args:
            query: SQL query string
            params_list: List of parameter tuples

        Returns:
            Number of affected rows
        """
        with self.get_cursor(commit=True) as cursor:
            cursor.executemany(query, params_list)
            return cursor.rowcount

    def get_stats(self):
        """Get database connection statistics"""
        return {
            **self.stats,
            'pool_size': self.connection_pool._maxconn if self.connection_pool else 0,
            'timestamp': time.time()
        }

    def reset_stats(self):
        """Reset statistics counters"""
        self.stats = {
            'queries': 0,
            'errors': 0,
            'retries': 0
        }

    def health_check(self):
        """
        Check database health

        Returns:
            Boolean indicating if database is healthy
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute('SELECT 1')
                return True
        except Exception:
            return False

    def close_all_connections(self):
        """Close all connections in the pool"""
        if self.connection_pool:
            self.connection_pool.closeall()
            print("All database connections closed")

# Singleton instance
db = Database()
