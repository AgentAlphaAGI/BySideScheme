import os
from typing import Any, Dict, List, Optional
from neo4j import GraphDatabase, Driver
from src.core.logger import logger


class Neo4jClient:
    """
    Neo4j 连接管理器（单例模式）
    从环境变量读取连接配置，提供 Cypher 查询执行方法，
    应用启动时自动初始化约束和索引。
    """

    _instance: Optional["Neo4jClient"] = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Neo4jClient, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._uri = os.getenv("NEO4J_URI", "bolt://localhost:17687")
        self._user = os.getenv("NEO4J_USER", "neo4j")
        self._password = os.getenv("NEO4J_PASSWORD", "bysidescheme")
        self._database = os.getenv("NEO4J_DATABASE", "neo4j")

        logger.info(f"Connecting to Neo4j at {self._uri} (db={self._database})")
        try:
            self._driver: Driver = GraphDatabase.driver(
                self._uri, auth=(self._user, self._password)
            )
            # Verify connectivity
            self._driver.verify_connectivity()
            logger.info("Neo4j connection established successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}", exc_info=True)
            raise

        self._init_schema()
        Neo4jClient._initialized = True

    def _init_schema(self):
        """
        初始化图数据库约束和索引。
        使用 user_id + name 复合唯一性约束，保证同一用户下实体不重复。
        """
        constraints = [
            # 节点唯一性约束（复合：user_id + name）
            (
                "constraint_person_unique",
                "CREATE CONSTRAINT constraint_person_unique IF NOT EXISTS "
                "FOR (n:Person) REQUIRE (n.user_id, n.name) IS UNIQUE",
            ),
            (
                "constraint_event_unique",
                "CREATE CONSTRAINT constraint_event_unique IF NOT EXISTS "
                "FOR (n:Event) REQUIRE (n.user_id, n.name) IS UNIQUE",
            ),
            (
                "constraint_project_unique",
                "CREATE CONSTRAINT constraint_project_unique IF NOT EXISTS "
                "FOR (n:Project) REQUIRE (n.user_id, n.name) IS UNIQUE",
            ),
            (
                "constraint_resource_unique",
                "CREATE CONSTRAINT constraint_resource_unique IF NOT EXISTS "
                "FOR (n:Resource) REQUIRE (n.user_id, n.name) IS UNIQUE",
            ),
            (
                "constraint_org_unique",
                "CREATE CONSTRAINT constraint_org_unique IF NOT EXISTS "
                "FOR (n:Organization) REQUIRE (n.user_id, n.name) IS UNIQUE",
            ),
        ]

        indexes = [
            # user_id 索引加速租户查询
            (
                "index_person_user",
                "CREATE INDEX index_person_user IF NOT EXISTS FOR (n:Person) ON (n.user_id)",
            ),
            (
                "index_event_user",
                "CREATE INDEX index_event_user IF NOT EXISTS FOR (n:Event) ON (n.user_id)",
            ),
            (
                "index_project_user",
                "CREATE INDEX index_project_user IF NOT EXISTS FOR (n:Project) ON (n.user_id)",
            ),
            (
                "index_resource_user",
                "CREATE INDEX index_resource_user IF NOT EXISTS FOR (n:Resource) ON (n.user_id)",
            ),
            (
                "index_org_user",
                "CREATE INDEX index_org_user IF NOT EXISTS FOR (n:Organization) ON (n.user_id)",
            ),
        ]

        try:
            with self._driver.session(database=self._database) as session:
                for name, cypher in constraints:
                    try:
                        session.run(cypher)
                        logger.debug(f"Ensured constraint: {name}")
                    except Exception as e:
                        # Some Neo4j editions don't support composite constraints
                        logger.warning(f"Could not create constraint {name}: {e}")

                for name, cypher in indexes:
                    try:
                        session.run(cypher)
                        logger.debug(f"Ensured index: {name}")
                    except Exception as e:
                        logger.warning(f"Could not create index {name}: {e}")

            logger.info("Neo4j schema initialization complete.")
        except Exception as e:
            logger.error(f"Error initializing Neo4j schema: {e}", exc_info=True)

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    def run_query(
        self, cypher: str, params: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        执行单条 Cypher 查询并返回结果列表。
        每个结果是一个 dict，key 为 RETURN 子句中的别名。
        """
        params = params or {}
        try:
            with self._driver.session(database=self._database) as session:
                result = session.run(cypher, params)
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Neo4j query error: {e}\nCypher: {cypher}\nParams: {params}", exc_info=True)
            raise

    def run_write(
        self, cypher: str, params: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        执行写入操作（在显式写事务中）。
        """
        params = params or {}
        try:
            with self._driver.session(database=self._database) as session:

                def _tx(tx):
                    result = tx.run(cypher, params)
                    return [record.data() for record in result]

                return session.execute_write(_tx)
        except Exception as e:
            logger.error(f"Neo4j write error: {e}\nCypher: {cypher}\nParams: {params}", exc_info=True)
            raise

    def close(self):
        """关闭驱动连接。"""
        if self._driver:
            self._driver.close()
            logger.info("Neo4j driver closed.")
