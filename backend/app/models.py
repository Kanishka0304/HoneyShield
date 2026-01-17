from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    source_ip = Column(String, index=True, nullable=False)
    username = Column(String, nullable=True)
    password = Column(String, nullable=True)
    port = Column(Integer, nullable=False)
    protocol = Column(String, default="ssh")
    success = Column(Boolean, default=False)
    raw = Column(String, nullable=True)
    attack_type = Column(String, nullable=True)  # e.g. bruteforce, recon


class IPRiskScore(Base):
    __tablename__ = "ip_risk_scores"

    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String, unique=True, index=True, nullable=False)
    score = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    ip = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    severity = Column(String, default="medium")  # low, medium, high, critical
    resolved = Column(Boolean, default=False)

    # Optional: link to a representative event
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    event = relationship("Event")
