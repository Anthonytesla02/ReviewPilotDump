import os
import psycopg2
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from urllib.parse import urlparse
import logging

class DatabaseManager:
    def __init__(self):
        """Initialize database connection using environment variables"""
        self.connection_params = self._get_connection_params()
        self.engine = None
        self.connection = None
        self._initialize_connection()
    
    def _get_connection_params(self):
        """Get database connection parameters from environment variables"""
        
        # Use the provided ReviewPilot database URL
        database_url = "postgresql://reviewpilot_user:kLQiZvLx6Hk5sOw92HO5tt7Xa9oeUEL6@dpg-d27nseogjchc738fvaf0-a.oregon-postgres.render.com/reviewpilot"
        
        if database_url:
            # Parse the database URL
            parsed = urlparse(database_url)
            return {
                'host': parsed.hostname,
                'port': parsed.port or 5432,
                'database': parsed.path[1:] if parsed.path else '',
                'username': parsed.username,
                'password': parsed.password
            }
        else:
            # Fallback to individual environment variables
            return {
                'host': os.getenv('PGHOST', 'localhost'),
                'port': int(os.getenv('PGPORT', 5432)),
                'database': os.getenv('PGDATABASE', 'postgres'),
                'username': os.getenv('PGUSER', 'postgres'),
                'password': os.getenv('PGPASSWORD', '')
            }
    
    def _initialize_connection(self):
        """Initialize SQLAlchemy engine and connection"""
        try:
            # Create SQLAlchemy engine
            connection_string = (
                f"postgresql://{self.connection_params['username']}:"
                f"{self.connection_params['password']}@"
                f"{self.connection_params['host']}:"
                f"{self.connection_params['port']}/"
                f"{self.connection_params['database']}"
            )
            
            self.engine = create_engine(
                connection_string,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=False
            )
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
        except Exception as e:
            st.error(f"Database connection failed: {str(e)}")
            self.engine = None
    
    def test_connection(self):
        """Test database connection"""
        if not self.engine:
            return False
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            st.error(f"Connection test failed: {str(e)}")
            return False
    
    def get_all_tables(self):
        """Get list of all tables in the database"""
        try:
            query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                tables = [row[0] for row in result]
            
            return tables
        
        except Exception as e:
            st.error(f"Error fetching tables: {str(e)}")
            return []
    
    def get_table_info(self, table_name):
        """Get detailed information about a table's columns"""
        try:
            query = """
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length,
                numeric_precision,
                numeric_scale,
                CASE 
                    WHEN column_name IN (
                        SELECT column_name 
                        FROM information_schema.key_column_usage 
                        WHERE table_name = :table_name 
                        AND constraint_name IN (
                            SELECT constraint_name 
                            FROM information_schema.table_constraints 
                            WHERE table_name = :table_name 
                            AND constraint_type = 'PRIMARY KEY'
                        )
                    ) THEN true 
                    ELSE false 
                END as is_primary_key
            FROM information_schema.columns 
            WHERE table_name = :table_name 
            AND table_schema = 'public'
            ORDER BY ordinal_position;
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query), {"table_name": table_name})
                columns = []
                
                for row in result:
                    columns.append({
                        'column_name': row[0],
                        'data_type': row[1],
                        'is_nullable': row[2],
                        'column_default': row[3],
                        'character_maximum_length': row[4],
                        'numeric_precision': row[5],
                        'numeric_scale': row[6],
                        'is_primary_key': row[7]
                    })
            
            return columns
        
        except Exception as e:
            st.error(f"Error fetching table info: {str(e)}")
            return []
    
    def get_table_row_count(self, table_name):
        """Get the number of rows in a table"""
        try:
            query = f'SELECT COUNT(*) FROM "{table_name}";'
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                count = result.scalar()
            
            return count
        
        except Exception as e:
            st.error(f"Error getting row count: {str(e)}")
            return 0
    
    def get_table_data(self, table_name, limit=100, offset=0, columns=None, search_term=None):
        """Get data from a table with optional filtering and pagination"""
        try:
            # Build column selection
            if columns:
                column_str = ', '.join([f'"{col}"' for col in columns])
            else:
                column_str = '*'
            
            # Build base query
            query = f'SELECT {column_str} FROM "{table_name}"'
            params = {}
            
            # Add search filter if provided
            if search_term:
                # Get all columns for search
                if not columns:
                    table_info = self.get_table_info(table_name)
                    all_columns = [col['column_name'] for col in table_info]
                else:
                    all_columns = columns
                
                # Create search conditions
                search_conditions = []
                for col in all_columns:
                    search_conditions.append(f'CAST("{col}" AS TEXT) ILIKE :search_term')
                
                query += f' WHERE ({" OR ".join(search_conditions)})'
                params['search_term'] = f'%{search_term}%'
            
            # Add pagination
            query += f' LIMIT {limit} OFFSET {offset}'
            
            # Execute query and return as DataFrame
            with self.engine.connect() as conn:
                df = pd.read_sql_query(text(query), conn, params=params)
            
            return df
        
        except Exception as e:
            st.error(f"Error fetching table data: {str(e)}")
            return None
    
    def get_foreign_keys(self):
        """Get foreign key relationships in the database"""
        try:
            query = """
            SELECT
                tc.table_name as source_table,
                kcu.column_name as source_column,
                ccu.table_name as target_table,
                ccu.column_name as target_column,
                tc.constraint_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = 'public'
            ORDER BY tc.table_name, kcu.column_name;
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                foreign_keys = []
                
                for row in result:
                    foreign_keys.append({
                        'Source Table': row[0],
                        'Source Column': row[1],
                        'Target Table': row[2],
                        'Target Column': row[3],
                        'Constraint Name': row[4]
                    })
            
            return foreign_keys
        
        except Exception as e:
            st.error(f"Error fetching foreign keys: {str(e)}")
            return []
    
    def execute_custom_query(self, query):
        """Execute a custom SQL query and return results as DataFrame"""
        try:
            with self.engine.connect() as conn:
                df = pd.read_sql_query(text(query), conn)
            
            return df
        
        except Exception as e:
            st.error(f"Error executing query: {str(e)}")
            return None
    
    def close_connection(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
