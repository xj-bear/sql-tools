import json
import mysql.connector
from mysql.connector import Error as MySQLError
from typing import Dict, Any, Optional
import time

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
        """初始化数据库管理器"""
        self.configs = json.loads(database_configs)
        self.connections = {}
        self.last_used = {}  # 记录连接最后使用时间
        self.connection_timeout = 300  # 连接超时时间（秒）
        
    def get_connection(self, db_name: str) -> Any:
        """获取数据库连接，包含重连机制"""
        if db_name not in self.configs:
            raise ValueError(f"Database config '{db_name}' not found")
            
        current_time = time.time()
        
        # 检查连接是否存在且未超时
        if db_name in self.connections and db_name in self.last_used:
            try:
                # 如果连接超过5分钟未使用，重新连接
                if current_time - self.last_used[db_name] > self.connection_timeout:
                    self.close_connection(db_name)
                else:
                    # 测试连接是否有效
                    if self.test_connection(db_name):
                        self.last_used[db_name] = current_time
                        return self.connections[db_name]
                    else:
                        self.close_connection(db_name)
            except Exception:
                self.close_connection(db_name)
        
        # 创建新连接
        config = self.configs[db_name]
        db_type = config["type"].lower()
        
        try:
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
                    connection_timeout=20,  # 连接超时时间
                    autocommit=True,  # 自动提交
                    pool_name=f"pool_{db_name}",  # 连接池名称
                    pool_size=5,  # 连接池大小
                    pool_reset_session=True  # 重置会话
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
                
            self.last_used[db_name] = current_time
            return self.connections[db_name]
            
        except Exception as e:
            raise Exception(f"Failed to connect to database '{db_name}': {str(e)}")
            
    def test_connection(self, db_name: str) -> bool:
        """测试连接是否有效"""
        try:
            if db_name in self.connections:
                conn = self.connections[db_name]
                if hasattr(conn, 'ping'):
                    conn.ping(reconnect=True)
                return True
        except Exception:
            return False
        return False
        
    def close_connection(self, db_name: str):
        """关闭指定的数据库连接"""
        try:
            if db_name in self.connections:
                self.connections[db_name].close()
                del self.connections[db_name]
            if db_name in self.last_used:
                del self.last_used[db_name]
        except Exception:
            pass
            
    def execute_query(self, db_name: str, sql: str) -> tuple:
        """执行SQL查询，包含重试机制"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                conn = self.get_connection(db_name)
                cursor = conn.cursor()
                cursor.execute(sql)
                
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                rows = cursor.fetchall()
                
                cursor.close()
                self.last_used[db_name] = time.time()  # 更新最后使用时间
                return columns, rows
                
            except (MySQLError, Exception) as e:
                retry_count += 1
                if retry_count >= max_retries:
                    raise Exception(f"Query failed after {max_retries} retries: {str(e)}")
                self.close_connection(db_name)  # 关闭失败的连接
                time.sleep(1)  # 等待1秒后重试
        
    def close_all(self):
        """关闭所有数据库连接"""
        for db_name in list(self.connections.keys()):
            self.close_connection(db_name)