# 🛡️ HoneyShield

**HoneyShield** is a lightweight, modular, and proactive cybersecurity solution that deploys decoy services (honeypots) to detect, analyze, and respond to malicious intrusion attempts in real-time. Built for quick deployment and adaptability, it integrates machine learning to detect anomalies and delivers actionable threat intelligence through a responsive web dashboard.

---

## 🚀 Features

- 🎯 **Deception-Based Intrusion Detection**: Deploys decoy services to lure and log attackers.
- 🧠 **ML-Based Anomaly Detection**: Real-time malicious activity detection using trained models.
- 📬 **Instant Alerting System**: Sends email notifications on suspicious behavior.
- 📊 **Interactive Web Dashboard**: Visualize logs, attack patterns, and analytics.
- ⚙️ **Multi-threaded Architecture**: Efficient handling of concurrent network connections.
- 💾 **Structured Logging**: Records attack metadata in JSON/CSV format for analysis.

---

## 🧱 Tech Stack

- **Backend / Honeypot**: Python, Socket, Threading, Logging, smtplib, datetime
- **Machine Learning**: Python (pandas, scikit-learn), CICIDS / NSL-KDD dataset
- **Web Dashboard**: HTML, CSS, JavaScript, Flask (or Express), Chart.js / D3.js

---

## 📁 Modules Overview

| Module                | Description                                                                 |
|-----------------------|-----------------------------------------------------------------------------|
| Honeypot Engine       | Emulates vulnerable services and logs attacker behavior                    |
| Logging & Storage     | Structures logs for use in both ML and dashboard                           |
| ML Detection          | Detects anomalies using models like Isolation Forest                       |
| Alert System          | Sends real-time alerts via email                                            |
| Web Dashboard         | Displays logs, detection status, and visualizations                        |

---

## 🧪 How It Works

1. Decoy services listen on predefined ports.
2. All incoming connections are logged in real-time.
3. Logs are analyzed using trained ML models for anomaly detection.
4. Suspicious activity triggers instant email alerts.
5. Web dashboard provides an interactive visualization of threats.

---

## 🧰 Setup Instructions

### Prerequisites
- Python 3.x
- `pip install -r requirements.txt`
- Node.js (if using Express for backend)
- SMTP-enabled email account (e.g., Gmail)

### Steps

```bash
# Clone the repo
git clone https://github.com/your-username/honeyshield.git
cd honeyshield

# Install backend dependencies
pip install -r requirements.txt

# (Optional) Start web frontend
cd dashboard
npm install
npm start

