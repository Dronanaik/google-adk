import os
from sqlalchemy import create_engine, text
from google.cloud import bigquery
import pandas as pd

class DatabaseConnector:
    def __init__(self, db_type, **kwargs):
        self.db_type = db_type.lower()
        self.config = kwargs
        self.engine = None
        self.client = None
        self._connect()

    def _connect(self):
        if self.db_type == 'postgresql':
            user = self.config.get('user')
            password = self.config.get('password')
            host = self.config.get('host', 'localhost')
            port = self.config.get('port', '5432')
            dbname = self.config.get('dbname')
            url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
            self.engine = create_engine(url)
            
        elif self.db_type == 'mysql':
            user = self.config.get('user')
            password = self.config.get('password')
            host = self.config.get('host', 'localhost')
            port = self.config.get('port', '3306')
            dbname = self.config.get('dbname')
            url = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{dbname}"
            self.engine = create_engine(url)
            
        elif self.db_type == 'bigquery':
            # Assumes GOOGLE_APPLICATION_CREDENTIALS is set or using default auth
            self.client = bigquery.Client(project=self.config.get('project_id'))
            
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")

    def execute_query(self, query):
        """
        Executes a SQL query and returns the result as a Pandas DataFrame.
        """
        if self.db_type in ['postgresql', 'mysql']:
            with self.engine.connect() as connection:
                return pd.read_sql(text(query), connection)
                
        elif self.db_type == 'bigquery':
            query_job = self.client.query(query)
            return query_job.to_dataframe()
            
        else:
            raise ValueError("Database not connected")

    def get_schema(self, table_name=None):
        """
        Returns schema information. Implementation depends on DB type.
        """
        # Placeholder for schema retrieval logic
        pass
