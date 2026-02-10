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
