#!/usr/bin/env python3
"""
ARAS Memory System
Short-term (conversation) + Long-term (SQLite) memory
"""

import os
import json
import sqlite3
from datetime import datetime
from collections import deque

# Paths
AGENT_DIR = os.path.dirname(os.path.dirname(__file__))
MEMORY_DIR = os.path.join(AGENT_DIR, "memory")
SHORT_TERM_FILE = os.path.join(MEMORY_DIR, "short_term.json")
LONG_TERM_DB = os.path.join(MEMORY_DIR, "long_term.db")

os.makedirs(MEMORY_DIR, exist_ok=True)

# === SHORT-TERM MEMORY (RAM/JSON) ===
class ShortTermMemory:
    """Fast conversation memory - recent messages"""
    def __init__(self, max_items=20):
        self.max_items = max_items
        self.messages = deque(maxlen=max_items)
        self.load()
    
    def load(self):
        """Load from file"""
        if os.path.exists(SHORT_TERM_FILE):
            try:
                with open(SHORT_TERM_FILE, "r") as f:
                    data = json.load(f)
                    self.messages = deque(data, maxlen=self.max_items)
            except:
                pass
    
    def save(self):
        """Save to file"""
        with open(SHORT_TERM_FILE, "w") as f:
            json.dump(list(self.messages), f)
    
    def add(self, role, content):
        """Add message to memory"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.save()
    
    def get_context(self, max_chars=2000):
        """Get conversation context"""
        context = ""
        for msg in self.messages:
            prefix = "User: " if msg["role"] == "user" else "ARAS: "
            context += prefix + msg["content"] + "\n"
        
        # Truncate if too long
        if len(context) > max_chars:
            context = context[-max_chars:]
        
        return context
    
    def clear(self):
        """Clear short-term memory"""
        self.messages.clear()
        self.save()


# === LONG-TERM MEMORY (SQLite) ===
class LongTermMemory:
    """Persistent memory - facts, preferences, learned info"""
    def __init__(self):
        self.conn = sqlite3.connect(LONG_TERM_DB, check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        """Create memory tables"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE,
                value TEXT,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
    
    def remember(self, key, value, category="general"):
        """Store a memory"""
        self.conn.execute("""
            INSERT OR REPLACE INTO memories (key, value, category, updated_at)
            VALUES (?, ?, ?, ?)
        """, (key, value, category, datetime.now().isoformat()))
        self.conn.commit()
        print(f"[MEMORY] Remembered: {key}")
    
    def recall(self, key):
        """Recall a memory"""
        cursor = self.conn.execute(
            "SELECT value FROM memories WHERE key = ?", (key,)
        )
        row = cursor.fetchone()
        return row[0] if row else None
    
    def search(self, query, limit=5):
        """Search memories"""
        cursor = self.conn.execute("""
            SELECT key, value FROM memories 
            WHERE key LIKE ? OR value LIKE ?
            ORDER BY updated_at DESC LIMIT ?
        """, (f"%{query}%", f"%{query}%", limit))
        return cursor.fetchall()
    
    def get_all(self, category=None):
        """Get all memories"""
        if category:
            cursor = self.conn.execute(
                "SELECT key, value FROM memories WHERE category = ? ORDER BY updated_at DESC",
                (category,)
            )
        else:
            cursor = self.conn.execute(
                "SELECT key, value FROM memories ORDER BY updated_at DESC"
            )
        return cursor.fetchall()
    
    def forget(self, key):
        """Delete a memory"""
        self.conn.execute("DELETE FROM memories WHERE key = ?", (key,))
        self.conn.commit()
    
    def clear_all(self):
        """Clear all long-term memories"""
        self.conn.execute("DELETE FROM memories")
        self.conn.commit()


# Global instances
short_memory = ShortTermMemory()
long_memory = LongTermMemory()


# === AGENT MEMORY FUNCTIONS ===

def add_to_memory(role, content):
    """Add to short-term memory"""
    short_memory.add(role, content)


def get_memory_context():
    """Get conversation context"""
    return short_memory.get_context()


def remember_fact(key, value, category="fact"):
    """Store important info"""
    long_memory.remember(key, value, category)


def recall_fact(key):
    """Recall stored info"""
    return long_memory.recall(key)


def search_memory(query):
    """Search long-term memory"""
    return long_memory.search(query)


def clear_memory():
    """Clear all memory"""
    short_memory.clear()
    long_memory.clear_all()
    print("[MEMORY] All memories cleared")


# Auto-learn user preferences
def learn_user_preference(user_id, preference):
    """Learn user preferences"""
    long_memory.remember(f"user_{preference}", preference, "preference")


def get_user_preferences(user_id):
    """Get user preferences"""
    prefs = long_memory.search(f"user_", limit=10)
    return prefs
