"""
Elasticsearch适配器

支持search、get、count等操作
"""

from typing import Dict, Any, Optional, List
import logging

try:
    from elasticsearch import Elasticsearch
except ImportError:
    Elasticsearch = None

from ..base import MiddlewareAdapter, ConnectionError, QueryError


class ElasticsearchAdapter(MiddlewareAdapter):
    """Elasticsearch适配器"""

    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        """
        初始化Elasticsearch适配器

        Args:
            config: Elasticsearch配置
                {
                    "hosts": ["http://localhost:9200"],
                    "username": "elastic",  # 可选
                    "password": "password"  # 可选
                }
        """
        super().__init__(config, logger)

        if Elasticsearch is None:
            raise ImportError("elasticsearch is not installed. Run: pip install elasticsearch")

        self.client = None

    def connect(self):
        """连接到Elasticsearch"""
        try:
            hosts = self.config.get('hosts', ['http://localhost:9200'])
            username = self.config.get('username')
            password = self.config.get('password')

            if username and password:
                self.client = Elasticsearch(
                    hosts,
                    basic_auth=(username, password)
                )
            else:
                self.client = Elasticsearch(hosts)

            # 测试连接
            info = self.client.info()
            self.connected = True
            self.logger.info(f"Connected to Elasticsearch: {hosts}, version: {info['version']['number']}")

        except Exception as e:
            self.logger.error(f"Failed to connect to Elasticsearch: {e}")
            raise ConnectionError(f"Failed to connect to Elasticsearch: {e}")

    def disconnect(self):
        """断开连接"""
        if self.client:
            self.client.close()
            self.connected = False
            self.logger.info("Disconnected from Elasticsearch")

    def query(self, query_config: Dict[str, Any]) -> Any:
        """
        执行查询

        Args:
            query_config: 查询配置
                {
                    "type": "search" | "get" | "count",
                    "index": "test_index",
                    "query": {...},  # search/count使用
                    "id": "doc_id"   # get使用
                }

        Returns:
            查询结果
                - search: List[Dict]
                - get: Dict
                - count: int
        """
        if not self.connected:
            raise ConnectionError("Not connected to Elasticsearch")

        query_type = query_config.get('type', 'search')
        index = query_config['index']

        try:
            self.logger.debug(f"Executing Elasticsearch {query_type.upper()} on {index}")

            if query_type == 'search':
                query = query_config.get('query', {'match_all': {}})
                response = self.client.search(index=index, query=query)
                hits = response['hits']['hits']
                results = [hit['_source'] for hit in hits]
                self.logger.debug(f"search returned {len(results)} documents")
                return results

            elif query_type == 'get':
                doc_id = query_config['id']
                response = self.client.get(index=index, id=doc_id)
                result = response['_source']
                self.logger.debug(f"get returned document: {doc_id}")
                return result

            elif query_type == 'count':
                query = query_config.get('query', {'match_all': {}})
                response = self.client.count(index=index, query=query)
                count = response['count']
                self.logger.debug(f"count returned: {count}")
                return count

            else:
                raise QueryError(f"Unsupported query type: {query_type}")

        except Exception as e:
            self.logger.error(f"Query failed: {e}")
            raise QueryError(f"Query failed: {e}")

    def search(self, index: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        search操作（便捷方法）

        Args:
            index: 索引名称
            query: 查询条件

        Returns:
            文档列表
        """
        return self.query({'type': 'search', 'index': index, 'query': query})

    def get(self, index: str, doc_id: str) -> Dict[str, Any]:
        """
        get操作（便捷方法）

        Args:
            index: 索引名称
            doc_id: 文档ID

        Returns:
            文档
        """
        return self.query({'type': 'get', 'index': index, 'id': doc_id})

    def count(self, index: str, query: Dict[str, Any]) -> int:
        """
        count操作（便捷方法）

        Args:
            index: 索引名称
            query: 查询条件

        Returns:
            文档数量
        """
        return self.query({'type': 'count', 'index': index, 'query': query})
