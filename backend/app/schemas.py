from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class EventCreate(BaseModel):
    timestamp: Optional[datetime] = None
    source_ip: str
    username: Optional[str] = None
    password: Optional[str] = None
    port: int
    protocol: str = "ssh"
    success: bool = False
    raw: Optional[str] = None


class EventRead(BaseModel):
    id: int
    timestamp: datetime
    source_ip: str
    username: Optional[str]
    password: Optional[str]
    port: int
    protocol: str
    success: bool
    attack_type: Optional[str]

    class Config:
        orm_mode = True


class OverviewStats(BaseModel):
    total_events: int
    unique_ips: int
    high_risk_ips: int
    open_alerts: int


class TimelinePoint(BaseModel):
    bucket_start: datetime
    count: int


class TimelineResponse(BaseModel):
    points: List[TimelinePoint]


class TopIP(BaseModel):
    ip: str
    events: int
    score: float


class TopIPsResponse(BaseModel):
    ips: List[TopIP]


class CredentialStat(BaseModel):
    username: str
    attempts: int


class CredentialHeatmapResponse(BaseModel):
    credentials: List[CredentialStat]


class AlertRead(BaseModel):
    id: int
    created_at: datetime
    ip: str
    title: str
    description: Optional[str]
    severity: str
    resolved: bool

    class Config:
        orm_mode = True


class AlertsResponse(BaseModel):
    alerts: List[AlertRead]
