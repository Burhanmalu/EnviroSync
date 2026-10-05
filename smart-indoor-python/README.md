# Smart Indoor Environment Monitoring & Automated Comfort Control System (Python Backend)

A high-performance **Python 3.11+ AI, Computer Vision, IoT, and Automation Backend** built with **FastAPI**, **SQLAlchemy**, **PostgreSQL / SQLite**, **MQTT**, **OpenCV**, and **scikit-learn**.

---

## 🌟 Architecture Highlights

* **FastAPI Async Core**: High-throughput asynchronous REST API and WebSockets (`/ws/halls/{hall_id}`).
* **JWT Authentication & RBAC**: Role-based access control with `ADMIN` and `USER` roles.
* **Computer Vision Occupancy AI**: Person counting & zone density distribution using YOLO/OpenCV with **strict privacy preservation** (no biometric tracking or facial recognition).
* **AI Multi-Parameter Comfort Scoring**: 0–100 Environmental Comfort Index computed from Temperature, Humidity, CO₂, Crowding, and Ambient Light.
* **Predictive ML Modeling**: Horizon forecasting for future thermal loads and CO₂ accumulation.
* **Autonomous Automation Engine**: Configurable trigger rules, priority hierarchy, cooldowns, and anti-flapping hysteresis margins.
* **Device Control & Manual Overrides**: AC, Fan, and Motorized Blinds management with temporary manual override support.
* **MQTT Hardware Bridge**: Seamless bidirectional communication with ESP32 microcontrollers and hardware sensors.
* **Zero-Hardware Simulation Suite**: Realistic continuous telemetry simulation with multiple operational demo scenarios (`NORMAL`, `HIGH_TEMPERATURE`, `HIGH_OCCUPANCY`, `HIGH_CO2`, `LOW_OCCUPANCY`).

---

## 📂 Project Structure

```text
smart-indoor-python/
│
├── app/
│   ├── main.py                  # FastAPI Application & Background Worker
│   ├── api/                     # REST Endpoints & WebSockets
│   │   ├── auth.py              # Login, Registration & Profile
│   │   ├── halls.py             # Hall Resource Management
│   │   ├── environment.py       # Temperature, Humidity, CO2, Light Ingestion & History
│   │   ├── occupancy.py         # Crowd Analytics & Zone Density
│   │   ├── devices.py           # Actuator State & Command Execution
│   │   ├── automation.py        # Automation Rules & Event Log
│   │   ├── notifications.py     # System & Environmental Alerts
│   │   ├── analytics.py         # Aggregations, Trends & AI Forecasts
│   │   ├── camera.py            # Computer Vision Stream Status
│   │   ├── demo.py              # Live Scenario Switcher
│   │   ├── health.py            # Component Health & Uptime
│   │   └── websocket.py         # Real-time WebSocket Protocol
│   ├── core/                    # Security, Database & Config
│   ├── models/                  # SQLAlchemy Database Models
│   ├── schemas/                 # Pydantic Schemas & DTOs
│   ├── services/                # Business Logic Services
│   ├── ai/                      # CV Detector, Scorer & Predictor
│   ├── iot/                     # MQTT Client, ESP32 Dispatcher & Device Controller
│   ├── simulation/              # Physics Drift Simulators & Scenarios
│   ├── realtime/                # WebSocket Room Connection Manager
│   └── utils/                   # Calculations, Validators & Timestamps
│
├── scripts/
│   ├── seed_database.py         # Default Data Seeder
│   └── train_model.py           # ML Model Training Script
│
├── tests/                       # Pytest Test Suite
├── requirements.txt             # Python Dependencies
├── alembic.ini                  # Migration Config
└── Dockerfile                   # Container Deployment
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
* Python 3.11+ (or Python 3.12 / 3.13 / 3.14)
* Virtual Environment: `python -m venv venv`

### 2. Installation
```bash
cd smart-indoor-python
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Start the Server
```bash
python -m uvicorn app.main:app --reload --port 8000
```

* **Interactive API Documentation (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **Alternative API Documentation (Redoc)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
* **WebSocket Stream**: `ws://localhost:8000/ws/halls/hall-01`

---

## 🔑 Default Seed Credentials

| Role | Email | Password |
|---|---|---|
| **Administrator** | `admin@envirosync.io` | `Admin@123456` |
| **Standard User** | `user@envirosync.io` | `User@123456` |

---

## 📡 Key REST API Endpoints

### 🔐 Authentication
* `POST /api/auth/login` - Authenticate & obtain JWT bearer token.
* `POST /api/auth/register` - Create new user profile.
* `GET /api/auth/me` - Fetch authenticated user details.

### 🏢 Halls
* `GET /api/halls` - List all monitored halls and rooms.
* `POST /api/halls` - Register a new hall (Admin).
* `GET /api/halls/{id}` - Retrieve hall details.
* `PUT /api/halls/{id}` - Update hall metadata.
* `DELETE /api/halls/{id}` - Delete hall.

### 🌡️ Environment & IAQ
* `GET /api/halls/{id}/environment` - Latest temperature, humidity, CO₂, light & IAQ score.
* `POST /api/halls/{id}/environment` - Ingest sensor telemetry.
* `GET /api/halls/{id}/environment/history?hours=24` - Historical time-series telemetry.

### 👥 Occupancy & Computer Vision
* `GET /api/halls/{id}/occupancy` - Latest crowd count, percentage, and zone breakdown.
* `POST /api/halls/{id}/occupancy` - Ingest vision/sensor occupancy count.
* `GET /api/halls/{id}/camera` - CV stream health, people count & privacy compliance notice.

### ❄️ Devices & Actuator Control
* `GET /api/halls/{id}/devices` - List all actuators (AC, Fan, Curtains).
* `GET /api/halls/{id}/devices/state` - Unified actuator state object.
* `PUT /api/devices/{id}` - Update device state/mode.
* `POST /api/devices/{id}/command` - Execute specific actuator action (`SET_TEMP`, `SET_SPEED`, `SET_POSITION`, `RETURN_AUTO`).

### ⚙️ Automation Engine
* `GET /api/halls/{id}/automation/rules` - List automation rules.
* `POST /api/halls/{id}/automation/rules` - Create automated rule with hysteresis.
* `PUT /api/automation/rules/{id}` - Modify rule thresholds or cooldown.
* `GET /api/halls/{id}/automation/events` - Audit log of autonomous actions triggered.

### 📊 AI Analytics & Predictions
* `GET /api/halls/{id}/analytics` - 24h summary averages, comfort trends, and energy savings.
* `GET /api/halls/{id}/comfort` - Comprehensive comfort index breakdown (0–100).
* `GET /api/halls/{id}/predictions?horizon_minutes=20` - ML forecasts for future environmental trajectories.

### 🎭 Live Demo Mode
* `POST /api/demo/scenario` - Trigger live demo scenario (`NORMAL`, `HIGH_TEMPERATURE`, `HIGH_OCCUPANCY`, `HIGH_CO2`, `LOW_OCCUPANCY`).
* `GET /api/demo/status/{hall_id}` - Current demo state.

---

## 🔌 Real-time WebSocket Protocol

Connect to `ws://localhost:8000/ws/halls/{hall_id}` to receive real-time JSON events:

```json
{
  "event_type": "environment_update",
  "hall_id": "hall-01",
  "data": {
    "temperature": 25.4,
    "humidity": 52.1,
    "co2": 560.0,
    "light": 450.0,
    "comfort_score": 87,
    "comfort_status": "EXCELLENT",
    "timestamp": "2026-10-05T11:45:00Z"
  }
}
```

---

## 🧪 Running Unit Tests

```bash
pytest -v
```
