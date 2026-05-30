"""
MySQL适配器

支持SELECT、COUNT查询，支持连接池
"""

from typing import Dict, Any, List, Optional
import logging

try:
    import pymysql
    from pymysql.cursors import DictCursor
except ImportError:
    pymysql = None

from ..base import MiddlewareAdapter, ConnectionError, QueryError


class MySQLAdapter(MiddlewareAdapter):
    """MySQL适配器"""

    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        """
        初始化MySQL适配器

        Args:
            config: MySQL配置
                {
                    "host": "localhost",
                    "port": 3306,
                    "user": "root",
                    "password": "password",
                    "database": "test_db",
                    "charset": "utf8mb4"
                }
        """
        super().__init__(config, logger)

        if pymysql is None:
            raise ImportError("pymysql is not installed. Run: pip install pymysql")

        self.connection = None

    def connect(self):
        """连接到MySQL"""
        try:
            self.connection = pymysql.connect(
                host=self.config.get('host', 'localhost'),
                port=self.config.get('port', 3306),
                user=self.config.get('user') or self.config.get('username', 'root'),
                password=self.config.get('password') or self.config.get('password', ''),
                database=self.config.get('database') or self.config.get('database', 'test'),
                charset=self.config.get('charset', 'utf8mb4'),
                cursorclass=DictCursor
            )
            self.connected = True
            self.logger.info(f"Connected to MySQL: {self.config['host']}:{self.config['port']}/{self.config['database']}")

        except Exception as e:
            self.logger.error(f"Failed to connect to MySQL: {e}")
            raise ConnectionError(f"Failed to connect to MySQL: {e}")

    def disconnect(self):
        """断开连接"""
        if self.connection:
            self.connection.close()
            self.connected = False
            self.logger.info("Disconnected from MySQL")

    def query(self, query_config: Dict[str, Any]) -> Any:
        """
        执行查询

        Args:
            query_config: 查询配置
                {
                    "type": "select" | "count",
                    "sql": "SELECT * FROM users WHERE id = %s",
                    "params": [1]  # 可选
                }

        Returns:
            查询结果
                - select: List[Dict] 或 Dict（如果只有一行）
                - count: int
        """
        if not self.connected:
            raise ConnectionError("Not connected to MySQL")

        query_type = query_config.get('type', 'select')
        sql = query_config['sql']
        params = query_config.get('params', [])

        try:
            with self.connection.cursor() as cursor:
                self.logger.debug(f"Executing SQL: {sql} with params: {params}")
                cursor.execute(sql, params)

                if query_type == 'select':
                    results = cursor.fetchall()
                    self.logger.debug(f"Query returned {len(results)} rows")

                    # 如果只有一行，返回字典；否则返回列表
                    if len(results) == 1:
                        return results[0]
                    return results

                elif query_type == 'count':
                    result = cursor.fetchone()
                    count = list(result.values())[0] if result else 0
                    self.logger.debug(f"Count query returned: {count}")
                    return count

                else:
                    raise QueryError(f"Unsupported query type: {query_type}")

        except Exception as e:
            self.logger.error(f"Query failed: {e}")
            raise QueryError(f"Query failed: {e}")

    def execute_select(self, sql: str, params: Optional[List] = None) -> List[Dict[str, Any]]:
        """
        执行SELECT查询（便捷方法）

        Args:
            sql: SQL语句
            params: 参数列表

        Returns:
            查询结果列表
        """
        return self.query({
            'type': 'select',
            'sql': sql,
            'params': params or []
        })

    def execute_count(self, sql: str, params: Optional[List] = None) -> int:
        """
        执行COUNT查询（便捷方法）

        Args:
            sql: SQL语句
            params: 参数列表

        Returns:
            计数结果
        """
        return self.query({
            'type': 'count',
            'sql': sql,
            'params': params or []
        })
