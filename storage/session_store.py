"""
会话存储 - SQLite 存储会话历史
注意：确保使用 UTF-8 编码存储中文
"""
import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
from config.settings import DB_PATH

logger = logging.getLogger(__name__)

class SessionStore:
    """会话存储类"""
    
    def __init__(self):
        self.db_path = DB_PATH
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # 设置 UTF-8 编码
                conn.execute("PRAGMA encoding = 'UTF-8'")
                conn.execute("PRAGMA foreign_keys = ON")
                
                cursor = conn.cursor()
                
                # 会话表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT DEFAULT 'default',
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 用户偏好表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS preferences (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    )
                ''')
                
                conn.commit()
                logger.info(f"数据库初始化成功：{self.db_path}")
        except Exception as e:
            logger.error(f"数据库初始化失败：{e}")
            raise
    
    def add_message(self, role: str, content: str, user_id: str = "default"):
        """添加消息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # 设置 UTF-8
                conn.execute("PRAGMA encoding = 'UTF-8'")
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO sessions (user_id, role, content, timestamp)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, role, content, datetime.now()))
                conn.commit()
                logger.debug(f"Message saved: {role}: {content[:20]}...")
        except Exception as e:
            logger.error(f"添加消息失败：{e}")
            raise
    
    def get_history(self, user_id: str = "default", limit: int = 50) -> List[Dict]:
        """获取历史消息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # 设置 UTF-8
                conn.execute("PRAGMA encoding = 'UTF-8'")
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT role, content, timestamp
                    FROM sessions
                    WHERE user_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (user_id, limit))
                
                rows = cursor.fetchall()
                result = [dict(row) for row in rows]
                logger.debug(f"Retrieved {len(result)} history items")
                return result
                
        except Exception as e:
            logger.error(f"获取历史失败：{e}")
            return []
    
    def clear_history(self, user_id: str = "default"):
        """清空历史"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA encoding = 'UTF-8'")
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM sessions
                    WHERE user_id = ?
                ''', (user_id,))
                conn.commit()
                logger.info(f"History cleared for user: {user_id}")
        except Exception as e:
            logger.error(f"清空历史失败：{e}")
    
    def save_preference(self, key: str, value):
        """保存偏好设置"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA encoding = 'UTF-8'")
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO preferences (key, value)
                    VALUES (?, ?)
                ''', (key, json.dumps(value, ensure_ascii=False)))
                conn.commit()
        except Exception as e:
            logger.error(f"保存偏好失败：{e}")
    
    def get_preference(self, key: str, default=None):
        """获取偏好设置"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA encoding = 'UTF-8'")
                cursor = conn.cursor()
                cursor.execute('SELECT value FROM preferences WHERE key = ?', (key,))
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])
                return default
        except Exception as e:
            logger.error(f"获取偏好失败：{e}")
            return default

# 全局会话存储实例
session_store = SessionStore()
