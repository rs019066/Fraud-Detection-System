"""
Visualization & Real-Time Log Routes
Plugs into existing main.py with zero breaking changes
"""

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import asyncio
import json
from datetime import datetime, timedelta

# These imports reference classes already in main.py
# We import them here to avoid circular imports
from auth.dependencies import get_current_user

visualization_router = APIRouter(prefix="/api/viz", tags=["visualization"])

# ── WebSocket connection manager ──────────────────────────────────────────────

class LogConnectionManager:
    """Broadcasts real-time prediction events to all connected WebSocket clients."""
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            self.disconnect(conn)

# Singleton — import this in main.py to call broadcast() after each prediction
log_manager = LogConnectionManager()


# ── Chart data endpoint ───────────────────────────────────────────────────────

@visualization_router.get("/charts")
async def get_chart_data(
    db: Session = Depends(lambda: None),   # replaced below via dependency override
    current_user: dict = Depends(get_current_user)
):
    """
    Returns all chart data in one call so the frontend makes a single request.
    Role-aware: analysts see only their own data, admins see everything.
    """
    from main import TransactionDB, SessionLocal, TransactionRepository

    db = SessionLocal()
    try:
        user_id = current_user.get("user_id")
        role    = current_user.get("role")

        base_query = db.query(TransactionDB)
        if role == "analyst":
            base_query = base_query.filter(TransactionDB.created_by_user_id == user_id)

        transactions = base_query.order_by(TransactionDB.created_at.asc()).all()

        # ── Fraud vs Legitimate (bar / pie) ──────────────────────────────
        total      = len(transactions)
        fraud_cnt  = sum(1 for t in transactions if t.is_fraud)
        legit_cnt  = total - fraud_cnt

        fraud_vs_legit = [
            {"name": "Legitimate", "value": legit_cnt, "color": "#22c55e"},
            {"name": "Fraudulent", "value": fraud_cnt, "color": "#ef4444"},
        ]

        # ── Risk level distribution ───────────────────────────────────────
        risk_buckets = {"MINIMAL": 0, "LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        for t in transactions:
            p = t.fraud_probability or 0
            if   p >= 0.90: risk_buckets["CRITICAL"] += 1
            elif p >= 0.70: risk_buckets["HIGH"]     += 1
            elif p >= 0.40: risk_buckets["MEDIUM"]   += 1
            elif p >= 0.20: risk_buckets["LOW"]      += 1
            else:           risk_buckets["MINIMAL"]  += 1

        risk_distribution = [
            {"name": k, "count": v,
             "color": {"MINIMAL":"#22c55e","LOW":"#86efac","MEDIUM":"#facc15",
                       "HIGH":"#f97316","CRITICAL":"#ef4444"}[k]}
            for k, v in risk_buckets.items()
        ]

        # ── Transaction volume over time (last 14 days, daily) ───────────
        cutoff = datetime.utcnow() - timedelta(days=14)
        recent = [t for t in transactions if t.created_at and t.created_at >= cutoff]

        daily: dict = {}
        for t in recent:
            day = t.created_at.strftime("%m/%d")
            if day not in daily:
                daily[day] = {"date": day, "total": 0, "fraud": 0, "legit": 0}
            daily[day]["total"] += 1
            if t.is_fraud:
                daily[day]["fraud"] += 1
            else:
                daily[day]["legit"] += 1

        volume_over_time = list(daily.values())

        # ── Amount distribution buckets ───────────────────────────────────
        amount_buckets = {"$0–50": 0, "$50–200": 0, "$200–500": 0,
                          "$500–1k": 0, "$1k+": 0}
        for t in transactions:
            a = t.transaction_amount or 0
            if   a <   50: amount_buckets["$0–50"]    += 1
            elif a <  200: amount_buckets["$50–200"]  += 1
            elif a <  500: amount_buckets["$200–500"] += 1
            elif a < 1000: amount_buckets["$500–1k"]  += 1
            else:          amount_buckets["$1k+"]     += 1

        amount_distribution = [{"range": k, "count": v} for k, v in amount_buckets.items()]

        # ── Hourly fraud pattern ──────────────────────────────────────────
        hour_data = [{"hour": h, "fraud": 0, "total": 0} for h in range(24)]
        for t in transactions:
            h = t.transaction_hour or 0
            hour_data[h]["total"] += 1
            if t.is_fraud:
                hour_data[h]["fraud"] += 1

        return {
            "summary": {
                "total": total,
                "fraud": fraud_cnt,
                "legit": legit_cnt,
                "fraud_rate": round((fraud_cnt / total * 100), 1) if total else 0,
            },
            "fraud_vs_legit":    fraud_vs_legit,
            "risk_distribution": risk_distribution,
            "volume_over_time":  volume_over_time,
            "amount_distribution": amount_distribution,
            "hourly_pattern":    hour_data,
        }
    finally:
        db.close()


# ── WebSocket real-time log ───────────────────────────────────────────────────

@visualization_router.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """
    Clients connect here to receive a live JSON event every time
    a prediction is made anywhere in the system.
    No auth on WS (token passed as query param if needed later).
    """
    await log_manager.connect(websocket)
    try:
        # Keep alive — client can send pings, we ignore them
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        log_manager.disconnect(websocket)