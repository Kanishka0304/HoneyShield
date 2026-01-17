from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from .models import Alert, Event, IPRiskScore


# Simple heuristic weights
FAILED_ATTEMPT_WEIGHT = 1.0
RECON_WEIGHT = 0.5
BRUTEFORCE_BURST_WEIGHT = 3.0

HIGH_RISK_THRESHOLD = 20.0


def _classify_attack_type(db: Session, event: Event) -> str:
    """Very simple classification: if many attempts in short period -> bruteforce, else recon."""

    window_start = datetime.utcnow() - timedelta(minutes=5)
    recent_count = (
        db.query(func.count(Event.id))
        .filter(Event.source_ip == event.source_ip, Event.timestamp >= window_start)
        .scalar()
    )

    if recent_count >= 20:
        return "bruteforce"
    elif recent_count >= 5:
        return "recon"
    return "low_activity"


def update_risk_and_alerts(db: Session, event: Event) -> None:
    # Classify attack type and update event
    attack_type = _classify_attack_type(db, event)
    event.attack_type = attack_type

    # Base score increment
    increment = 0.0
    if not event.success:
        increment += FAILED_ATTEMPT_WEIGHT

    if attack_type == "recon":
        increment += RECON_WEIGHT
    elif attack_type == "bruteforce":
        increment += BRUTEFORCE_BURST_WEIGHT

    # Get or create risk record
    ip_risk = db.query(IPRiskScore).filter(IPRiskScore.ip == event.source_ip).first()
    if not ip_risk:
        ip_risk = IPRiskScore(ip=event.source_ip, score=0.0, last_updated=datetime.utcnow())
        db.add(ip_risk)

    ip_risk.score += increment
    ip_risk.last_updated = datetime.utcnow()
    db.flush()

    # Generate alert if threshold crossed
    if ip_risk.score >= HIGH_RISK_THRESHOLD:
        existing_open = (
            db.query(Alert)
            .filter(Alert.ip == event.source_ip, Alert.resolved.is_(False))
            .first()
        )
        if not existing_open:
            alert = Alert(
                ip=event.source_ip,
                title="High risk SSH activity detected",
                description=(
                    f"IP {event.source_ip} exceeded risk score threshold with attack type "
                    f"'{attack_type}'."
                ),
                severity="high",
                event=event,
            )
            db.add(alert)

    db.commit()
