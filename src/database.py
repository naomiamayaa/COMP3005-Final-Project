"""
Database connection module for Health and Fitness Club Management System
Handles PostgreSQL database connections and operations
"""

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DatabaseConnection:
    """Manages database connection pool and provides connection interface"""
    
    def __init__(self):
        """Initialize connection pool"""
        self.connection_pool = None
        self.init_pool()
    
    def init_pool(self):
        """Initialize the connection pool"""
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                1, 20,  # min and max connections
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5432'),
                database=os.getenv('DB_NAME', 'fitness_club'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', '')
            )
            if self.connection_pool:
                print("Database connection pool created successfully")
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error creating connection pool: {error}")
            raise
    
    def get_connection(self):
        """Get a connection from the pool"""
        try:
            return self.connection_pool.getconn()
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error getting connection from pool: {error}")
            raise
    
    def return_connection(self, connection):
        """Return a connection to the pool"""
        self.connection_pool.putconn(connection)
    
    def close_all_connections(self):
        """Close all connections in the pool"""
        if self.connection_pool:
            self.connection_pool.closeall()
            print("Database connection pool closed")


class DatabaseManager:
    """Provides high-level database operations"""
    
    def __init__(self, db_connection):
        """Initialize with a DatabaseConnection instance"""
        self.db_connection = db_connection
    
    def execute_query(self, query, params=None, fetch=True):
        """
        Execute a SQL query
        
        Args:
            query: SQL query string
            params: Query parameters (tuple or dict)
            fetch: Whether to fetch results
            
        Returns:
            Query results if fetch=True, otherwise None
        """
        connection = None
        cursor = None
        try:
            connection = self.db_connection.get_connection()
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute(query, params)
            
            if fetch:
                results = cursor.fetchall()
                return results
            else:
                connection.commit()
                return None
                
        except (Exception, psycopg2.DatabaseError) as error:
            if connection:
                connection.rollback()
            print(f"Error executing query: {error}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.db_connection.return_connection(connection)
    
    def execute_many(self, query, params_list):
        """
        Execute a query multiple times with different parameters
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples
        """
        connection = None
        cursor = None
        try:
            connection = self.db_connection.get_connection()
            cursor = connection.cursor()
            
            cursor.executemany(query, params_list)
            connection.commit()
                
        except (Exception, psycopg2.DatabaseError) as error:
            if connection:
                connection.rollback()
            print(f"Error executing batch query: {error}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.db_connection.return_connection(connection)
    
    def call_procedure(self, procedure_name, params=None):
        """
        Call a stored procedure
        
        Args:
            procedure_name: Name of the procedure
            params: Procedure parameters
        """
        connection = None
        cursor = None
        try:
            connection = self.db_connection.get_connection()
            cursor = connection.cursor()
            
            cursor.callproc(procedure_name, params)
            connection.commit()
                
        except (Exception, psycopg2.DatabaseError) as error:
            if connection:
                connection.rollback()
            print(f"Error calling procedure: {error}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.db_connection.return_connection(connection)
