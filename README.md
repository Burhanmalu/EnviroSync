# EnviroSync 🌿⚡
### AI-Based Smart Indoor Environment Monitoring & Automated Comfort Control System

**EnviroSync** is an end-to-end, enterprise-ready system featuring:
1. **React Native Mobile App** ([`smart-indoor-app/`](./smart-indoor-app/)) built with Expo, TypeScript, Zustand, and React Query.
2. **Python AI + IoT Backend** ([`smart-indoor-python/`](./smart-indoor-python/)) built with FastAPI, SQLAlchemy, OpenCV, YOLO, scikit-learn, and MQTT.

```text
                    ┌─────────────────────────┐
                    │ React Native Mobile App │
                    │ (smart-indoor-app)      │
                    └────────────┬────────────┘
                                 │
                         REST API / WebSocket
                                 │
                    ┌────────────▼────────────┐
                    │      Python Backend     │
                    │      FastAPI Server     │
                    │ (smart-indoor-python)   │
                    └────────────┬────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
        AI/Computer Vision   Automation Engine   Database
              │                  │                  │
        OpenCV / YOLO          Rules/AI          PostgreSQL
              │                  │                  │
              └──────────────────┼──────────────────┘
                                 │
                            MQTT / HTTP
                                 │
                    ┌────────────▼────────────┐
                    │      ESP32 Controller   │
                    └────────────┬────────────┘
                                 │
          ┌──────────────────────┼─────────────────────┐
          │          │           │          │          │
      Temperature  Humidity      CO₂       Light    Devices
       Sensor      Sensor      Sensor     Sensor
                                             │
                                  AC / Fan / Curtains
```

---

## 🌟 Key Features & Capabilities

1. **Live Indoor Air Quality (IAQ) & Thermal Comfort**:
   - Composite IAQ Scoring (0–100) and ASHRAE 55 system comfort scoring.
   - Real-time tracking of Temperature (°C), Relative Humidity (%), CO₂ (ppm), and Ambient Light (lux).
   - Dynamic status alerts: `OPTIMAL`, `GOOD`, `MODERATE`, `WARNING`, and `CRITICAL`.

2. **AI Vision Occupancy & Edge Inference**:
   - Person detection using OpenCV / YOLO pipelines with **strict privacy preservation** (no biometric tracking or facial recognition).
   - Spatial density distribution across Zone A (Front), Zone B (Center), Zone C (Back-Left), and Zone D (Back-Right).

3. **Smart Actuator Control & Manual Override**:
   - **Smart AC**: Setpoint (16°C–30°C), presets, operating modes (`COOL`, `HEAT`, `FAN`, `DRY`, `AUTO`), fan speed.
   - **Ventilation Fans**: Multi-tier speed regulation and oscillation.
   - **Motorized Curtains/Blinds**: Position percentage stepper (0–100%) and glare mitigation.
   - **Manual Override Protection**: Temporary manual overrides with auto-return to autonomous mode.

4. **Autonomous AI Automation Engine**:
   - Evaluates rules against environment, crowd density, and device states.
   - **Anti-Flapping & Hysteresis**: Configurable deadbands prevent rapid on/off relay cycling.
   - Cooldown protection & priority scheduling.

5. **IoT Gateway & MQTT Communication**:
   - Standardized topic taxonomy: `smart-building/{hall_id}/commands`, `smart-building/{hall_id}/environment`, etc.
   - Direct translation to ESP32 relays, PWM fans, and stepper motors.

6. **Interactive Zero-Hardware Simulation**:
   - Realistic physics drift for testing without hardware.
   - Scenario switcher: `NORMAL`, `HIGH_TEMPERATURE`, `HIGH_OCCUPANCY`, `HIGH_CO2`, `LOW_OCCUPANCY`.

---

## 📁 Repository Structure

```text
EnviroSync/
│
├── smart-indoor-app/               # React Native (Expo) Mobile Application
│   ├── app/                        # Expo Router Screens & Layouts
│   ├── src/                        # Components, Stores, Themes & Services
│   ├── package.json
│   └── app.json
│
├── smart-indoor-python/            # FastAPI AI, Computer Vision & IoT Backend
│   ├── app/
│   │   ├── main.py                 # FastAPI Application & Background Simulator
│   │   ├── api/                    # REST Endpoints & WebSockets
│   │   ├── core/                   # Security, DB, Config, Logging
│   │   ├── models/                 # SQLAlchemy Database Models
│   │   ├── schemas/                # Pydantic Request/Response Models
│   │   ├── services/               # Business Logic & Orchestration
│   │   ├── ai/                     # CV Occupancy & Comfort Predictors
│   │   ├── iot/                    # MQTT Bridge & ESP32 Client
│   │   ├── simulation/             # Continuous Sensor Physics Simulators
│   │   └── realtime/               # WebSocket Manager
│   ├── scripts/
│   │   ├── seed_database.py        # Database Seeder
│   │   └── train_model.py          # ML Model Training Script
│   ├── tests/                      # Unit & Integration Tests
│   ├── requirements.txt
│   └── Dockerfile
│
└── README.md
```

---

## 🚀 Running the System

### 1. Start the Python AI Backend
```bash
cd smart-indoor-python
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```
* **Swagger API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **WebSocket Stream**: `ws://localhost:8000/ws/halls/hall-01`

### 2. Start the React Native Mobile App
```bash
cd smart-indoor-app
npm install
npx expo start -c
```
* Press `w` to open in browser, or scan QR code with Expo Go on Android/iOS.

---

## 🔑 Default Credentials

| Role | Email | Password |
|---|---|---|
| **Administrator** | `admin@envirosync.io` | `Admin@123456` |
| **Standard User** | `user@envirosync.io` | `User@123456` |
