from datetime import datetime, timedelta

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

from .config import settings
from .correlation import update_risk_and_alerts
from .database import Base, engine, get_db
from .models import Alert, Event, IPRiskScore
from .schemas import (
    AlertsResponse,
    CredentialHeatmapResponse,
    CredentialStat,
    EventCreate,
    OverviewStats,
    TimelinePoint,
    TimelineResponse,
    TopIP,
    TopIPsResponse,
)


# Create tables on startup (simple approach instead of migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="HoneyShield SIEM API")

# Allow local frontend dev by default
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.post(f"{settings.API_PREFIX}/ingest/ssh", response_model=None)
async def ingest_ssh_event(payload: EventCreate, db: Session = Depends(get_db)):
    # Normalize event
    event = Event(
        timestamp=payload.timestamp or datetime.utcnow(),
        source_ip=payload.source_ip,
        username=payload.username,
        password=payload.password,
        port=payload.port,
        protocol=payload.protocol,
        success=payload.success,
        raw=payload.raw,
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    # Correlation + risk scoring
    update_risk_and_alerts(db, event)

    return {"status": "ok"}


@app.get(f"{settings.API_PREFIX}/stats/overview", response_model=OverviewStats)
async def get_overview_stats(db: Session = Depends(get_db)):
    total_events = db.query(func.count(Event.id)).scalar() or 0
    unique_ips = db.query(func.count(func.distinct(Event.source_ip))).scalar() or 0
    high_risk_ips = (
        db.query(func.count(IPRiskScore.id))
        .filter(IPRiskScore.score >= 20.0)
        .scalar()
        or 0
    )
    open_alerts = db.query(func.count(Alert.id)).filter(Alert.resolved.is_(False)).scalar() or 0

    return OverviewStats(
        total_events=total_events,
        unique_ips=unique_ips,
        high_risk_ips=high_risk_ips,
        open_alerts=open_alerts,
    )


@app.get(f"{settings.API_PREFIX}/stats/timeline", response_model=TimelineResponse)
async def get_timeline(db: Session = Depends(get_db)):
    # Group by 10-minute buckets for demo purposes
    now = datetime.utcnow()
    window_start = now - timedelta(hours=6)

    rows = (
        db.query(
            func.date_trunc("hour", Event.timestamp).label("bucket"),
            func.count(Event.id),
        )
        .filter(Event.timestamp >= window_start)
        .group_by("bucket")
        .order_by("bucket")
        .all()
    )

    points = [
        TimelinePoint(bucket_start=row[0], count=row[1])
        for row in rows
    ]

    return TimelineResponse(points=points)


@app.get(f"{settings.API_PREFIX}/stats/top-ips", response_model=TopIPsResponse)
async def get_top_ips(db: Session = Depends(get_db), limit: int = 10):
    rows = (
        db.query(
            Event.source_ip,
            func.count(Event.id).label("events"),
            func.coalesce(IPRiskScore.score, 0.0).label("score"),
        )
        .outerjoin(IPRiskScore, IPRiskScore.ip == Event.source_ip)
        .group_by(Event.source_ip, IPRiskScore.score)
        .order_by(func.count(Event.id).desc())
        .limit(limit)
        .all()
    )

    ips = [TopIP(ip=row[0], events=row[1], score=float(row[2] or 0.0)) for row in rows]
    return TopIPsResponse(ips=ips)


@app.get(f"{settings.API_PREFIX}/stats/credentials", response_model=CredentialHeatmapResponse)
async def get_credential_heatmap(db: Session = Depends(get_db), limit: int = 20):
    rows = (
        db.query(Event.username, func.count(Event.id).label("attempts"))
        .filter(Event.username.isnot(None))
        .group_by(Event.username)
        .order_by(func.count(Event.id).desc())
        .limit(limit)
        .all()
    )

    credentials = [
        CredentialStat(username=row[0] or "", attempts=row[1])
        for row in rows
    ]

    return CredentialHeatmapResponse(credentials=credentials)


@app.get(f"{settings.API_PREFIX}/alerts", response_model=AlertsResponse)
async def get_alerts(db: Session = Depends(get_db)):
    alerts = db.query(Alert).order_by(Alert.created_at.desc()).limit(100).all()
    return AlertsResponse(alerts=alerts)
