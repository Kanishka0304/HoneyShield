import random
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.correlation import update_risk_and_alerts
from app.database import Base, SessionLocal, engine
from app.models import Event


def seed_events(db: Session, num_events: int = 200) -> None:
    Base.metadata.create_all(bind=engine)

    base_time = datetime.utcnow() - timedelta(hours=6)

    ips = [
        "192.0.2.10",
        "198.51.100.23",
        "203.0.113.5",
        "10.0.0.15",
        "172.16.1.20",
    ]
    usernames = ["root", "admin", "test", "ubuntu", "guest"]
    passwords = ["123456", "password", "admin", "toor", "letmein"]

    for _ in range(num_events):
        ts = base_time + timedelta(minutes=random.randint(0, 360))
        ip = random.choice(ips)
        username = random.choice(usernames)
        password = random.choice(passwords)

        event = Event(
            timestamp=ts,
            source_ip=ip,
            username=username,
            password=password,
            port=2222,
            protocol="ssh",
            success=False,
            raw=None,
        )
        db.add(event)
        db.flush()  # get event.id

        update_risk_and_alerts(db, event)

    db.commit()


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_events(db)
        print("Seeded sample SSH attack events.")
    finally:
        db.close()
