import os
import pymysql
import prestodb
from pyhive import hive
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.connections = {}
        
    def get_mysql_connection(self):
        if 'mysql' not in self.connections:
            self.connections['mysql'] = pymysql.connect(
                host=os.getenv('MYSQL_HOST'),
                port=int(os.getenv('MYSQL_PORT', 3306)),
                user=os.getenv('MYSQL_USER'),
                password=os.getenv('MYSQL_PASSWORD'),
                charset='utf8mb4'
            )
        return self.connections['mysql']
    
    def get_presto_connection(self):
        if 'presto' not in self.connections:
            self.connections['presto'] = prestodb.dbapi.connect(
                host=os.getenv('PRESTO_HOST'),
                port=int(os.getenv('PRESTO_PORT', 8080)),
                user=os.getenv('PRESTO_USER'),
                catalog=os.getenv('PRESTO_CATALOG'),
                schema=os.getenv('PRESTO_SCHEMA')
            )
        return self.connections['presto']
    
    def get_hive_connection(self):
        if 'hive' not in self.connections:
            self.connections['hive'] = hive.Connection(
                host=os.getenv('HIVE_HOST'),
                port=int(os.getenv('HIVE_PORT', 10000)),
                username=os.getenv('HIVE_USER')
            )
        return self.connections['hive']
    
    def execute_query(self, db_type: str, sql: str):
        try:
            if db_type == 'mysql':
                conn = self.get_mysql_connection()
            elif db_type == 'presto':
                conn = self.get_presto_connection()
            elif db_type == 'hive':
                conn = self.get_hive_connection()
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
            
            df = pd.read_sql(sql, conn)
            return df.to_markdown(index=False)
            
        except Exception as e:
            raise Exception(f"Database error: {str(e)}") 