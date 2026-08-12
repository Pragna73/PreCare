# PreCare — Unified AI-Powered Prenatal Healthcare Platform

[![PreCare CI Pipeline](https://github.com/Pragna73/PreCare/actions/workflows/combined-tests.yml/badge.svg)](https://github.com/Pragna73/PreCare/actions)
[![Selenium Tests](https://github.com/Pragna73/PreCare/actions/workflows/selenium-tests.yml/badge.svg)](https://github.com/Pragna73/PreCare/actions)
[![Appium Mobile Tests](https://github.com/Pragna73/PreCare/actions/workflows/appium-tests.yml/badge.svg)](https://github.com/Pragna73/PreCare/actions)
[![Backend Security](https://github.com/Pragna73/PreCare/actions/workflows/backend-security.yml/badge.svg)](https://github.com/Pragna73/PreCare/actions)
[![Load Tests](https://github.com/Pragna73/PreCare/actions/workflows/load-tests.yml/badge.svg)](https://github.com/Pragna73/PreCare/actions)
[![Package Release ZIP](https://github.com/Pragna73/PreCare/actions/workflows/package-release.yml/badge.svg)](https://github.com/Pragna73/PreCare/actions)

PreCare is an end-to-end prenatal healthcare and clinical risk prediction ecosystem designed to monitor maternal and fetal well-being throughout pregnancy. The unified platform consolidates a native SwiftUI iOS mobile application, a high-performance Python FastAPI backend with Maya AI maternal triage, a modern React/Vite clinical web portal with Supabase & Gemini integration, and a multi-tiered automated testing suite (Selenium, Appium, Locust, SAST).

---

## 🏗️ Repository Architecture

```text
PreCare/
│
├── mobile/
│   └── PreCare-App/
│       ├── PreCare-main/              # SwiftUI iOS Application & Xcode Project
│       │   ├── PreCare/               # Views, ViewModels, Components, Assets
│       │   ├── PreCare.xcodeproj      # Xcode Project configuration
│       │   └── codemagic.yaml         # CI/CD Cloud Build configuration
│       ├── precare__backend-main/     # Python FastAPI Clinical Backend
│       │   ├── app/                   # Database models, auth, config, main router
│       │   ├── routers/               # Dashboard, Maya, reports, appointments
│       │   ├── services/              # AI risk analysis, OCR, digital twin, triage
│       │   └── requirements.txt       # Python backend dependencies
│       ├── tests/                     # 305 Mobile Appium clinical test cases
│       └── load_tests/                # Locust load testing & performance scripts
│
├── website/                           # React + TypeScript + Vite Web Application
│   ├── src/                           # Frontend components, clinical risk dashboard
│   ├── api/                           # Serverless analysis & OCR handlers
│   ├── public/                        # Static assets, branding, and icons
│   ├── package.json                   # Web dependencies (React, Lucide, Tailwind)
│   └── vite.config.ts                 # Vite bundler configuration
│
├── tests/                             # Unified Testing Hub
│   ├── selenium/                      # 300 Automated Selenium Website Tests
│   ├── appium/                        # 305 Mobile Appium UI & Auth Tests
│   ├── api/                           # Concurrent API load & latency benchmarks
│   └── test_data/                     # Parameterized clinical pregnancy datasets
│
├── .github/
│   └── workflows/                     # Automated CI/CD Workflows
│       ├── combined-tests.yml         # Master CI test pipeline
│       ├── selenium-tests.yml         # Website Selenium automated testing
│       ├── appium-tests.yml           # Mobile Appium automated testing
│       ├── backend-security.yml       # Dependency audit (pip-audit) & SAST (Bandit)
│       ├── load-tests.yml             # Locust 50-user load & stress testing
│       └── package-release.yml        # Clean complete project ZIP packager
│
├── .gitignore                         # Multi-stack exclusions (iOS, Python, Node)
└── README.md                          # Platform documentation & quickstart
```

---

## 📦 How to Download the Complete Project

You can download the entire PreCare platform in a single unified archive:

1. **Via GitHub UI**: Click the green **Code** button at the top right of this repository and select **Download ZIP**.
2. **Via GitHub Actions Releases**: Go to the **Actions** tab → Select **Package Complete PreCare Project (ZIP)** → Download the latest `PreCare-complete-project.zip` artifact.

---

## 🚀 Quick Start Guide

### 1. Web Application (`website/`)

The PreCare web application provides pregnancy risk analysis, maternal indicator dashboards, lab report uploads, and doctor recommendations.

```bash
cd website

# 1. Install dependencies
npm install

# 2. Configure environment variables
cp .env.example .env
# Edit .env and supply your Supabase and Gemini keys

# 3. Start local development server
npm run dev

# 4. Build for production
npm run build
```

---

### 2. FastAPI Backend (`mobile/PreCare-App/precare__backend-main/`)

The FastAPI backend powers Maya AI conversational guidance, digital twin maternal health tracking, appointment scheduling, and automated clinical risk scoring.

```bash
cd mobile/PreCare-App/precare__backend-main

# 1. Create and activate Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env

# 4. Start FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
* Interactive API Documentation (Swagger UI): `http://127.0.0.1:8000/docs`
* Health Check: `http://127.0.0.1:8000/health`

---

### 3. iOS Mobile Application (`mobile/PreCare-App/PreCare-main/`)

The iOS app is built natively in **SwiftUI** for iOS 17+, featuring secure authentication with password visibility toggles, interactive Maya AI chat, kick counter, emergency contact triage, and health vitals tracking.

```bash
# 1. Open the project in Xcode
open mobile/PreCare-App/PreCare-main/PreCare.xcodeproj

# 2. Select your target simulator (e.g. iPhone 16 / iPhone 16 Pro)
# 3. Press Cmd + R to build and run
```

---

## 🧪 Automated Testing Suites

### 1. Selenium Website Tests (300 Test Cases)
Automates clinical test case validation on the live web portal:
```bash
pip install selenium pytest pytest-html
pytest tests/selenium/ -v --html=reports/selenium-report.html --self-contained-html
```

### 2. Appium Mobile Tests (305 Test Cases)
Automates native iOS mobile workflows including authentication, emergency contacts, appointment bookings, and Maya AI queries:
```bash
pip install Appium-Python-Client pytest pytest-html selenium
pytest tests/appium/ -v --html=reports/appium-report.html --self-contained-html
```

### 3. Backend Concurrency & Load Tests
Validates high-concurrency performance (800+ req/s, <5ms latency) using Locust:
```bash
pip install locust
python3 tests/api/test_backend_load.py

# Run headless Locust 50-user load test
locust -f tests/api/locustfile.py --headless -u 50 -r 10 --run-time 15s --host http://127.0.0.1:8000 --html reports/load-test-report.html
```

---

## 🔄 CI/CD Workflows (`.github/workflows/`)

| Workflow | Description | Trigger |
| :--- | :--- | :--- |
| `combined-tests.yml` | Master pipeline running Website, Mobile, and Backend checks | Push / PR |
| `selenium-tests.yml` | 300 Parameterized Selenium web tests + HTML artifact | Push / PR |
| `appium-tests.yml` | 305 Appium mobile tests + HTML artifact | Push / PR |
| `backend-security.yml`| Automated `pip-audit`, Bandit SAST, and Flake8 linting | Push / PR |
| `load-tests.yml` | Headless Locust 50-user performance benchmark | Push / PR |
| `package-release.yml`| Creates clean `PreCare-complete-project.zip` release | Push / Manual |

---

## 🔒 Security & Secrets Management
- All production credentials, database URLs, and API keys are managed exclusively via environment variables and GitHub Actions Secrets.
- Sensitive files (`.env`, `*.db`, `uploads/`, `reports/`, `DerivedData/`) are strictly excluded via `.gitignore`.
- Reference templates are provided in `.env.example` across both website and backend modules.

---

## 📄 License
PreCare Platform is proprietary and confidential. All rights reserved.
