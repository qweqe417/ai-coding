"""
MongoDB适配器

支持find_one、find、count等操作
"""

from typing import Dict, Any, List, Optional
import logging

try:
    from pymongo import MongoClient
    from bson import ObjectId
except ImportError:
    MongoClient = None
    ObjectId = None

from ..base import MiddlewareAdapter, ConnectionError, QueryError


class MongoDBAdapter(MiddlewareAdapter):
    """MongoDB适配器"""

    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        """
        初始化MongoDB适配器

        Args:
            config: MongoDB配置
                {
                    "host": "localhost",
                    "port": 27017,
                    "database": "test_db",
                    "username": "user",  # 可选
                    "password": "password"  # 可选
                }
        """
        super().__init__(config, logger)

        if MongoClient is None:
            raise ImportError("pymongo is not installed. Run: pip install pymongo")

        self.client = None
        self.db = None

    def connect(self):
        """连接到MongoDB"""
        try:
            host = self.config.get('host', 'localhost')
            port = self.config.get('port', 27017)
            username = self.config.get('username')
            password = self.config.get('password')

            # 构建连接字符串
            if username and password:
                connection_string = f"mongodb://{username}:{password}@{host}:{port}/"
            else:
                connection_string = f"mongodb://{host}:{port}/"

            self.client = MongoClient(connection_string)
            self.db = self.client[self.config['database']]

            # 测试连接
            self.client.server_info()
            self.connected = True
            self.logger.info(f"Connected to MongoDB: {host}:{port}/{self.config['database']}")

        except Exception as e:
            self.logger.error(f"Failed to connect to MongoDB: {e}")
            raise ConnectionError(f"Failed to connect to MongoDB: {e}")

    def disconnect(self):
        """断开连接"""
        if self.client:
            self.client.close()
            self.connected = False
            self.logger.info("Disconnected from MongoDB")

    def query(self, query_config: Dict[str, Any]) -> Any:
        """
        执行查询

        Args:
            query_config: 查询配置
                {
                    "type": "find_one" | "find" | "count",
                    "collection": "users",
                    "query": {"_id": "..."}
                }

        Returns:
            查询结果
                - find_one: Dict 或 None
                - find: List[Dict]
                - count: int
        """
        if not self.connected:
            raise ConnectionError("Not connected to MongoDB")

        query_type = query_config.get('type', 'find_one')
        collection_name = query_config['collection']
        query = query_config.get('query', {})

        try:
            collection = self.db[collection_name]
            self.logger.debug(f"Executing MongoDB {query_type.upper()} on {collection_name}: {query}")

            if query_type == 'find_one':
                result = collection.find_one(query)
                if result:
                    result = self._convert_objectid(result)
                self.logger.debug(f"find_one returned: {result}")
                return result

            elif query_type == 'find':
                cursor = collection.find(query)
                results = [self._convert_objectid(doc) for doc in cursor]
                self.logger.debug(f"find returned {len(results)} documents")
                return results

            elif query_type == 'count':
                count = collection.count_documents(query)
                self.logger.debug(f"count returned: {count}")
                return count

            else:
                raise QueryError(f"Unsupported query type: {query_type}")

        except Exception as e:
            self.logger.error(f"Query failed: {e}")
            raise QueryError(f"Query failed: {e}")

    def _convert_objectid(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """将ObjectId转换为字符串"""
        if isinstance(doc, dict):
            for key, value in doc.items():
                if isinstance(value, ObjectId):
                    doc[key] = str(value)
                elif isinstance(value, dict):
                    doc[key] = self._convert_objectid(value)
                elif isinstance(value, list):
                    doc[key] = [self._convert_objectid(item) if isinstance(item, dict) else item for item in value]
        return doc

    def find_one(self, collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        find_one操作（便捷方法）

        Args:
            collection: 集合名称
            query: 查询条件

        Returns:
            文档或None
        """
        return self.query({'type': 'find_one', 'collection': collection, 'query': query})

    def find(self, collection: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        find操作（便捷方法）

        Args:
            collection: 集合名称
            query: 查询条件

        Returns:
            文档列表
        """
        return self.query({'type': 'find', 'collection': collection, 'query': query})

    def count(self, collection: str, query: Dict[str, Any]) -> int:
        """
        count操作（便捷方法）

        Args:
            collection: 集合名称
            query: 查询条件

        Returns:
            文档数量
        """
        return self.query({'type': 'count', 'collection': collection, 'query': query})
