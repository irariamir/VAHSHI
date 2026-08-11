"""
VAHSHI Memory Store — SQLite + FTS5 (Hermes-inspired)
سه لایه: MEMORY.md + USER.md + SessionDB FTS5
"""
import sqlite3
import pathlib
import datetime
import os

DEFAULT_DB = pathlib.Path("data/sessions/state.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    created_at TEXT,
    updated_at TEXT,
    title TEXT,
    summary TEXT
);
CREATE TABLE IF NOT EXISTS turns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    role TEXT,
    content TEXT,
    created_at TEXT,
    FOREIGN KEY(session_id) REFERENCES sessions(id)
);
-- FTS5 for full-text search
CREATE VIRTUAL TABLE IF NOT EXISTS turns_fts USING fts5(content, content='turns', content_rowid='id', tokenize='porter unicode61');
CREATE TRIGGER IF NOT EXISTS turns_ai AFTER INSERT ON turns BEGIN
  INSERT INTO turns_fts(rowid, content) VALUES (new.id, new.content);
END;
CREATE TRIGGER IF NOT EXISTS turns_ad AFTER DELETE ON turns BEGIN
  INSERT INTO turns_fts(turns_fts, rowid, content) VALUES('delete', old.id, old.content);
END;
CREATE TRIGGER IF NOT EXISTS turns_au AFTER UPDATE ON turns BEGIN
  INSERT INTO turns_fts(turns_fts, rowid, content) VALUES('delete', old.id, old.content);
  INSERT INTO turns_fts(rowid, content) VALUES (new.id, new.content);
END;
"""

class MemoryStore:
    def __init__(self, db_path: str | pathlib.Path = DEFAULT_DB):
        self.db_path = pathlib.Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def ensure_session(self, session_id: str, title: str = ""):
        now = datetime.datetime.utcnow().isoformat()
        self.conn.execute(
            "INSERT OR IGNORE INTO sessions (id, created_at, updated_at, title) VALUES (?,?,?,?)",
            (session_id, now, now, title)
        )
        self.conn.commit()

    def add_turn(self, session_id: str, role: str, content: str):
        self.ensure_session(session_id)
        now = datetime.datetime.utcnow().isoformat()
        self.conn.execute(
            "INSERT INTO turns (session_id, role, content, created_at) VALUES (?,?,?,?)",
            (session_id, role, content, now)
        )
        self.conn.execute("UPDATE sessions SET updated_at=? WHERE id=?", (now, session_id))
        self.conn.commit()

    def search(self, query: str, limit: int = 10) -> list[dict]:
        """FTS5 search + anchored window"""
        try:
            cur = self.conn.execute(
                """
                SELECT t.session_id, t.role, t.content, t.created_at, rank
                FROM turns_fts
                JOIN turns t ON t.id = turns_fts.rowid
                WHERE turns_fts MATCH ?
                ORDER BY rank LIMIT ?
                """,
                (query, limit)
            )
            rows = cur.fetchall()
            return [{"session_id": r[0], "role": r[1], "content": r[2], "created_at": r[3]} for r in rows]
        except sqlite3.OperationalError:
            # fallback LIKE
            cur = self.conn.execute(
                "SELECT session_id, role, content, created_at FROM turns WHERE content LIKE ? LIMIT ?",
                (f"%{query}%", limit)
            )
            return [{"session_id": r[0], "role": r[1], "content": r[2], "created_at": r[3]} for r in cur.fetchall()]

    def recent_turns(self, session_id: str, n: int = 20) -> list[dict]:
        cur = self.conn.execute(
            "SELECT role, content, created_at FROM turns WHERE session_id=? ORDER BY id DESC LIMIT ?",
            (session_id, n)
        )
        rows = cur.fetchall()
        return list(reversed([{"role": r[0], "content": r[1], "created_at": r[2]} for r in rows]))

    def summarize_session(self, session_id: str) -> str:
        turns = self.recent_turns(session_id, 30)
        if not turns:
            return "سشن خالی"
        # simple extractive summary
        user_msgs = [t["content"][:120] for t in turns if t["role"] == "user"][-5:]
        return " | ".join(user_msgs) if user_msgs else turns[-1]["content"][:200]

# singleton
_store = None
def get_store() -> MemoryStore:
    global _store
    if _store is None:
        _store = MemoryStore()
    return _store
