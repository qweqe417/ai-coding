"""
自动中间件配置读取器

从项目源代码中自动检测中间件配置（数据库连接、Redis、消息队列等）
实现"零配置"设计目标
"""

import os
import re
import json
from typing import Dict, Any, Optional
import logging


class AutoConfigReader:
    """自动配置读取器

    支持从以下来源自动检测配置:
    - Java: application.yml, application.properties, application-{profile}.yml
    - Python: settings.py, .env, config.py, django settings
    - Go: config.yaml, config.toml, .env
    - Node.js: .env, config.js, config.json
    """

    def __init__(self, project_root: str, logger: Optional[logging.Logger] = None):
        """
        Args:
            project_root: 项目根目录
            logger: 日志实例
        """
        self.project_root = os.path.abspath(project_root)
        self.logger = logger or logging.getLogger(__name__)
        self._cache: Dict[str, Any] = {}

    def detect_middleware_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        自动检测所有中间件配置

        Returns:
            {
                'mysql': {'host': '...', 'port': 3306, 'database': '...', ...},
                'redis': {'host': '...', 'port': 6379, ...},
                ...
            }
        """
        configs: Dict[str, Dict[str, Any]] = {}

        # 检测各中间件
        mysql_config = self._detect_mysql()
        if mysql_config:
            configs['mysql'] = mysql_config

        redis_config = self._detect_redis()
        if redis_config:
            configs['redis'] = redis_config

        mongodb_config = self._detect_mongodb()
        if mongodb_config:
            configs['mongodb'] = mongodb_config

        rabbitmq_config = self._detect_rabbitmq()
        if rabbitmq_config:
            configs['rabbitmq'] = rabbitmq_config

        kafka_config = self._detect_kafka()
        if kafka_config:
            configs['kafka'] = kafka_config

        elasticsearch_config = self._detect_elasticsearch()
        if elasticsearch_config:
            configs['elasticsearch'] = elasticsearch_config

        return configs

    def _find_config_files(self, patterns: list) -> list:
        """查找配置文件"""
        results = []
        for root, dirs, files in os.walk(self.project_root):
            # 跳过不必要的目录
            dirs[:] = [d for d in dirs if d not in (
                'node_modules', 'vendor', '.git', '__pycache__',
                'venv', '.venv', 'target', 'build', 'dist',
                '.idea', '.vscode'
            )]
            for pattern in patterns:
                for f in files:
                    if f == pattern or f.endswith(pattern):
                        results.append(os.path.join(root, f))
        return results

    def _read_file_content(self, filepath: str) -> str:
        """读取文件内容"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.logger.debug(f"Failed to read {filepath}: {e}")
            return ""

    def _parse_yaml_value(self, content: str, key_path: str) -> Optional[str]:
        """从YAML内容中提取嵌套键值"""
        # 简化的YAML解析（支持嵌套键）
        lines = content.split('\n')
        current_indent = -1
        in_target = False
        current_parent_indent = -1

        keys = key_path.split('.')
        for i, key in enumerate(keys):
            found = False
            for line in lines:
                stripped = line.strip()
                if not stripped or stripped.startswith('#'):
                    continue

                # 计算缩进
                indent = len(line) - len(line.lstrip())

                if not found and stripped.startswith(key + ':'):
                    if i == len(keys) - 1:
                        # 最后一个key, 提取值
                        value = stripped[len(key)+1:].strip()
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        if value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        # 处理 ${VAR:default} 模式
                        env_match = re.match(r'\$\{([^:}]+)(?::([^}]*))?\}', value)
                        if env_match:
                            env_var = env_match.group(1)
                            default_val = env_match.group(2) or ""
                            value = os.environ.get(env_var, default_val)
                        return value if value else None
                    else:
                        current_indent = indent
                        found = True
                        in_target = True

            if not found:
                return None

        return None

    def _parse_properties_value(self, content: str, key: str) -> Optional[str]:
        """从Properties文件内容中提取键值"""
        pattern = re.compile(rf'^{re.escape(key)}\s*[=:]\s*(.+?)$', re.MULTILINE)
        match = pattern.search(content)
        if match:
            value = match.group(1).strip()
            # 处理 ${VAR:default} 模式
            env_match = re.match(r'\$\{([^:}]+)(?::([^}]*))?\}', value)
            if env_match:
                env_var = env_match.group(1)
                default_val = env_match.group(2) or ""
                return os.environ.get(env_var, default_val)
            return value
        return None

    def _parse_env_value(self, content: str, key: str) -> Optional[str]:
        """从.env文件内容中提取键值"""
        pattern = re.compile(rf'^{re.escape(key)}\s*=\s*(.+?)$', re.MULTILINE)
        match = pattern.search(content)
        if match:
            value = match.group(1).strip()
            # 去除引号
            if (value.startswith('"') and value.endswith('"')) or \
               (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            return value
        return None

    def _parse_json_value(self, content: str, key_path: str) -> Optional[Any]:
        """从JSON内容中提取嵌套键值"""
        try:
            data = json.loads(content)
            keys = key_path.split('.')
            for key in keys:
                if isinstance(data, dict):
                    data = data.get(key)
                else:
                    return None
                if data is None:
                    return None
            return data
        except json.JSONDecodeError:
            return None

    def _parse_jdbc_url(self, url: str) -> Dict[str, Any]:
        """解析JDBC URL提取连接信息"""
        config = {'url': url}
        # jdbc:mysql://host:port/database?params
        match = re.match(r'jdbc:(mysql|postgresql|mariadb)://([^:/]+)(?::(\d+))?/([^?]+)(\?.*)?', url)
        if match:
            config['db_type'] = match.group(1)
            config['host'] = match.group(2)
            config['port'] = int(match.group(3)) if match.group(3) else self._default_port(match.group(1))
            config['database'] = match.group(4)
            if match.group(5):
                params = match.group(5)[1:]  # remove '?'
                for param in params.split('&'):
                    if '=' in param:
                        k, v = param.split('=', 1)
                        config[k] = v
        return config

    @staticmethod
    def _default_port(db_type: str) -> int:
        ports = {'mysql': 3306, 'postgresql': 5432, 'mariadb': 3306}
        return ports.get(db_type, 3306)

    def _detect_mysql(self) -> Optional[Dict[str, Any]]:
        """检测MySQL配置"""
        # Java: application.yml / application.properties
        for config_file in self._find_config_files(['application.yml', 'application.yaml',
                                                      'application.properties', 'application-dev.yml',
                                                      'application-prod.yml']):
            content = self._read_file_content(config_file)

            # 尝试 YAML 格式
            if config_file.endswith(('.yml', '.yaml')):
                host = self._parse_yaml_value(content, 'spring.datasource.url')
                if host:
                    config = self._parse_jdbc_url(host)
                    username = self._parse_yaml_value(content, 'spring.datasource.username')
                    password = self._parse_yaml_value(content, 'spring.datasource.password')
                    if username:
                        config['username'] = username
                    if password:
                        config['password'] = password
                    config['enabled'] = True
                    return config

            # 尝试 Properties 格式
            elif config_file.endswith('.properties'):
                url = self._parse_properties_value(content, 'spring.datasource.url')
                if url:
                    config = self._parse_jdbc_url(url)
                    username = self._parse_properties_value(content, 'spring.datasource.username')
                    password = self._parse_properties_value(content, 'spring.datasource.password')
                    if username:
                        config['username'] = username
                    if password:
                        config['password'] = password
                    config['enabled'] = True
                    return config

        # Python: .env / settings.py
        for config_file in self._find_config_files(['.env', 'settings.py', 'config.py']):
            content = self._read_file_content(config_file)
            db_host = self._parse_env_value(content, 'DB_HOST') or \
                      self._parse_env_value(content, 'DATABASE_HOST') or \
                      self._parse_env_value(content, 'MYSQL_HOST')
            if db_host:
                db_port = self._parse_env_value(content, 'DB_PORT') or \
                          self._parse_env_value(content, 'DATABASE_PORT') or '3306'
                db_name = self._parse_env_value(content, 'DB_NAME') or \
                          self._parse_env_value(content, 'DATABASE_NAME') or \
                          self._parse_env_value(content, 'MYSQL_DATABASE')
                db_user = self._parse_env_value(content, 'DB_USER') or \
                          self._parse_env_value(content, 'DATABASE_USER') or \
                          self._parse_env_value(content, 'MYSQL_USER')
                db_pass = self._parse_env_value(content, 'DB_PASSWORD') or \
                          self._parse_env_value(content, 'DATABASE_PASSWORD') or \
                          self._parse_env_value(content, 'MYSQL_PASSWORD')
                return {
                    'host': db_host,
                    'port': int(db_port),
                    'database': db_name or '',
                    'username': db_user or '',
                    'password': db_pass or '',
                    'enabled': True
                }

        # Go: config.yaml 等
        for config_file in self._find_config_files(['config.yaml', 'config.yml', 'config.toml']):
            content = self._read_file_content(config_file)
            if config_file.endswith(('.yml', '.yaml')):
                db_host = self._parse_yaml_value(content, 'database.host')
                if db_host:
                    return {
                        'host': db_host,
                        'port': int(self._parse_yaml_value(content, 'database.port') or '3306'),
                        'database': self._parse_yaml_value(content, 'database.name') or '',
                        'username': self._parse_yaml_value(content, 'database.username') or '',
                        'password': self._parse_yaml_value(content, 'database.password') or '',
                        'enabled': True
                    }

        # Node.js: config.json
        for config_file in self._find_config_files(['config.json']):
            content = self._read_file_content(config_file)
            db_config = self._parse_json_value(content, 'database.mysql')
            if db_config:
                return {
                    'host': db_config.get('host', 'localhost'),
                    'port': db_config.get('port', 3306),
                    'database': db_config.get('database', ''),
                    'username': db_config.get('username', ''),
                    'password': db_config.get('password', ''),
                    'enabled': True
                }

        return None

    def _detect_redis(self) -> Optional[Dict[str, Any]]:
        """检测Redis配置"""
        # Java: application.yml / application.properties
        for config_file in self._find_config_files(['application.yml', 'application.yaml',
                                                      'application.properties']):
            content = self._read_file_content(config_file)

            if config_file.endswith(('.yml', '.yaml')):
                host = self._parse_yaml_value(content, 'spring.redis.host')
                if host:
                    return {
                        'host': host,
                        'port': int(self._parse_yaml_value(content, 'spring.redis.port') or '6379'),
                        'password': self._parse_yaml_value(content, 'spring.redis.password') or '',
                        'database': int(self._parse_yaml_value(content, 'spring.redis.database') or '0'),
                        'enabled': True
                    }

            elif config_file.endswith('.properties'):
                host = self._parse_properties_value(content, 'spring.redis.host')
                if host:
                    return {
                        'host': host,
                        'port': int(self._parse_properties_value(content, 'spring.redis.port') or '6379'),
                        'password': self._parse_properties_value(content, 'spring.redis.password') or '',
                        'database': int(self._parse_properties_value(content, 'spring.redis.database') or '0'),
                        'enabled': True
                    }

        # .env
        for config_file in self._find_config_files(['.env']):
            content = self._read_file_content(config_file)
            redis_host = self._parse_env_value(content, 'REDIS_HOST')
            if redis_host:
                return {
                    'host': redis_host,
                    'port': int(self._parse_env_value(content, 'REDIS_PORT') or '6379'),
                    'password': self._parse_env_value(content, 'REDIS_PASSWORD') or '',
                    'database': int(self._parse_env_value(content, 'REDIS_DB') or '0'),
                    'enabled': True
                }

        return None

    def _detect_mongodb(self) -> Optional[Dict[str, Any]]:
        """检测MongoDB配置"""
        # Java
        for config_file in self._find_config_files(['application.yml', 'application.yaml',
                                                      'application.properties']):
            content = self._read_file_content(config_file)

            if config_file.endswith(('.yml', '.yaml')):
                uri = self._parse_yaml_value(content, 'spring.data.mongodb.uri')
                host = self._parse_yaml_value(content, 'spring.data.mongodb.host')
                if uri:
                    # 解析 mongodb://host:port/database
                    match = re.match(r'mongodb://([^:]*):([^@]*)@([^:/]+)(?::(\d+))?/(.+)', uri)
                    if match:
                        return {
                            'host': match.group(3),
                            'port': int(match.group(4)) if match.group(4) else 27017,
                            'username': match.group(1) if match.group(1) else '',
                            'password': match.group(2) if match.group(2) else '',
                            'database': match.group(5),
                            'enabled': True
                        }
                elif host:
                    return {
                        'host': host,
                        'port': int(self._parse_yaml_value(content, 'spring.data.mongodb.port') or '27017'),
                        'database': self._parse_yaml_value(content, 'spring.data.mongodb.database') or '',
                        'enabled': True
                    }

            elif config_file.endswith('.properties'):
                uri = self._parse_properties_value(content, 'spring.data.mongodb.uri')
                host = self._parse_properties_value(content, 'spring.data.mongodb.host')
                if uri:
                    match = re.match(r'mongodb://([^:]*):([^@]*)@([^:/]+)(?::(\d+))?/(.+)', uri)
                    if match:
                        return {
                            'host': match.group(3),
                            'port': int(match.group(4)) if match.group(4) else 27017,
                            'username': match.group(1) if match.group(1) else '',
                            'password': match.group(2) if match.group(2) else '',
                            'database': match.group(5),
                            'enabled': True
                        }
                elif host:
                    return {
                        'host': host,
                        'port': int(self._parse_properties_value(content, 'spring.data.mongodb.port') or '27017'),
                        'database': self._parse_properties_value(content, 'spring.data.mongodb.database') or '',
                        'enabled': True
                    }

        # .env
        for config_file in self._find_config_files(['.env']):
            content = self._read_file_content(config_file)
            mongo_uri = self._parse_env_value(content, 'MONGODB_URI') or \
                       self._parse_env_value(content, 'MONGO_URI')
            mongo_host = self._parse_env_value(content, 'MONGODB_HOST') or \
                        self._parse_env_value(content, 'MONGO_HOST')
            if mongo_uri:
                match = re.match(r'mongodb://([^:]*):([^@]*)@([^:/]+)(?::(\d+))?/(.+)', mongo_uri)
                if match:
                    return {
                        'host': match.group(3),
                        'port': int(match.group(4)) if match.group(4) else 27017,
                        'username': match.group(1) if match.group(1) else '',
                        'password': match.group(2) if match.group(2) else '',
                        'database': match.group(5),
                        'enabled': True
                    }
            elif mongo_host:
                return {
                    'host': mongo_host,
                    'port': int(self._parse_env_value(content, 'MONGODB_PORT') or '27017'),
                    'database': self._parse_env_value(content, 'MONGODB_DATABASE') or '',
                    'enabled': True
                }

        return None

    def _detect_rabbitmq(self) -> Optional[Dict[str, Any]]:
        """检测RabbitMQ配置"""
        # Java
        for config_file in self._find_config_files(['application.yml', 'application.yaml',
                                                      'application.properties']):
            content = self._read_file_content(config_file)

            if config_file.endswith(('.yml', '.yaml')):
                host = self._parse_yaml_value(content, 'spring.rabbitmq.host')
                if host:
                    return {
                        'host': host,
                        'port': int(self._parse_yaml_value(content, 'spring.rabbitmq.port') or '5672'),
                        'username': self._parse_yaml_value(content, 'spring.rabbitmq.username') or 'guest',
                        'password': self._parse_yaml_value(content, 'spring.rabbitmq.password') or 'guest',
                        'virtual_host': self._parse_yaml_value(content, 'spring.rabbitmq.virtual-host') or '/',
                        'enabled': True
                    }
            elif config_file.endswith('.properties'):
                host = self._parse_properties_value(content, 'spring.rabbitmq.host')
                if host:
                    return {
                        'host': host,
                        'port': int(self._parse_properties_value(content, 'spring.rabbitmq.port') or '5672'),
                        'username': self._parse_properties_value(content, 'spring.rabbitmq.username') or 'guest',
                        'password': self._parse_properties_value(content, 'spring.rabbitmq.password') or 'guest',
                        'virtual_host': self._parse_properties_value(content, 'spring.rabbitmq.virtual-host') or '/',
                        'enabled': True
                    }

        # .env
        for config_file in self._find_config_files(['.env']):
            content = self._read_file_content(config_file)
            host = self._parse_env_value(content, 'RABBITMQ_HOST')
            if host:
                return {
                    'host': host,
                    'port': int(self._parse_env_value(content, 'RABBITMQ_PORT') or '5672'),
                    'username': self._parse_env_value(content, 'RABBITMQ_USER') or 'guest',
                    'password': self._parse_env_value(content, 'RABBITMQ_PASSWORD') or 'guest',
                    'virtual_host': self._parse_env_value(content, 'RABBITMQ_VHOST') or '/',
                    'enabled': True
                }

        return None

    def _detect_kafka(self) -> Optional[Dict[str, Any]]:
        """检测Kafka配置"""
        # Java
        for config_file in self._find_config_files(['application.yml', 'application.yaml',
                                                      'application.properties']):
            content = self._read_file_content(config_file)

            if config_file.endswith(('.yml', '.yaml')):
                servers = self._parse_yaml_value(content, 'spring.kafka.bootstrap-servers')
                if servers:
                    return {
                        'bootstrap_servers': servers,
                        'group_id': self._parse_yaml_value(content, 'spring.kafka.consumer.group-id') or '',
                        'enabled': True
                    }
            elif config_file.endswith('.properties'):
                servers = self._parse_properties_value(content, 'spring.kafka.bootstrap-servers')
                if servers:
                    return {
                        'bootstrap_servers': servers,
                        'group_id': self._parse_properties_value(content, 'spring.kafka.consumer.group-id') or '',
                        'enabled': True
                    }

        # .env
        for config_file in self._find_config_files(['.env']):
            content = self._read_file_content(config_file)
            brokers = self._parse_env_value(content, 'KAFKA_BOOTSTRAP_SERVERS') or \
                     self._parse_env_value(content, 'KAFKA_BROKERS')
            if brokers:
                return {
                    'bootstrap_servers': brokers,
                    'group_id': self._parse_env_value(content, 'KAFKA_GROUP_ID') or '',
                    'enabled': True
                }

        return None

    def _detect_elasticsearch(self) -> Optional[Dict[str, Any]]:
        """检测Elasticsearch配置"""
        # Java
        for config_file in self._find_config_files(['application.yml', 'application.yaml',
                                                      'application.properties']):
            content = self._read_file_content(config_file)

            if config_file.endswith(('.yml', '.yaml')):
                uris = self._parse_yaml_value(content, 'spring.elasticsearch.uris')
                host = self._parse_yaml_value(content, 'spring.elasticsearch.host')
                if uris:
                    return {
                        'hosts': uris,
                        'username': self._parse_yaml_value(content, 'spring.elasticsearch.username') or '',
                        'password': self._parse_yaml_value(content, 'spring.elasticsearch.password') or '',
                        'enabled': True
                    }
                elif host:
                    return {
                        'hosts': f"{host}:{self._parse_yaml_value(content, 'spring.elasticsearch.port') or '9200'}",
                        'username': self._parse_yaml_value(content, 'spring.elasticsearch.username') or '',
                        'password': self._parse_yaml_value(content, 'spring.elasticsearch.password') or '',
                        'enabled': True
                    }
            elif config_file.endswith('.properties'):
                uris = self._parse_properties_value(content, 'spring.elasticsearch.uris')
                if uris:
                    return {
                        'hosts': uris,
                        'username': self._parse_properties_value(content, 'spring.elasticsearch.username') or '',
                        'password': self._parse_properties_value(content, 'spring.elasticsearch.password') or '',
                        'enabled': True
                    }

        # .env
        for config_file in self._find_config_files(['.env']):
            content = self._read_file_content(config_file)
            es_host = self._parse_env_value(content, 'ELASTICSEARCH_HOST') or \
                     self._parse_env_value(content, 'ES_HOST')
            if es_host:
                return {
                    'hosts': f"{es_host}:{self._parse_env_value(content, 'ELASTICSEARCH_PORT') or '9200'}",
                    'username': self._parse_env_value(content, 'ELASTICSEARCH_USER') or '',
                    'password': self._parse_env_value(content, 'ELASTICSEARCH_PASSWORD') or '',
                    'enabled': True
                }

        return None

    def detect_service_config(self) -> Dict[str, Any]:
        """检测服务配置（URL、端口等）"""
        config = {}

        # 从配置文件检测
        for config_file in self._find_config_files(['application.yml', 'application.yaml',
                                                      'application.properties',
                                                      'serverless.yml', 'docker-compose.yml']):
            content = self._read_file_content(config_file)

            if config_file.endswith(('.yml', '.yaml')):
                port = self._parse_yaml_value(content, 'server.port')
                if port:
                    config['port'] = int(port)
                context_path = self._parse_yaml_value(content, 'server.servlet.context-path')
                if context_path:
                    config['context_path'] = context_path

        # 从 .env 检测
        for config_file in self._find_config_files(['.env']):
            content = self._read_file_content(config_file)
            port = self._parse_env_value(content, 'PORT') or \
                   self._parse_env_value(content, 'SERVER_PORT')
            if port:
                config['port'] = int(port)
            base_url = self._parse_env_value(content, 'BASE_URL') or \
                      self._parse_env_value(content, 'API_URL')
            if base_url:
                config['base_url'] = base_url

        return config
