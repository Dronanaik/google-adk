from .db_connector import DatabaseConnector
import pandas as pd

class SchemaInspector:
    def __init__(self, connector: DatabaseConnector):
        self.connector = connector

    def get_all_tables(self):
        """
        Retrieves a list of all tables in the database.
        """
        if self.connector.db_type == 'postgresql':
            query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            """
            df = self.connector.execute_query(query)
            return df['table_name'].tolist()
            
        elif self.connector.db_type == 'mysql':
            query = "SHOW TABLES"
            df = self.connector.execute_query(query)
            return df.iloc[:, 0].tolist()
            
        elif self.connector.db_type == 'bigquery':
            # List tables in the dataset
            dataset_id = self.connector.config.get('dataset_id')
            tables = self.connector.client.list_tables(dataset_id)
            return [table.table_id for table in tables]
            
        return []

    def get_table_schema(self, table_name):
        """
        Retrieves the schema (column name, type) for a specific table.
        """
        if self.connector.db_type == 'postgresql':
            query = f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            """
            return self.connector.execute_query(query)
            
        elif self.connector.db_type == 'mysql':
            query = f"DESCRIBE {table_name}"
            return self.connector.execute_query(query)
            
        elif self.connector.db_type == 'bigquery':
            dataset_id = self.connector.config.get('dataset_id')
            table_ref = self.connector.client.dataset(dataset_id).table(table_name)
            table = self.connector.client.get_table(table_ref)
            schema_info = [{'column_name': schema.name, 'data_type': schema.field_type} for schema in table.schema]
            return pd.DataFrame(schema_info)
            
        return pd.DataFrame()

    def get_formatted_schema(self):
        """
        Returns a string representation of the schema for all tables, formatted for the LLM.
        """
        tables = self.get_all_tables()
        schema_str = ""
        for table in tables:
            df = self.get_table_schema(table)
            columns = [f"{row['column_name']} ({row['data_type']})" for _, row in df.iterrows()]
            schema_str += f"Table: {table}\nColumns: {', '.join(columns)}\n\n"
        return schema_str
