import sqlite3
import json
import os
from typing import Optional, Dict, Any
from src.core.situation import SituationModel
from src.core.logger import logger

class DatabaseManager:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default to data/app.db relative to project root
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            data_dir = os.path.join(base_dir, "data")
            os.makedirs(data_dir, exist_ok=True)
            self.db_path = os.path.join(data_dir, "app.db")
        else:
            self.db_path = db_path
            
        logger.info(f"Database initialized at: {self.db_path}")
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Initialize database schema"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Create user_situations table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_situations (
                        user_id TEXT PRIMARY KEY,
                        data TEXT NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create user_feedback table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_feedback (
                        id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        fact TEXT,
                        advice_result TEXT,
                        rating INTEGER, -- 1-5
                        comment TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_persona_versions (
                        id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        person_name TEXT NOT NULL,
                        person_title TEXT,
                        persona TEXT NOT NULL,
                        deviation_summary TEXT,
                        confidence REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_user_persona_versions_lookup
                    ON user_persona_versions (user_id, person_name, created_at)
                """)
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}", exc_info=True)

    def save_feedback(self, feedback_data: Dict[str, Any]):
        """Save user feedback"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO user_feedback (id, user_id, fact, advice_result, rating, comment, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    feedback_data.get("id"),
                    feedback_data.get("user_id"),
                    feedback_data.get("fact"),
                    json.dumps(feedback_data.get("advice_result"), ensure_ascii=False),
                    feedback_data.get("rating"),
                    feedback_data.get("comment")
                ))
                conn.commit()
            logger.debug(f"Saved feedback for user {feedback_data.get('user_id')}")
        except sqlite3.Error as e:
            logger.error(f"Error saving feedback: {e}", exc_info=True)

    def save_situation(self, user_id: str, situation: SituationModel):
        """Save or update user situation"""
        data_json = situation.model_dump_json()
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO user_situations (user_id, data, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (user_id, data_json))
                conn.commit()
            logger.debug(f"Saved situation for user {user_id}")
        except sqlite3.Error as e:
            logger.error(f"Error saving situation for user {user_id}: {e}", exc_info=True)

    def get_situation(self, user_id: str) -> Optional[SituationModel]:
        """Get user situation by user_id"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT data FROM user_situations WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
                
                if row:
                    data_dict = json.loads(row[0])
                    return SituationModel(**data_dict)
                return None
        except sqlite3.Error as e:
            logger.error(f"Error getting situation for user {user_id}: {e}", exc_info=True)
            return None

    def delete_situation(self, user_id: str):
        """Delete user situation"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM user_situations WHERE user_id = ?", (user_id,))
                conn.commit()
            logger.debug(f"Deleted situation for user {user_id}")
        except sqlite3.Error as e:
            logger.error(f"Error deleting situation for user {user_id}: {e}", exc_info=True)

    def save_persona_version(
        self,
        persona_id: str,
        user_id: str,
        person_name: str,
        persona: str,
        person_title: str = "",
        deviation_summary: str = "",
        confidence: float = 0.0,
    ):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO user_persona_versions
                    (id, user_id, person_name, person_title, persona, deviation_summary, confidence, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """,
                    (
                        persona_id,
                        user_id,
                        person_name,
                        person_title,
                        persona,
                        deviation_summary,
                        confidence,
                    ),
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.error(
                f"Error saving persona version for user {user_id} person {person_name}: {e}",
                exc_info=True,
            )

    def get_latest_persona(self, user_id: str, person_name: str) -> Optional[Dict[str, Any]]:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, person_title, persona, deviation_summary, confidence, created_at
                    FROM user_persona_versions
                    WHERE user_id = ? AND person_name = ?
                    ORDER BY created_at DESC
                    LIMIT 1
                    """,
                    (user_id, person_name),
                )
                row = cursor.fetchone()
                if not row:
                    return None
                return {
                    "id": row[0],
                    "person_title": row[1],
                    "persona": row[2],
                    "deviation_summary": row[3],
                    "confidence": row[4],
                    "created_at": row[5],
                }
        except sqlite3.Error as e:
            logger.error(
                f"Error getting latest persona for user {user_id} person {person_name}: {e}",
                exc_info=True,
            )
            return None

    def list_persona_versions(self, user_id: str, person_name: str, limit: int = 50) -> list[Dict[str, Any]]:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, person_title, persona, deviation_summary, confidence, created_at
                    FROM user_persona_versions
                    WHERE user_id = ? AND person_name = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                    """,
                    (user_id, person_name, limit),
                )
                rows = cursor.fetchall()
                return [
                    {
                        "id": r[0],
                        "person_title": r[1],
                        "persona": r[2],
                        "deviation_summary": r[3],
                        "confidence": r[4],
                        "created_at": r[5],
                    }
                    for r in rows
                ]
        except sqlite3.Error as e:
            logger.error(
                f"Error listing persona versions for user {user_id} person {person_name}: {e}",
                exc_info=True,
            )
            return []

    def get_persona_version(self, persona_id: str) -> Optional[Dict[str, Any]]:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, user_id, person_name, person_title, persona, deviation_summary, confidence, created_at
                    FROM user_persona_versions
                    WHERE id = ?
                    LIMIT 1
                    """,
                    (persona_id,),
                )
                row = cursor.fetchone()
                if not row:
                    return None
                return {
                    "id": row[0],
                    "user_id": row[1],
                    "person_name": row[2],
                    "person_title": row[3],
                    "persona": row[4],
                    "deviation_summary": row[5],
                    "confidence": row[6],
                    "created_at": row[7],
                }
        except sqlite3.Error as e:
            logger.error(f"Error getting persona version {persona_id}: {e}", exc_info=True)
            return None
