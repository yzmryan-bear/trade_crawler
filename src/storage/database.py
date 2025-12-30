"""Database layer for storing messages and trading actions."""

import sqlite3
import os
from typing import List, Optional
from datetime import datetime
from ..models.message import Message
from ..models.trading_action import TradingAction


class Database:
    """SQLite database for storing messages and trading actions."""
    
    def __init__(self, db_path: str = "./data/trading_actions.db"):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_schema()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_schema(self) -> None:
        """Initialize database schema."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT NOT NULL,
                send_time TEXT NOT NULL,
                message TEXT NOT NULL,
                channel TEXT,
                message_id TEXT,
                platform TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(platform, message_id) ON CONFLICT IGNORE
            )
        """)
        
        # Trading actions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trading_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER,
                action_type TEXT NOT NULL,
                symbol TEXT NOT NULL,
                price REAL,
                quantity INTEGER,
                confidence REAL NOT NULL,
                raw_message TEXT,
                extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                action_signal_time TEXT,
                FOREIGN KEY (message_id) REFERENCES messages(id),
                CHECK (confidence >= 0.0 AND confidence <= 1.0)
            )
        """)
        
        # Add action_signal_time column if it doesn't exist (for existing databases)
        try:
            cursor.execute("ALTER TABLE trading_actions ADD COLUMN action_signal_time TEXT")
        except sqlite3.OperationalError:
            # Column already exists, ignore
            pass
        
        # Create indexes for better query performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_sender 
            ON messages(sender)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_send_time 
            ON messages(send_time)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_trading_actions_symbol 
            ON trading_actions(symbol)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_trading_actions_confidence 
            ON trading_actions(confidence)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_trading_actions_extracted_at 
            ON trading_actions(extracted_at)
        """)
        
        conn.commit()
        conn.close()
    
    def save_message(self, message: Message) -> int:
        """Save a message to the database.
        
        Args:
            message: Message object to save
        
        Returns:
            Database ID of saved message
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO messages (sender, send_time, message, channel, message_id, platform)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            message.sender,
            message.send_time,
            message.message,
            message.channel,
            message.message_id,
            message.platform
        ))
        
        message_db_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return message_db_id
    
    def save_trading_action(self, action: TradingAction, message_db_id: Optional[int] = None) -> int:
        """Save a trading action to the database.
        
        Args:
            action: TradingAction object to save
            message_db_id: Database ID of associated message (optional)
        
        Returns:
            Database ID of saved trading action
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        extracted_at = action.extracted_at or datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO trading_actions 
            (message_id, action_type, symbol, price, quantity, confidence, raw_message, extracted_at, action_signal_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            message_db_id,
            action.action_type.value,
            action.symbol,
            action.price,
            action.quantity,
            action.confidence,
            action.raw_message,
            extracted_at,
            action.action_signal_time
        ))
        
        action_db_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return action_db_id
    
    def get_recent_messages(self, limit: int = 100) -> List[dict]:
        """Get recent messages from database.
        
        Args:
            limit: Maximum number of messages to retrieve
        
        Returns:
            List of message dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM messages 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_recent_actions(self, limit: int = 100, min_confidence: float = 0.0) -> List[dict]:
        """Get recent trading actions from database.
        
        Args:
            limit: Maximum number of actions to retrieve
            min_confidence: Minimum confidence threshold
        
        Returns:
            List of trading action dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ta.*, m.sender, m.send_time, m.message
            FROM trading_actions ta
            LEFT JOIN messages m ON ta.message_id = m.id
            WHERE ta.confidence >= ?
            ORDER BY ta.extracted_at DESC
            LIMIT ?
        """, (min_confidence, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_action_statistics(self) -> dict:
        """Get statistics about trading actions.
        
        Returns:
            Dictionary with statistics
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Total actions
        cursor.execute("SELECT COUNT(*) FROM trading_actions")
        total = cursor.fetchone()[0]
        
        # Actions by type
        cursor.execute("""
            SELECT action_type, COUNT(*) as count 
            FROM trading_actions 
            GROUP BY action_type
        """)
        by_type = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Average confidence
        cursor.execute("SELECT AVG(confidence) FROM trading_actions")
        avg_confidence = cursor.fetchone()[0] or 0.0
        
        # Actions by symbol (top 10)
        cursor.execute("""
            SELECT symbol, COUNT(*) as count 
            FROM trading_actions 
            GROUP BY symbol 
            ORDER BY count DESC 
            LIMIT 10
        """)
        top_symbols = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            "total_actions": total,
            "by_type": by_type,
            "average_confidence": round(avg_confidence, 3),
            "top_symbols": top_symbols
        }

