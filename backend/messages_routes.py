# ============================================================
# messages_routes.py  —  FastAPI version
# ============================================================
# Your main.py already has:
#   from messages_routes import messages_router   ← already correct!
#   app.include_router(messages_router)           ← already correct!
#
# Uses python-jose (same as your auth module) and matches
# your JWT payload: {"sub": username, "role": role, "user_id": id}
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from jose import JWTError, jwt          # same library you already use
import sqlite3, os

# ── Reuse your existing Config (SECRET_KEY, ALGORITHM) ──────
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from config import Config

# ── Router (named messages_router to match your main.py import) ──
messages_router = APIRouter(prefix="/api/messages", tags=["messages"])

DB_PATH = os.path.join(os.path.dirname(__file__), "fraud_detection.db")
security = HTTPBearer(auto_error=False)


# ── DB ───────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_messages_table():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS contact_messages (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER,
            username    TEXT,
            name        TEXT NOT NULL,
            email       TEXT,
            subject     TEXT NOT NULL,
            message     TEXT NOT NULL,
            status      TEXT DEFAULT 'pending',
            reply       TEXT,
            replied_at  TEXT,
            created_at  TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


create_messages_table()   # auto-creates table on startup, no migration needed


def row_to_dict(row):
    return dict(row) if row else None


# ── Auth helpers (matches your JWT payload exactly) ──────────

def decode_token(token: str) -> Optional[dict]:
    """Decode using python-jose + your Config keys."""
    try:
        return jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
    except JWTError:
        return None


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
):
    """Returns decoded payload or None — used for endpoints open to guests too."""
    if not credentials:
        return None
    return decode_token(credentials.credentials)


def get_required_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
):
    """Returns decoded payload or raises 401."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload


def get_admin_user(user=Depends(get_required_user)):
    """Raises 403 if not admin."""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


# ── Schemas ───────────────────────────────────────────────────

class MessageCreate(BaseModel):
    name: str
    email: Optional[str] = ""
    subject: str
    message: str


class ReplyCreate(BaseModel):
    reply: str


# ── Endpoints ─────────────────────────────────────────────────

# POST /api/messages  — works for guests AND logged-in users
@messages_router.post("", status_code=201)
async def submit_message(
    body: MessageCreate,
    user=Depends(get_optional_user),
):
    if not body.name.strip() or not body.subject.strip() or not body.message.strip():
        raise HTTPException(status_code=400, detail="name, subject and message are required")

    # JWT payload uses "sub" for username and "user_id" for id (matches your auth module)
    user_id  = user.get("user_id") if user else None
    username = user.get("sub")     if user else None

    conn = get_db()
    cursor = conn.execute(
        """INSERT INTO contact_messages
           (user_id, username, name, email, subject, message, status, created_at)
           VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)""",
        (
            user_id,
            username,
            body.name.strip(),
            body.email or "",
            body.subject.strip(),
            body.message.strip(),
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM contact_messages WHERE id = ?", (cursor.lastrowid,)
    ).fetchone()
    conn.close()
    return row_to_dict(row)


# GET /api/messages  — Admin: all messages
@messages_router.get("")
async def get_all_messages(admin=Depends(get_admin_user)):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM contact_messages ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


# GET /api/messages/my  — Logged-in user: their own messages + replies
@messages_router.get("/my")
async def get_my_messages(user=Depends(get_required_user)):
    user_id = user.get("user_id")   # matches your JWT payload
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM contact_messages WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


# POST /api/messages/{id}/reply  — Admin: send or update reply
@messages_router.post("/{msg_id}/reply")
async def reply_to_message(
    msg_id: int,
    body: ReplyCreate,
    admin=Depends(get_admin_user),
):
    if not body.reply.strip():
        raise HTTPException(status_code=400, detail="reply text is required")

    now = datetime.now(timezone.utc).isoformat()
    conn = get_db()
    conn.execute(
        "UPDATE contact_messages SET reply=?, replied_at=?, status='replied' WHERE id=?",
        (body.reply.strip(), now, msg_id),
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM contact_messages WHERE id = ?", (msg_id,)
    ).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Message not found")
    return row_to_dict(row)


# PATCH /api/messages/{id}/read  — Admin: mark as read
@messages_router.patch("/{msg_id}/read")
async def mark_as_read(msg_id: int, admin=Depends(get_admin_user)):
    conn = get_db()
    conn.execute(
        "UPDATE contact_messages SET status='read' WHERE id=? AND status='pending'",
        (msg_id,),
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM contact_messages WHERE id = ?", (msg_id,)
    ).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Message not found")
    return row_to_dict(row)