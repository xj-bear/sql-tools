import json
import mysql.connector
from typing import Dict, Any, Optional

# 条件导入数据库驱动
try:
    from pyhive import hive
except ImportError:
    hive = None

try:
    from presto.dbapi import connect as presto_connect
except ImportError:
    presto_connect = None

class DatabaseManager:
    def __init__(self, database_configs: str):
        """初始化数据库管理器
        
        Args:
            database_configs: JSON格式的数据库配置字符串
        """
        self.configs = json.loads(database_configs)
        self.connections = {}
        
    def get_connection(self, db_name: str) -> Any:
        """获取指定数据库的连接"""
        if db_name not in self.configs:
            raise ValueError(f"Database config '{db_name}' not found")
            
        if db_name not in self.connections:
            config = self.configs[db_name]
            db_type = config["type"].lower()
            
            if db_type == "mysql":
                self.connections[db_name] = mysql.connector.connect(
                    host=config["host"],
                    port=config["port"],
                    user=config["user"],
                    password=config.get("password", ""),
                    database=config.get("database", ""),
                    charset='utf8mb4',
                    collation='utf8mb4_unicode_ci',
                    use_unicode=True,
                    auth_plugin='mysql_native_password',
                    consume_results=True,
                )
                # 设置会话变量
                cursor = self.connections[db_name].cursor(dictionary=True)
                cursor.execute('SET NAMES utf8mb4')
                cursor.execute('SET CHARACTER SET utf8mb4')
                cursor.execute('SET character_set_connection=utf8mb4')
                cursor.execute('SET character_set_results=utf8mb4')
                cursor.execute('SET character_set_client=utf8mb4')
                cursor.close()
            elif db_type == "hive":
                if hive is None:
                    raise ImportError("Hive support is not installed. Please install pyhive.")
                self.connections[db_name] = hive.Connection(
                    host=config["host"],
                    port=config["port"],
                    username=config["user"]
                )
            elif db_type == "presto":
                if presto_connect is None:
                    raise ImportError("Presto support is not installed. Please install presto-python-client.")
                self.connections[db_name] = presto_connect(
                    host=config["host"],
                    port=config["port"],
                    user=config["user"],
                    catalog=config.get("catalog", "hive"),
                    schema=config.get("schema", "default")
                )
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
                
        return self.connections[db_name]
        
    def execute_query(self, db_name: str, sql: str) -> tuple:
        """执行SQL查询"""
        conn = self.get_connection(db_name)
        cursor = conn.cursor()
        cursor.execute(sql)
        
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        
        cursor.close()
        return columns, rows
        
    def close_all(self):
        """关闭所有数据库连接"""
        for conn in self.connections.values():
            try:
                conn.close()
            except:
                pass
        self.connections.clear()