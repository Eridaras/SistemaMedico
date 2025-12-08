"""
Database configuration and connection pool
"""
import os
from contextlib import contextmanager
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

class Database:
    """Database connection pool manager"""

    def __init__(self):
        self.connection_pool = None
        self._initialize_pool()

    def _initialize_pool(self):
        """Initialize the connection pool"""
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                1,  # minconn
                20,  # maxconn
                os.getenv('DATABASE_URL'),
                cursor_factory=RealDictCursor
            )
            if self.connection_pool:
                print("✓ Database connection pool created successfully")
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"✗ Error creating connection pool: {error}")
            raise

    @contextmanager
    def get_connection(self):
        """Get a connection from the pool"""
        connection = self.connection_pool.getconn()
        try:
            yield connection
        finally:
            self.connection_pool.putconn(connection)

    @contextmanager
    def get_cursor(self, commit=False):
        """Get a cursor with automatic connection management"""
        with self.get_connection() as connection:
            cursor = connection.cursor()
            try:
                yield cursor
                if commit:
                    connection.commit()
            except Exception as e:
                connection.rollback()
                raise e
            finally:
                cursor.close()

    def close_all_connections(self):
        """Close all connections in the pool"""
        if self.connection_pool:
            self.connection_pool.closeall()
            print("✓ All database connections closed")

# Singleton instance
db = Database()
