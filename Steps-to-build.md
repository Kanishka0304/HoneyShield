# 🛡️ HoneyShield: Modular Cybersecurity Honeypot System

HoneyShield is a lightweight, modular honeypot and intrusion detection platform that uses deception-based tactics and ML to detect and analyze malicious activity. It offers real-time alerts and a web-based threat dashboard.

---

## 🚀 Project Phases Overview

| Phase | Module                 | Description                                      |
|-------|------------------------|--------------------------------------------------|
| 1     | Honeypot Engine        | Emulate fake services to trap attackers         |
| 2     | Structured Logging     | Store logs in JSON/CSV for ML and dashboard     |
| 3     | ML Detection Engine    | Use ML to detect anomalies in behavior          |
| 4     | Email Alert System     | Notify on suspicious activity                   |
| 5     | Web Dashboard          | Visualize logs and threat data                  |
| 6     | Real-Time Integration  | Live ML predictions and alert triggering        |
| 7     | Deployment             | Containerized system with logging stack         |

---

## 🧱 Core Tech Stack

- **Backend / Honeypots**: Python (Socket, Threading, Logging)
- **Logging**: JSON, CSV, SQLite (optional), `datetime`
- **ML Engine**: `pandas`, `scikit-learn`, IsolationForest
- **Web Dashboard**: Flask, HTML/CSS, JS, Chart.js or D3.js
- **Email Alerts**: `smtplib` for SMTP-based notifications
- **Deployment**: Docker, Docker Compose, (optional: ELK stack)

---

## 🛠️ Step-by-Step Build Plan

### ✅ Phase 1: Honeypot Engine

1. Create multi-threaded TCP socket server.
2. Simulate SSH/HTTP/FTP banners (e.g. SSH: `SSH-2.0-OpenSSH_7.6p1`).
3. Log:
   - Timestamp
   - IP address
   - Port
   - Payload (e.g. password attempts)
4. Save logs to `logs/session_TIMESTAMP.json`

---

### ✅ Phase 2: Structured Logging

1. Design log schema:
```json
{
  "timestamp": "2025-05-13T14:55:21Z",
  "ip": "192.168.0.10",
  "port": 22,
  "protocol": "SSH",
  "payload": "admin:1234"
}
