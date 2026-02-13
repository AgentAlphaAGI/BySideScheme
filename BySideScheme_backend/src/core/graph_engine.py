import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.core.llm_client import LLMClientFactory
from src.core.logger import logger
from src.core.neo4j_client import Neo4jClient
from src.core.prompt_loader import PromptLoader

# ------------------------------------------------------------------
# 常量
# ------------------------------------------------------------------

VALID_NODE_TYPES = {"Person", "Event", "Project", "Resource", "Organization"}

VALID_RELATION_TYPES = {
    # Person ↔ Person
    "REPORTS_TO",
    "ALLIES_WITH",
    "COMPETES_WITH",
    "TRUSTS",
    "DISTRUSTS",
    "INFLUENCES",
    # Person → Event
    "PARTICIPATED_IN",
    "INITIATED",
    "OPPOSED",
    # Person → Project
    "OWNS",
    "WORKS_ON",
    "SUPPORTS",
    "BLOCKS",
    # Person → Resource
    "CONTROLS",
    "COMPETES_FOR",
    # Person → Organization
    "BELONGS_TO",
    "LEADS",
}


class GraphEngine:
    """
    图谱引擎：
    - 调用 LLM 从事实文本中抽取实体与关系
    - 通过 Neo4j 的 MERGE 语义增量合并到图
    - 提供图谱上下文生成、子图查询、变化检测等能力
    """

    def __init__(self, neo4j_client: Neo4jClient):
        self.neo4j = neo4j_client
        self.client, self.model = LLMClientFactory.create_client("GRAPH_ENGINE")
        logger.info(f"GraphEngine initialized with model: {self.model}")

    # ==================================================================
    # 1. LLM 实体关系抽取
    # ==================================================================

    def extract_entities_relations(
        self, text: str, situation_context: str = "", graph_summary: str = ""
    ) -> Dict[str, Any]:
        """
        调用 LLM 从文本中抽取实体和关系，返回结构化 JSON：
        {
            "entities": [ { "name": ..., "type": ..., "properties": {...} } ],
            "relations": [ { "source": ..., "target": ..., "type": ..., "properties": {...} } ]
        }
        """
        try:
            prompt_data = PromptLoader.load_prompt("graph", "extract")
            system_msg = prompt_data["system"]
            user_msg = prompt_data["user"].format(
                situation_context=situation_context or "暂无",
                graph_summary=graph_summary or "暂无已有图谱",
                text=text,
            )

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
                response_format={"type": "json_object"},
            )
            result = json.loads(response.choices[0].message.content)

            # 校验 & 过滤非法类型
            entities = []
            for e in result.get("entities", []):
                if e.get("type") in VALID_NODE_TYPES and e.get("name"):
                    entities.append(e)
                else:
                    logger.warning(f"Filtered invalid entity: {e}")

            relations = []
            for r in result.get("relations", []):
                rtype = r.get("type", "").upper()
                if rtype in VALID_RELATION_TYPES and r.get("source") and r.get("target"):
                    r["type"] = rtype
                    relations.append(r)
                else:
                    logger.warning(f"Filtered invalid relation: {r}")

            logger.info(
                f"Extracted {len(entities)} entities, {len(relations)} relations from text."
            )
            return {"entities": entities, "relations": relations}

        except Exception as e:
            logger.error(f"Error in extract_entities_relations: {e}", exc_info=True)
            return {"entities": [], "relations": []}

    # ==================================================================
    # 2. 图谱合并写入
    # ==================================================================

    def merge_to_graph(self, user_id: str, extracted_data: Dict[str, Any]):
        """
        使用 Cypher MERGE 将抽取结果合并入 Neo4j。
        - 新实体 → 创建
        - 已有实体 → 更新 properties / updated_at
        - 关系 → MERGE 并更新 weight、evidence 等
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        entities = extracted_data.get("entities", [])
        relations = extracted_data.get("relations", [])

        # --- Merge nodes ---
        for entity in entities:
            etype = entity["type"]
            name = entity["name"].strip()
            props = entity.get("properties", {})
            # 构建 SET 子句：将 properties 展平到节点属性
            props["updated_at"] = now_iso
            props["user_id"] = user_id
            props["name"] = name

            cypher = (
                f"MERGE (n:{etype} {{user_id: $user_id, name: $name}}) "
                f"ON CREATE SET n += $props, n.created_at = $now "
                f"ON MATCH SET n += $props"
            )
            try:
                self.neo4j.run_write(
                    cypher,
                    {
                        "user_id": user_id,
                        "name": name,
                        "props": props,
                        "now": now_iso,
                    },
                )
            except Exception as e:
                logger.error(f"Error merging entity {name} ({etype}): {e}")

        # --- Merge relationships ---
        for rel in relations:
            source_name = rel["source"].strip()
            target_name = rel["target"].strip()
            rel_type = rel["type"]
            props = rel.get("properties", {})

            weight = float(props.get("weight", 0.5))
            sentiment = props.get("sentiment", "neutral")
            confidence = float(props.get("confidence", 0.5))
            evidence_item = props.get("evidence", "")

            # 需要先找到 source 和 target 节点（可能是任意类型）
            cypher = (
                f"MATCH (s {{user_id: $user_id, name: $source}}) "
                f"MATCH (t {{user_id: $user_id, name: $target}}) "
                f"MERGE (s)-[r:{rel_type}]->(t) "
                f"ON CREATE SET r.weight = $weight, r.sentiment = $sentiment, "
                f"r.confidence = $confidence, r.evidence = [$evidence], "
                f"r.created_at = $now, r.updated_at = $now "
                f"ON MATCH SET r.weight = $weight, r.sentiment = $sentiment, "
                f"r.confidence = $confidence, "
                f"r.evidence = CASE WHEN $evidence IN r.evidence THEN r.evidence "
                f"ELSE r.evidence + $evidence END, "
                f"r.updated_at = $now"
            )
            try:
                self.neo4j.run_write(
                    cypher,
                    {
                        "user_id": user_id,
                        "source": source_name,
                        "target": target_name,
                        "weight": weight,
                        "sentiment": sentiment,
                        "confidence": confidence,
                        "evidence": evidence_item if isinstance(evidence_item, str) else str(evidence_item),
                        "now": now_iso,
                    },
                )
            except Exception as e:
                logger.error(
                    f"Error merging relation {source_name}-[{rel_type}]->{target_name}: {e}"
                )

        logger.info(
            f"Merged {len(entities)} entities and {len(relations)} relations for user {user_id}."
        )

    # ==================================================================
    # 3. 抽取 + 合并一步完成（供 AdvisorService 调用）
    # ==================================================================

    def process_fact(
        self, user_id: str, fact: str, situation_context: str = ""
    ):
        """
        从事实文本中抽取实体关系并合并到图谱（端到端）。
        """
        graph_summary = self._get_graph_summary(user_id)
        extracted = self.extract_entities_relations(
            text=fact,
            situation_context=situation_context,
            graph_summary=graph_summary,
        )
        if extracted["entities"] or extracted["relations"]:
            self.merge_to_graph(user_id, extracted)
        return extracted

    # ==================================================================
    # 4. 图谱查询
    # ==================================================================

    def get_graph_data(self, user_id: str) -> Dict[str, Any]:
        """
        返回用户完整图数据（nodes + edges），供前端可视化。
        """
        # 查询所有节点
        nodes_cypher = (
            "MATCH (n) WHERE n.user_id = $user_id "
            "RETURN id(n) AS id, labels(n) AS labels, properties(n) AS props"
        )
        nodes_raw = self.neo4j.run_query(nodes_cypher, {"user_id": user_id})

        nodes = []
        for row in nodes_raw:
            label_list = row.get("labels", [])
            node_type = label_list[0] if label_list else "Unknown"
            props = row.get("props", {})
            nodes.append(
                {
                    "id": str(row["id"]),
                    "name": props.get("name", ""),
                    "type": node_type,
                    "properties": {
                        k: v
                        for k, v in props.items()
                        if k not in ("user_id",)
                    },
                }
            )

        # 查询所有关系
        edges_cypher = (
            "MATCH (s)-[r]->(t) "
            "WHERE s.user_id = $user_id AND t.user_id = $user_id "
            "RETURN id(s) AS source, id(t) AS target, type(r) AS rel_type, "
            "properties(r) AS props"
        )
        edges_raw = self.neo4j.run_query(edges_cypher, {"user_id": user_id})

        edges = []
        for row in edges_raw:
            props = row.get("props", {})
            edges.append(
                {
                    "source": str(row["source"]),
                    "target": str(row["target"]),
                    "type": row.get("rel_type", ""),
                    "weight": float(props.get("weight", 0.5)),
                    "sentiment": props.get("sentiment", "neutral"),
                    "confidence": float(props.get("confidence", 0.5)),
                    "evidence": props.get("evidence", []),
                }
            )

        return {"nodes": nodes, "edges": edges}

    def get_entity_neighborhood(
        self, user_id: str, entity_name: str, depth: int = 2
    ) -> Dict[str, Any]:
        """
        返回指定实体的 N 跳邻域子图。
        """
        cypher = (
            "MATCH (center {user_id: $user_id, name: $name}) "
            f"CALL apoc.path.subgraphAll(center, {{maxLevel: {depth}}}) "
            "YIELD nodes, relationships "
            "RETURN nodes, relationships"
        )

        # Fallback: 如果没有 APOC 插件，使用基础 Cypher
        fallback_cypher = (
            "MATCH path = (center {user_id: $user_id, name: $name})-[*1..%d]-(neighbor) "
            "WHERE neighbor.user_id = $user_id "
            "WITH collect(DISTINCT center) + collect(DISTINCT neighbor) AS all_nodes, "
            "collect(DISTINCT relationships(path)) AS all_rels_nested "
            "UNWIND all_nodes AS n "
            "WITH collect(DISTINCT n) AS nodes, all_rels_nested "
            "UNWIND all_rels_nested AS rels "
            "UNWIND rels AS r "
            "WITH nodes, collect(DISTINCT r) AS relationships "
            "RETURN nodes, relationships"
        ) % depth

        params = {"user_id": user_id, "name": entity_name}

        try:
            raw = self.neo4j.run_query(cypher, params)
        except Exception:
            logger.debug("APOC not available, using fallback Cypher for neighborhood.")
            try:
                raw = self.neo4j.run_query(fallback_cypher, params)
            except Exception as e:
                logger.error(f"Neighborhood query failed: {e}")
                return {"nodes": [], "edges": []}

        if not raw:
            return {"nodes": [], "edges": []}

        record = raw[0]
        raw_nodes = record.get("nodes", [])
        raw_rels = record.get("relationships", [])

        nodes = []
        for n in raw_nodes:
            # n might be a Neo4j Node object or dict depending on driver version
            if hasattr(n, "labels"):
                node_type = list(n.labels)[0] if n.labels else "Unknown"
                props = dict(n)
            else:
                node_type = n.get("labels", ["Unknown"])[0] if isinstance(n, dict) else "Unknown"
                props = n.get("props", n) if isinstance(n, dict) else {}

            nodes.append(
                {
                    "id": str(n.element_id if hasattr(n, "element_id") else n.get("id", "")),
                    "name": props.get("name", ""),
                    "type": node_type,
                    "properties": {
                        k: v for k, v in props.items() if k not in ("user_id",)
                    },
                }
            )

        edges = []
        for r in raw_rels:
            if hasattr(r, "type"):
                rel_type = r.type
                rel_props = dict(r)
                source_id = str(r.start_node.element_id)
                target_id = str(r.end_node.element_id)
            else:
                rel_type = r.get("type", "")
                rel_props = r.get("props", r) if isinstance(r, dict) else {}
                source_id = str(r.get("source", ""))
                target_id = str(r.get("target", ""))

            edges.append(
                {
                    "source": source_id,
                    "target": target_id,
                    "type": rel_type,
                    "weight": float(rel_props.get("weight", 0.5)),
                    "sentiment": rel_props.get("sentiment", "neutral"),
                    "confidence": float(rel_props.get("confidence", 0.5)),
                    "evidence": rel_props.get("evidence", []),
                }
            )

        return {"nodes": nodes, "edges": edges}

    # ==================================================================
    # 5. 图谱上下文（用于注入 Prompt）
    # ==================================================================

    def get_graph_context(self, user_id: str, query: str = "") -> str:
        """
        生成格式化的图谱上下文字符串，注入到 Decision/Narrative prompt 中。
        包含：关键人物及其关系、重要事件、项目状态、风险关系。
        """
        # 人物关系
        person_rels_cypher = (
            "MATCH (p:Person {user_id: $user_id})-[r]->(t {user_id: $user_id}) "
            "RETURN p.name AS source, type(r) AS rel_type, r.weight AS weight, "
            "r.sentiment AS sentiment, t.name AS target, labels(t)[0] AS target_type "
            "ORDER BY r.weight DESC LIMIT 30"
        )
        person_rels = self.neo4j.run_query(person_rels_cypher, {"user_id": user_id})

        # 所有人物节点
        persons_cypher = (
            "MATCH (p:Person {user_id: $user_id}) "
            "RETURN p.name AS name, p.role AS role, p.influence_level AS influence, "
            "p.style AS style "
            "ORDER BY p.name"
        )
        persons = self.neo4j.run_query(persons_cypher, {"user_id": user_id})

        # 近期事件
        events_cypher = (
            "MATCH (e:Event {user_id: $user_id}) "
            "RETURN e.name AS name, e.description AS description, e.date AS date "
            "ORDER BY e.updated_at DESC LIMIT 10"
        )
        events = self.neo4j.run_query(events_cypher, {"user_id": user_id})

        # 项目状态
        projects_cypher = (
            "MATCH (pj:Project {user_id: $user_id}) "
            "RETURN pj.name AS name, pj.status AS status, pj.priority AS priority "
            "ORDER BY pj.updated_at DESC LIMIT 10"
        )
        projects = self.neo4j.run_query(projects_cypher, {"user_id": user_id})

        # 构建上下文字符串
        lines = ["[局势图谱]"]

        if persons:
            lines.append("> 关键人物:")
            for p in persons:
                role_str = f", 角色:{p['role']}" if p.get("role") else ""
                inf_str = f", 影响力:{p['influence']}" if p.get("influence") else ""
                style_str = f", 风格:{p['style']}" if p.get("style") else ""
                lines.append(f"  - {p['name']}{role_str}{inf_str}{style_str}")

        if person_rels:
            lines.append("> 人物关系网:")
            for r in person_rels:
                sentiment_marker = (
                    "+" if r.get("sentiment") == "positive"
                    else "-" if r.get("sentiment") == "negative"
                    else "~"
                )
                weight_str = f"(强度:{r['weight']:.1f})" if r.get("weight") else ""
                lines.append(
                    f"  - {r['source']} --[{r['rel_type']} {sentiment_marker}]--> "
                    f"{r['target']}({r.get('target_type', '')}) {weight_str}"
                )

        if events:
            lines.append("> 关键事件:")
            for e in events:
                date_str = f" ({e['date']})" if e.get("date") else ""
                desc_str = e.get("description") or e.get("name", "")
                lines.append(f"  - {e['name']}{date_str}: {desc_str}")

        if projects:
            lines.append("> 项目状态:")
            for pj in projects:
                status_str = f" [{pj['status']}]" if pj.get("status") else ""
                lines.append(f"  - {pj['name']}{status_str}")

        if len(lines) == 1:
            lines.append("  (图谱为空，尚未积累局势数据)")

        return "\n".join(lines)

    # ==================================================================
    # 6. 图谱摘要（用于抽取 Prompt 中提供上下文）
    # ==================================================================

    def _get_graph_summary(self, user_id: str) -> str:
        """
        简要描述当前图谱内容，帮助 LLM 在抽取时避免重复/保持一致。
        """
        cypher = (
            "MATCH (n {user_id: $user_id}) "
            "RETURN labels(n)[0] AS type, n.name AS name "
            "ORDER BY n.name LIMIT 50"
        )
        results = self.neo4j.run_query(cypher, {"user_id": user_id})
        if not results:
            return "暂无已有图谱数据"

        by_type: Dict[str, List[str]] = {}
        for r in results:
            t = r.get("type", "Unknown")
            by_type.setdefault(t, []).append(r.get("name", ""))

        parts = []
        for t, names in by_type.items():
            parts.append(f"{t}: {', '.join(names)}")
        return "已有实体 - " + "; ".join(parts)

    # ==================================================================
    # 7. 变化检测
    # ==================================================================

    def detect_changes(self, user_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """
        检测最近 N 小时内的图谱变化（新增实体/关系、权重变动）。
        """
        cutoff = datetime.now(timezone.utc)
        from datetime import timedelta
        cutoff_iso = (cutoff - timedelta(hours=hours)).isoformat()

        changes = []

        # 新增节点
        new_nodes_cypher = (
            "MATCH (n {user_id: $user_id}) "
            "WHERE n.created_at >= $cutoff "
            "RETURN labels(n)[0] AS type, n.name AS name, n.created_at AS created_at"
        )
        new_nodes = self.neo4j.run_query(
            new_nodes_cypher, {"user_id": user_id, "cutoff": cutoff_iso}
        )
        for node in new_nodes:
            changes.append(
                {
                    "change_type": "new_entity",
                    "description": f"新增{node['type']}: {node['name']}",
                    "timestamp": node.get("created_at", ""),
                }
            )

        # 新增关系
        new_rels_cypher = (
            "MATCH (s {user_id: $user_id})-[r]->(t {user_id: $user_id}) "
            "WHERE r.created_at >= $cutoff "
            "RETURN s.name AS source, type(r) AS rel_type, t.name AS target, "
            "r.created_at AS created_at, r.weight AS weight, r.sentiment AS sentiment"
        )
        new_rels = self.neo4j.run_query(
            new_rels_cypher, {"user_id": user_id, "cutoff": cutoff_iso}
        )
        for rel in new_rels:
            changes.append(
                {
                    "change_type": "new_relation",
                    "description": (
                        f"新增关系: {rel['source']} -[{rel['rel_type']}]-> {rel['target']} "
                        f"(权重:{rel.get('weight', '?')}, 情感:{rel.get('sentiment', '?')})"
                    ),
                    "timestamp": rel.get("created_at", ""),
                }
            )

        # 最近更新的关系（created_at < cutoff 但 updated_at >= cutoff）
        updated_rels_cypher = (
            "MATCH (s {user_id: $user_id})-[r]->(t {user_id: $user_id}) "
            "WHERE r.updated_at >= $cutoff AND r.created_at < $cutoff "
            "RETURN s.name AS source, type(r) AS rel_type, t.name AS target, "
            "r.updated_at AS updated_at, r.weight AS weight, r.sentiment AS sentiment"
        )
        updated_rels = self.neo4j.run_query(
            updated_rels_cypher, {"user_id": user_id, "cutoff": cutoff_iso}
        )
        for rel in updated_rels:
            changes.append(
                {
                    "change_type": "updated_relation",
                    "description": (
                        f"关系更新: {rel['source']} -[{rel['rel_type']}]-> {rel['target']} "
                        f"(当前权重:{rel.get('weight', '?')}, 情感:{rel.get('sentiment', '?')})"
                    ),
                    "timestamp": rel.get("updated_at", ""),
                }
            )

        logger.info(f"Detected {len(changes)} graph changes in last {hours}h for user {user_id}.")
        return changes

    # ==================================================================
    # 8. 中心性 / 洞察分析
    # ==================================================================

    def get_centrality_analysis(self, user_id: str) -> Dict[str, Any]:
        """
        计算图谱洞察：
        - 关键人物（按连接数排序）
        - 风险关系（负面情感 / 高权重对抗）
        - 孤立节点
        """
        # 度中心性（简化版：统计连接数）
        degree_cypher = (
            "MATCH (p:Person {user_id: $user_id})-[r]-() "
            "RETURN p.name AS name, count(r) AS degree "
            "ORDER BY degree DESC LIMIT 10"
        )
        degree_results = self.neo4j.run_query(degree_cypher, {"user_id": user_id})

        key_players = [
            {"name": r["name"], "centrality": r["degree"]}
            for r in degree_results
        ]

        # 风险关系
        risk_cypher = (
            "MATCH (s {user_id: $user_id})-[r]->(t {user_id: $user_id}) "
            "WHERE r.sentiment = 'negative' OR type(r) IN ['COMPETES_WITH', 'DISTRUSTS', 'BLOCKS', 'OPPOSED'] "
            "RETURN s.name AS source, type(r) AS rel_type, t.name AS target, "
            "r.weight AS weight, r.sentiment AS sentiment, r.evidence AS evidence "
            "ORDER BY r.weight DESC"
        )
        risk_results = self.neo4j.run_query(risk_cypher, {"user_id": user_id})

        risk_relations = [
            {
                "source": r["source"],
                "target": r["target"],
                "type": r["rel_type"],
                "weight": float(r.get("weight", 0)),
                "sentiment": r.get("sentiment", "negative"),
                "confidence": 0.0,
                "evidence": r.get("evidence", []),
            }
            for r in risk_results
        ]

        # 近期变化
        recent_changes = self.detect_changes(user_id, hours=72)

        return {
            "key_players": key_players,
            "risk_relations": risk_relations,
            "recent_changes": [
                {"description": c["description"], "timestamp": c["timestamp"]}
                for c in recent_changes[:20]
            ],
        }

    # ==================================================================
    # 9. 删除操作
    # ==================================================================

    def clear_graph(self, user_id: str):
        """清空用户的全部图谱数据。"""
        cypher = (
            "MATCH (n {user_id: $user_id}) DETACH DELETE n"
        )
        self.neo4j.run_write(cypher, {"user_id": user_id})
        logger.info(f"Cleared all graph data for user {user_id}.")

    def delete_entity(self, user_id: str, entity_name: str):
        """删除指定实体及其所有关系。"""
        cypher = (
            "MATCH (n {user_id: $user_id, name: $name}) DETACH DELETE n"
        )
        self.neo4j.run_write(cypher, {"user_id": user_id, "name": entity_name})
        logger.info(f"Deleted entity '{entity_name}' for user {user_id}.")
