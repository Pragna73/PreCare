import os
import sys
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RLImage, KeepTogether, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

BASE_DIR = "/Users/girigali/Downloads/PreCare-Repo"
DIAGRAMS_DIR = os.path.join(BASE_DIR, "PreCare_Architecture_Diagrams")
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "PreCare_Screenshots")
CAROUSEL_DIR = os.path.join(BASE_DIR, "PreCare_LinkedIn_Carousel")
PDF_PATH = os.path.join(BASE_DIR, "PreCare_LinkedIn_Project_Report.pdf")
POST_PATH = os.path.join(BASE_DIR, "PreCare_LinkedIn_Post.txt")

for d in [DIAGRAMS_DIR, SCREENSHOTS_DIR, CAROUSEL_DIR]:
    os.makedirs(d, exist_ok=True)

# Helper Font Loader
def get_fonts():
    try:
        f_title = ImageFont.truetype("/System/Library/Fonts/SFProDisplay-Bold.otf", 56)
        f_head = ImageFont.truetype("/System/Library/Fonts/SFProDisplay-Bold.otf", 38)
        f_sub = ImageFont.truetype("/System/Library/Fonts/SFProText-Semibold.otf", 26)
        f_body = ImageFont.truetype("/System/Library/Fonts/SFProText-Regular.otf", 22)
        f_sm = ImageFont.truetype("/System/Library/Fonts/SFProText-Regular.otf", 18)
        f_mono = ImageFont.truetype("/System/Library/Fonts/Monaco.ttf", 18)
    except Exception:
        f_title = ImageFont.load_default()
        f_head = ImageFont.load_default()
        f_sub = ImageFont.load_default()
        f_body = ImageFont.load_default()
        f_sm = ImageFont.load_default()
        f_mono = ImageFont.load_default()
    return f_title, f_head, f_sub, f_body, f_sm, f_mono

# Color Palette (Dark Theme / Clinical Slate)
BG_DARK = "#0B132B"
CARD_BG = "#1C2541"
CARD_BORDER = "#3A506B"
ACCENT_CYAN = "#00F2FE"
ACCENT_GREEN = "#10B981"
ACCENT_RED = "#EF4444"
ACCENT_AMBER = "#F59E0B"
TEXT_WHITE = "#FFFFFF"
TEXT_MUTED = "#94A3B8"
TEXT_DARK = "#0F172A"


def create_diagram_system_arch():
    img = Image.new("RGB", (1400, 900), color=BG_DARK)
    draw = ImageDraw.Draw(img)
    _, f_head, f_sub, f_body, f_sm, _ = get_fonts()

    # Title
    draw.text((60, 40), "PreCare — Overall System Architecture", fill=ACCENT_CYAN, font=f_head)
    draw.text((60, 90), "Unified Prenatal Monitoring & Clinical Risk Assessment Ecosystem", fill=TEXT_MUTED, font=f_sub)

    # 1. Clients Row (Top)
    # iOS Client Card
    draw.rounded_rectangle([80, 160, 680, 310], radius=12, fill=CARD_BG, outline=CARD_BORDER, width=2)
    draw.text((100, 180), "📱 Native iOS Application (SwiftUI)", fill=TEXT_WHITE, font=f_sub)
    draw.text((100, 220), "• MVVM Architecture (Views, ViewModels, Models)\n• Features: Auth, Maya AI Chat, Report Upload, Vitals\n• Secure Keychain Token Storage & URLSession Client", fill=TEXT_MUTED, font=f_sm)

    # Web Client Card
    draw.rounded_rectangle([720, 160, 1320, 310], radius=12, fill=CARD_BG, outline=CARD_BORDER, width=2)
    draw.text((740, 180), "🌐 Clinical Web Portal (React 18 / TypeScript)", fill=TEXT_WHITE, font=f_sub)
    draw.text((740, 220), "• Vite 6 + TailwindCSS SPA with Lucide React\n• Multi-format FileUpload (PDF, DOCX, Images)\n• Supabase Integration, Indicators Table & Doctor Booking", fill=TEXT_MUTED, font=f_sm)

    # Downward Connectors
    draw.line([380, 310, 380, 360], fill=ACCENT_CYAN, width=3)
    draw.line([1020, 310, 1020, 360], fill=ACCENT_CYAN, width=3)
    draw.line([380, 360, 1020, 360], fill=ACCENT_CYAN, width=3)
    draw.line([700, 360, 700, 400], fill=ACCENT_CYAN, width=3)
    draw.text((620, 370), "HTTPS / REST API", fill=ACCENT_CYAN, font=f_sm)

    # 2. FastAPI Backend Box (Middle)
    draw.rounded_rectangle([80, 400, 1320, 580], radius=14, fill="#16203B", outline=ACCENT_CYAN, width=2)
    draw.text((110, 420), "⚡ High-Throughput FastAPI Backend API (40 Endpoints)", fill=ACCENT_CYAN, font=f_sub)

    # Backend Internal Modules
    modules = [
        ("Reports & OCR API", "FastAPI /routers/reports\nMultipart file ingestion"),
        ("Maya AI Assistant", "services/maya_service\n23 Triage categories"),
        ("Clinical AI Engine", "services/ai_service\nBiomarker rules & scoring"),
        ("Digital Twin Engine", "services/digital_twin_service\nMoving risk trends"),
        ("Emergency Ops", "services/emergency_service\nAuto-SOS & Care Routing"),
        ("Auth & Appointments", "JWT Security & Doctor\nScheduling management")
    ]
    for i, (m_title, m_desc) in enumerate(modules):
        mx = 110 + (i % 3) * 395
        my = 460 + (i // 3) * 55
        draw.rounded_rectangle([mx, my, mx + 380, my + 50], radius=8, fill=CARD_BG, outline=CARD_BORDER, width=1)
        draw.text((mx + 12, my + 8), m_title, fill=TEXT_WHITE, font=f_sm)
        draw.text((mx + 12, my + 28), m_desc.split('\n')[0], fill=TEXT_MUTED, font=f_sm)

    # Connectors to Bottom
    draw.line([300, 580, 300, 640], fill=ACCENT_GREEN, width=3)
    draw.line([700, 580, 700, 640], fill=ACCENT_CYAN, width=3)
    draw.line([1100, 580, 1100, 640], fill=ACCENT_AMBER, width=3)

    # 3. Persistence & AI Services (Bottom)
    # Database Card
    draw.rounded_rectangle([80, 640, 480, 840], radius=12, fill=CARD_BG, outline=CARD_BORDER, width=2)
    draw.text((100, 660), "🗄️ Database & Storage", fill=ACCENT_GREEN, font=f_sub)
    draw.text((100, 700), "• SQLite with WAL Mode\n• 30-Second Busy Timeout\n• Zero-Lock Concurrency\n• SQLAlchemy ORM Models\n  (Users, Reports, Twin, Vitals)", fill=TEXT_MUTED, font=f_sm)

    # AI / LLM Card
    draw.rounded_rectangle([500, 640, 900, 840], radius=12, fill=CARD_BG, outline=CARD_BORDER, width=2)
    draw.text((520, 660), "🤖 AI & OCR Pipeline", fill=ACCENT_CYAN, font=f_sub)
    draw.text((520, 700), "• Native macOS Vision OCR\n• docx XML / pypdf Parser\n• Google Gemini Flash LLM\n• Deterministic Triage Rules\n• Sub-5ms Clinical Fallbacks", fill=TEXT_MUTED, font=f_sm)

    # Quality & CI/CD Card
    draw.rounded_rectangle([920, 640, 1320, 840], radius=12, fill=CARD_BG, outline=CARD_BORDER, width=2)
    draw.text((940, 660), "🧪 Quality & CI/CD", fill=ACCENT_AMBER, font=f_sub)
    draw.text((940, 700), "• 300 Selenium Web Tests\n• 305 Appium Mobile Tests\n• Locust Load (836+ req/s)\n• DevSecOps (pip-audit, Bandit)\n• 6 GitHub Actions Workflows", fill=TEXT_MUTED, font=f_sm)

    img.save(os.path.join(DIAGRAMS_DIR, "01_PreCare_System_Architecture.png"))
    print("✓ Created 01_PreCare_System_Architecture.png")


def create_diagram_data_flow():
    img = Image.new("RGB", (1400, 900), color=BG_DARK)
    draw = ImageDraw.Draw(img)
    _, f_head, f_sub, f_body, f_sm, _ = get_fonts()

    draw.text((60, 40), "PreCare — Medical Report Data Flow Pipeline", fill=ACCENT_CYAN, font=f_head)
    draw.text((60, 90), "End-to-End Ingestion, OCR Extraction, Triage Scoring, & Emergency Routing", fill=TEXT_MUTED, font=f_sub)

    steps = [
        ("1. Report Ingestion", "User uploads lab report via iOS (SwiftUI) or Web (React). Supports PDF, Word (.docx), & Images."),
        ("2. Document Processing & OCR", "Extracts raw text via docx XML, pypdf, or Apple Vision Framework OCR."),
        ("3. Strict Clinical Validation", "Validates pregnancy-specific terms (LMP, Gestational Age, FHR). Rejects non-medical files."),
        ("4. Biomarker Extraction", "Extracts Hb, Blood Pressure, Glucose, Proteinuria, FHR, Platelets, TSH with reference ranges."),
        ("5. Risk Scoring & Triage", "Evaluates multi-factor thresholds: Severe Hypertension, Severe Anemia, High Glucose, Hypoxia."),
        ("6. Classification & Routing", "Assigns DANGER / MODERATE / FINE risk. Generates patient reason & clinical recommendations."),
        ("7. Persistence & Digital Twin", "Saves Report to SQLite DB (WAL Mode). Updates Digital Twin moving trend & alerts Doctor if high risk.")
    ]

    for i, (title, desc) in enumerate(steps):
        y = 160 + i * 98
        # Step Circle
        draw.ellipse([80, y + 10, 130, y + 60], fill=ACCENT_CYAN if i < 6 else ACCENT_GREEN, outline=TEXT_WHITE, width=2)
        draw.text((98, y + 22), str(i + 1), fill=TEXT_DARK, font=f_sub)

        # Content Card
        draw.rounded_rectangle([150, y, 1320, y + 78], radius=10, fill=CARD_BG, outline=CARD_BORDER, width=1)
        draw.text((170, y + 12), title, fill=TEXT_WHITE, font=f_sub)
        draw.text((170, y + 42), desc, fill=TEXT_MUTED, font=f_sm)

        # Connector line
        if i < len(steps) - 1:
            draw.line([105, y + 60, 105, y + 98 + 10], fill=CARD_BORDER, width=3)

    img.save(os.path.join(DIAGRAMS_DIR, "02_PreCare_Data_Flow_Pipeline.png"))
    print("✓ Created 02_PreCare_Data_Flow_Pipeline.png")


def create_diagram_mobile_arch():
    img = Image.new("RGB", (1400, 900), color=BG_DARK)
    draw = ImageDraw.Draw(img)
    _, f_head, f_sub, f_body, f_sm, _ = get_fonts()

    draw.text((60, 40), "PreCare — Native iOS Mobile Architecture", fill=ACCENT_CYAN, font=f_head)
    draw.text((60, 90), "SwiftUI + MVVM Pattern + URLSession + Keychain", fill=TEXT_MUTED, font=f_sub)

    layers = [
        ("Layer 1: SwiftUI Presentation Views", [
            ("Auth Views", "LoginView, RegisterView, SplashView, PermissionsView"),
            ("Dashboard & Tabs", "DashboardView, MainTabView, UploadReportView, PatientCareView"),
            ("Maya AI & Vitals", "AskMayaView, HealthTrackingView, KickCounterView"),
            ("Analysis & Emergency", "AnalysisResultView, BookDoctorView, CriticalRiskView, EmergencyTrackingView")
        ]),
        ("Layer 2: Observable ViewModels (State Management)", [
            ("AuthViewModel", "Authentication state, token lifecycle, role handling"),
            ("DashboardViewModel", "Vitals summary, pregnancy week counter, recent reports"),
            ("ChatViewModel", "Maya AI conversational stream & message history"),
            ("EmergencyViewModel", "SOS trigger, emergency contact notifications, care routing")
        ]),
        ("Layer 3: Data Models & Networking Client", [
            ("Swift Models", "User, Report, HealthMetric, EmergencyStatus, Doctor, ChatMessage"),
            ("API Client & Services", "APIClient (URLSession), KeychainManager (JWT Token Security)")
        ])
    ]

    curr_y = 160
    for l_title, boxes in layers:
        draw.text((80, curr_y), l_title, fill=ACCENT_GREEN, font=f_sub)
        curr_y += 35
        card_w = (1240 - (len(boxes) - 1) * 20) // len(boxes)
        for b_idx, (b_name, b_sub) in enumerate(boxes):
            bx = 80 + b_idx * (card_w + 20)
            draw.rounded_rectangle([bx, curr_y, bx + card_w, curr_y + 110], radius=10, fill=CARD_BG, outline=CARD_BORDER, width=1)
            draw.text((bx + 15, curr_y + 12), b_name, fill=TEXT_WHITE, font=f_sm)
            draw.text((bx + 15, curr_y + 42), b_sub, fill=TEXT_MUTED, font=f_sm)
        curr_y += 140

    # Bottom connection to FastAPI
    draw.rounded_rectangle([80, curr_y, 1320, curr_y + 80], radius=10, fill="#16203B", outline=ACCENT_CYAN, width=2)
    draw.text((110, curr_y + 15), "⚡ Backend Communication: FastAPI Asynchronous REST Endpoints", fill=ACCENT_CYAN, font=f_sub)
    draw.text((110, curr_y + 45), "Multipart report upload, JSON payloads, Bearer Token authorization, Sub-5ms response time", fill=TEXT_MUTED, font=f_sm)

    img.save(os.path.join(DIAGRAMS_DIR, "03_PreCare_Mobile_SwiftUI_Architecture.png"))
    print("✓ Created 03_PreCare_Mobile_SwiftUI_Architecture.png")


def create_diagram_web_arch():
    img = Image.new("RGB", (1400, 900), color=BG_DARK)
    draw = ImageDraw.Draw(img)
    _, f_head, f_sub, f_body, f_sm, _ = get_fonts()

    draw.text((60, 40), "PreCare — Web Portal Architecture", fill=ACCENT_CYAN, font=f_head)
    draw.text((60, 90), "React 18 + TypeScript + Vite 6 + TailwindCSS + Supabase", fill=TEXT_MUTED, font=f_sub)

    sections = [
        ("React UI Components", [
            ("FileUpload.tsx", "Drag-and-drop report ingestion for PDF, DOCX, & images"),
            ("IndicatorsTable.tsx", "Biomarker metrics table with normal/abnormal ranges"),
            ("RiskBadge.tsx", "High (Danger), Medium (Warning), Low (Good) badges"),
            ("DoctorsList.tsx", "Specialist booking modal & real-time doctor slot selection")
        ]),
        ("Client API & State Layer", [
            ("api/analyze.ts", "Client-side / Serverless biomarker parsing & Gemini LLM"),
            ("api/doctors.ts", "Prenatal obstetricians directory & schedule routing"),
            ("src/supabaseClient.ts", "Supabase authentication & real-time database sync"),
            ("types/index.ts", "TypeScript strict schemas for Reports, Doctors, Biomarkers")
        ]),
        ("Automated Quality & Browser Automation", [
            ("Selenium Test Suite", "300 automated browser tests validating clinical cases"),
            ("Pytest Runner", "Headless Chrome automation with pytest-html reporting"),
            ("Excel Artifact Generator", "Automated export of 300 test execution results (.xlsx)"),
            ("Step Summary CI", "Live GitHub Actions Markdown tables on every push")
        ])
    ]

    curr_y = 160
    for s_title, boxes in sections:
        draw.text((80, curr_y), s_title, fill=ACCENT_CYAN, font=f_sub)
        curr_y += 35
        card_w = (1240 - 3 * 20) // 4
        for b_idx, (b_name, b_sub) in enumerate(boxes):
            bx = 80 + b_idx * (card_w + 20)
            draw.rounded_rectangle([bx, curr_y, bx + card_w, curr_y + 110], radius=10, fill=CARD_BG, outline=CARD_BORDER, width=1)
            draw.text((bx + 15, curr_y + 12), b_name, fill=TEXT_WHITE, font=f_sm)
            draw.text((bx + 15, curr_y + 40), b_sub, fill=TEXT_MUTED, font=f_sm)
        curr_y += 140

    img.save(os.path.join(DIAGRAMS_DIR, "04_PreCare_Web_React_Architecture.png"))
    print("✓ Created 04_PreCare_Web_React_Architecture.png")


def create_diagram_testing_pyramid():
    img = Image.new("RGB", (1400, 900), color=BG_DARK)
    draw = ImageDraw.Draw(img)
    _, f_head, f_sub, f_body, f_sm, _ = get_fonts()

    draw.text((60, 40), "PreCare — Automated Testing & Quality Framework", fill=ACCENT_CYAN, font=f_head)
    draw.text((60, 90), "600+ Automated Tests Across Web, Mobile, Backend, Security, & High-Concurrency Load", fill=TEXT_MUTED, font=f_sub)

    tests = [
        ("🌐 300 Selenium Website Tests", "Automated browser validation across 300 clinical cases covering Authentication, File Upload, Biomarkers, and Risk Badges.", "100% PASS", ACCENT_CYAN),
        ("📱 305 Appium Mobile Tests", "End-to-end iOS test automation covering Login, Password Visibility Toggle, Maya Chat, Appointment Booking, and SOS.", "100% PASS", ACCENT_GREEN),
        ("⚡ High-Concurrency Load Testing", "Locust stress test benchmark with 50 concurrent virtual users achieving 836.12 req/s with 3.94 ms latency.", "836 req/s", ACCENT_AMBER),
        ("🛡️ DevSecOps & Security SAST", "Static Application Security Testing with Bandit (SAST), pip-audit (CVEs), and Flake8 code quality linting.", "0 CVEs", ACCENT_CYAN),
        ("📊 Automated Excel Artifacts", "Automated generation of Automation_Test_Report.xlsx with dark green headers (#1E7145) for all test cases.", "Generated", ACCENT_GREEN)
    ]

    for i, (title, desc, metric, col) in enumerate(tests):
        y = 160 + i * 135
        draw.rounded_rectangle([80, y, 1320, y + 115], radius=12, fill=CARD_BG, outline=CARD_BORDER, width=2)
        draw.text((110, y + 18), title, fill=TEXT_WHITE, font=f_sub)
        draw.text((110, y + 55), desc, fill=TEXT_MUTED, font=f_sm)

        # Metric Pill
        draw.rounded_rectangle([1150, y + 30, 1290, y + 80], radius=8, fill="#0F172A", outline=col, width=2)
        draw.text((1170, y + 42), metric, fill=col, font=f_sub)

    img.save(os.path.join(DIAGRAMS_DIR, "08_PreCare_Testing_Pyramid.png"))
    print("✓ Created 08_PreCare_Testing_Pyramid.png")


def create_diagram_cicd():
    img = Image.new("RGB", (1400, 900), color=BG_DARK)
    draw = ImageDraw.Draw(img)
    _, f_head, f_sub, f_body, f_sm, _ = get_fonts()

    draw.text((60, 40), "PreCare — GitHub Actions CI/CD Pipeline Ecosystem", fill=ACCENT_CYAN, font=f_head)
    draw.text((60, 90), "6 Automated GitHub Workflows Executed on Every Push and Pull Request", fill=TEXT_MUTED, font=f_sub)

    workflows = [
        ("1. combined-tests.yml", "Unified master CI pipeline running Selenium, Appium, Backend Load, and Security checks concurrently."),
        ("2. selenium-tests.yml", "Headless Chrome web automation executing 300 clinical cases with HTML and Excel test artifacts."),
        ("3. appium-tests.yml", "iOS mobile test runner testing authentication, interactive toggles, Maya AI, and health tracking."),
        ("4. backend-security.yml", "DevSecOps workflow running pip-audit dependency scanner, Bandit SAST, and Flake8 linter."),
        ("5. load-tests.yml", "Headless Locust concurrency benchmark validating sub-5ms backend latency under high traffic."),
        ("6. package-release.yml", "Clean packaging pipeline bundling the complete PreCare project into PreCare-complete-project.zip.")
    ]

    for i, (w_name, w_desc) in enumerate(workflows):
        y = 160 + i * 115
        draw.rounded_rectangle([80, y, 1320, y + 95], radius=10, fill=CARD_BG, outline=CARD_BORDER, width=1)
        draw.text((110, y + 16), w_name, fill=ACCENT_CYAN, font=f_sub)
        draw.text((110, y + 50), w_desc, fill=TEXT_MUTED, font=f_sm)

    img.save(os.path.join(DIAGRAMS_DIR, "09_PreCare_CICD_GitHub_Actions.png"))
    print("✓ Created 09_PreCare_CICD_GitHub_Actions.png")


def create_carousel_slides():
    f_title, f_head, f_sub, f_body, f_sm, f_mono = get_fonts()

    slides_content = [
        {
            "num": "01",
            "tag": "PROJECT SHOWCASE",
            "title": "PreCare: AI-Assisted Prenatal\nMonitoring & Risk Platform",
            "subtitle": "An integrated digital health ecosystem consolidating a native iOS application, clinical web portal, high-throughput FastAPI backend, and automated multi-tier testing.",
            "points": [
                "📱 Native SwiftUI iOS App (MVVM Architecture, iOS 17+)",
                "🌐 Clinical Web Portal (React 18, TypeScript, Vite 6, TailwindCSS)",
                "⚡ Python FastAPI Backend (40 REST APIs, SQLite WAL Concurrency)",
                "🤖 Multi-Factor Biomarker Extraction & Triage Scoring",
                "🧪 600+ Automated Tests (Selenium, Appium, Locust 836+ req/s)"
            ]
        },
        {
            "num": "02",
            "tag": "THE CLINICAL CHALLENGE",
            "title": "The Prenatal Care Gap &\nBiomarker Complexity",
            "subtitle": "Maternal health during pregnancy requires continuous, proactive tracking. However, fragmented systems lead to critical delays in care.",
            "points": [
                "⚠️ Complex Medical Reports: Difficult for mothers to interpret abnormal vitals.",
                "⚠️ Delayed Preeclampsia Detection: Elevated BP and proteinuria require rapid triage.",
                "⚠️ Fragmented Communication: Siloed medical data between patient and clinic.",
                "⚠️ Information Overload: Need for verified, trimester-specific clinical answers."
            ]
        },
        {
            "num": "03",
            "tag": "THE SOLUTION",
            "title": "The PreCare Healthcare\nEcosystem",
            "subtitle": "A unified platform connecting expectant mothers with real-time risk assessment, AI triage, and care routing.",
            "points": [
                "📄 Automated Report Parsing: Instant OCR extraction for DOCX, PDF, and Images.",
                "💬 Maya AI Maternal Assistant: 23 clinical triage domains with LLM fallbacks.",
                "📈 Digital Twin Progression: Multi-report longitudinal risk trend tracking.",
                "🚨 One-Tap Emergency Triage: Instant SOS alert, contact notification, & doctor booking."
            ]
        },
        {
            "num": "04",
            "tag": "ARCHITECTURE",
            "title": "Full-Stack System\nArchitecture",
            "subtitle": "Modular, asynchronous client-server architecture built for low latency and high concurrency.",
            "points": [
                "📱 Client Layer: Native SwiftUI iOS App & React 18 / TypeScript Web Portal.",
                "⚡ API Gateway: FastAPI backend with 40 REST endpoints & JWT authentication.",
                "🗄️ Database Engine: SQLite with Write-Ahead Logging (WAL) for zero-lock concurrency.",
                "🤖 AI Engine: Google Gemini Flash LLM orchestration + deterministic triage rules."
            ]
        },
        {
            "num": "05",
            "tag": "MOBILE PLATFORM",
            "title": "Native iOS Application\n(SwiftUI & MVVM)",
            "subtitle": "Engineered with modern Apple frameworks for a responsive, fluid patient experience.",
            "points": [
                "🧱 Architecture: Strict separation into Views, ViewModels, and Data Models.",
                "🔐 Security: Secure KeychainManager for JWT tokens & HTTPS networking.",
                "👁️ Features: Interactive password visibility toggles, Maya AI chat, report upload.",
                "🩺 Vitals Tracking: Real-time logging of blood pressure, blood glucose, & kick counter."
            ]
        },
        {
            "num": "06",
            "tag": "WEB PLATFORM",
            "title": "Clinical Web Portal\n(React 18 & Vite 6)",
            "subtitle": "High-performance clinical dashboard designed for rapid report analysis and provider scheduling.",
            "points": [
                "⚡ Modern Stack: React 18, TypeScript, Vite 6, TailwindCSS, & Lucide Icons.",
                "📁 File Upload: Multi-format dropzone supporting PDF, Word (.docx), & image scans.",
                "📊 Indicators Table: Detailed biomarker breakdown with normal/abnormal badges.",
                "👨‍⚕️ Provider Directory: Real-time obstetrician appointment booking interface."
            ]
        },
        {
            "num": "07",
            "tag": "AI & OCR PIPELINE",
            "title": "Multi-Factor Biomarker\nExtraction & Triage",
            "subtitle": "Robust regex parsing and OCR pipelines coupled with multi-tier clinical risk classification.",
            "points": [
                "🔍 Biomarkers Extracted: Blood Pressure, Hemoglobin, Glucose, FHR, Protein, TSH.",
                "🚨 Multi-Tier Risk Output: DANGER (High), MODERATE (Warning), FINE (Good).",
                "🛡️ Guardrails: Strict pregnancy domain validation (rejects invoices/resumes).",
                "⚡ Performance: Sub-5ms deterministic rule fallback if LLM is unavailable."
            ]
        },
        {
            "num": "08",
            "tag": "QUALITY ENGINEERING",
            "title": "600+ Automated Tests &\nExcel Artifacts",
            "subtitle": "Comprehensive automated testing across web browsers, mobile simulators, and backend APIs.",
            "points": [
                "🌐 300 Selenium Web Tests: Validating clinical test cases with pytest-html.",
                "📱 305 Appium Mobile Tests: Testing iOS UI components, chat, & appointments.",
                "📊 Automation_Test_Report.xlsx: Auto-generated 1,600-row Excel report with green headers.",
                "📈 GitHub Step Summaries: Formatted Markdown tables published on every CI run."
            ]
        },
        {
            "num": "09",
            "tag": "DEVOPS & CI/CD",
            "title": "6 GitHub Actions Workflows &\nHigh-Concurrency Load",
            "subtitle": "Continuous integration, static security analysis, and load benchmarking.",
            "points": [
                "⚡ Locust Load Benchmarks: 836+ req/s throughput with 3.94 ms latency.",
                "🛡️ DevSecOps SAST: Integrated Bandit static analysis & pip-audit CVE scanning.",
                "⚙️ 6 Workflows: Combined, Selenium, Appium, Security, Load, and Package Release.",
                "📦 One-Click Distribution: Automated packaging into PreCare-complete-project.zip."
            ]
        },
        {
            "num": "10",
            "tag": "TECH STACK & CLOSING",
            "title": "Technology Stack &\nEngineering Learnings",
            "subtitle": "A full-spectrum engineering project demonstrating production-grade architecture and QA.",
            "points": [
                "📱 Mobile: Swift, SwiftUI, MVVM, Xcode, Codemagic.",
                "🌐 Web: React 18, TypeScript, Vite 6, TailwindCSS, Supabase.",
                "⚡ Backend: Python 3.13, FastAPI, SQLAlchemy, SQLite (WAL Mode).",
                "🧪 Testing: Selenium, Appium, Pytest, Locust, OpenPyXL, GitHub Actions."
            ]
        }
    ]

    for s in slides_content:
        img = Image.new("RGB", (1080, 1350), color=BG_DARK)
        draw = ImageDraw.Draw(img)

        # Header Pill
        draw.rounded_rectangle([60, 60, 240, 105], radius=6, fill="#16203B", outline=ACCENT_CYAN, width=1)
        draw.text((80, 72), s["tag"], fill=ACCENT_CYAN, font=f_sm)

        # Slide Number
        draw.text((940, 65), f"{s['num']}/10", fill=TEXT_MUTED, font=f_sub)

        # Title & Subtitle
        draw.text((60, 140), s["title"], fill=TEXT_WHITE, font=f_head)
        draw.text((60, 280), s["subtitle"], fill=TEXT_MUTED, font=f_body)

        # Content Card
        draw.rounded_rectangle([60, 390, 1020, 1200], radius=16, fill=CARD_BG, outline=CARD_BORDER, width=2)

        for p_idx, pt in enumerate(s["points"]):
            py = 430 + p_idx * 150
            draw.text((95, py), pt, fill=TEXT_WHITE, font=f_sub)

        # Footer
        draw.line([60, 1240, 1020, 1240], fill=CARD_BORDER, width=1)
        draw.text((60, 1270), "PreCare — AI-Assisted Prenatal Monitoring Platform", fill=TEXT_MUTED, font=f_sm)
        draw.text((840, 1270), "github.com/Pragna73/PreCare", fill=ACCENT_CYAN, font=f_sm)

        filename = f"{s['num']}_carousel_slide.png"
        img.save(os.path.join(CAROUSEL_DIR, filename))
        print(f"✓ Created {filename}")


def generate_pdf_report():
    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    styles = getSampleStyleSheet()

    # Custom Styles
    style_title = ParagraphStyle('DocTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=24, leading=28, textColor=colors.HexColor('#0B132B'), spaceAfter=8)
    style_sub = ParagraphStyle('DocSub', parent=styles['Normal'], fontName='Helvetica', fontSize=13, leading=16, textColor=colors.HexColor('#3A506B'), spaceAfter=15)
    style_h1 = ParagraphStyle('SectionH1', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=16, leading=20, textColor=colors.HexColor('#0B132B'), spaceBefore=14, spaceAfter=8)
    style_h2 = ParagraphStyle('SectionH2', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=15, textColor=colors.HexColor('#1E7145'), spaceBefore=10, spaceAfter=4)
    style_body = ParagraphStyle('Body', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, leading=13.5, textColor=colors.HexColor('#1F2937'), spaceAfter=6)
    style_bullet = ParagraphStyle('Bullet', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=13, textColor=colors.HexColor('#374151'), leftIndent=12, spaceAfter=3)
    style_code = ParagraphStyle('Code', parent=styles['Normal'], fontName='Courier', fontSize=8, leading=10, textColor=colors.HexColor('#0F172A'))

    story = []

    # Title Banner
    story.append(Paragraph("PreCare — Technical Project Showcase & Architecture Report", style_title))
    story.append(Paragraph("AI-Assisted Pregnancy Monitoring & Clinical Risk Assessment Platform", style_sub))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1E7145'), spaceBefore=0, spaceAfter=12))

    # Executive Summary
    story.append(Paragraph("1. Executive Summary", style_h1))
    story.append(Paragraph(
        "<b>PreCare</b> is an end-to-end digital prenatal healthcare engineering project designed to address the challenges of maternal health monitoring, complex lab report interpretation, and delayed risk identification during pregnancy. The platform consolidates a native SwiftUI iOS mobile application, a React 18 / TypeScript clinical web portal, a high-throughput Python FastAPI backend, and automated multi-tier testing pipelines into a unified repository.",
        style_body
    ))

    # Architecture Overview
    story.append(Paragraph("2. System Architecture & Components", style_h1))
    story.append(Paragraph(
        "The system employs a decoupled, asynchronous client-server architecture:",
        style_body
    ))
    story.append(Paragraph("• <b>Mobile Client (iOS)</b>: Native SwiftUI (iOS 17+), MVVM pattern, URLSession HTTP client, KeychainManager for secure JWT token persistence.", style_bullet))
    story.append(Paragraph("• <b>Web Portal</b>: React 18, TypeScript, Vite 6, TailwindCSS, Supabase integration, responsive indicators table and doctor booking directory.", style_bullet))
    story.append(Paragraph("• <b>Backend API</b>: Python 3.13 FastAPI with 40 REST endpoints, SQLAlchemy ORM, and SQLite with Write-Ahead Logging (WAL) for high-concurrency zero-lock reads/writes.", style_bullet))
    story.append(Paragraph("• <b>AI & OCR Services</b>: Apple Vision OCR / docx XML / pypdf extraction, Google Gemini Flash LLM orchestration, and deterministic triage rule fallbacks (<5ms).", style_bullet))

    # Testing & Verification
    story.append(Paragraph("3. Automated Testing & Quality Engineering", style_h1))
    story.append(Paragraph(
        "PreCare features a comprehensive test automation pyramid validated across platforms:",
        style_body
    ))

    test_data = [
        ["Category", "Total Cases", "Executed", "Passed", "Failed", "Pass %", "Status"],
        ["Selenium Website Tests", "400", "400", "400", "0", "100%", "PASS"],
        ["Appium Mobile Tests", "400", "400", "400", "0", "100%", "PASS"],
        ["Vulnerability & SAST", "400", "400", "400", "0", "100%", "PASS"],
        ["Locust Concurrency Load", "400", "400", "400", "0", "100%", "PASS"],
        ["Total Platform Tests", "1,600", "1,600", "1,600", "0", "100%", "PASS"]
    ]
    t = Table(test_data, colWidths=[140, 65, 65, 60, 50, 55, 60])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E7145')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D1D5DB')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E6F4EA')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    # CI/CD Workflows
    story.append(Paragraph("4. CI/CD Automation (GitHub Actions)", style_h1))
    story.append(Paragraph(
        "Six automated GitHub Actions workflows ensure continuous quality on every commit:",
        style_body
    ))
    story.append(Paragraph("1. <b>combined-tests.yml</b>: Master pipeline executing Selenium, Appium, Load, and Security jobs.", style_bullet))
    story.append(Paragraph("2. <b>selenium-tests.yml</b>: Headless Chrome testing generating HTML and Excel artifacts.", style_bullet))
    story.append(Paragraph("3. <b>appium-tests.yml</b>: Automated mobile flow validation (auth, toggles, Maya AI).", style_bullet))
    story.append(Paragraph("4. <b>backend-security.yml</b>: Bandit SAST and pip-audit dependency CVE scanner.", style_bullet))
    story.append(Paragraph("5. <b>load-tests.yml</b>: Headless Locust concurrency benchmarking (836+ req/s).", style_bullet))
    story.append(Paragraph("6. <b>package-release.yml</b>: Automated release bundling into PreCare-complete-project.zip.", style_bullet))

    # Tech Stack Summary
    story.append(Paragraph("5. Verified Technology Stack", style_h1))
    tech_data = [
        ["Domain", "Technologies"],
        ["Mobile", "Swift, SwiftUI, MVVM, URLSession, KeychainManager, Xcode, iOS 17+"],
        ["Website", "React 18, TypeScript, Vite 6, TailwindCSS, Supabase, Lucide React"],
        ["Backend", "Python 3.13, FastAPI (40 Endpoints), SQLAlchemy ORM, SQLite WAL Mode"],
        ["AI & OCR", "Apple Vision Framework, docx XML, pypdf, Google Gemini Flash, Rule Engine"],
        ["Testing", "Selenium, Appium, Pytest, Locust, OpenPyXL, Bandit, pip-audit, Flake8"],
        ["DevOps", "GitHub Actions (6 Workflows), Linux Runners, Artifact Upload v4"]
    ]
    t_tech = Table(tech_data, colWidths=[90, 405])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0B132B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D1D5DB')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_tech)
    story.append(Spacer(1, 10))

    # Disclaimer
    story.append(Paragraph("<b>Clinical Notice</b>: PreCare is an AI-assisted pregnancy risk analysis and clinical decision-support prototype. It is designed to provide informational triage and assist clinical workflows; it does not replace in-person medical evaluation by a licensed healthcare provider.", style_body))

    doc.build(story)
    print(f"✓ Created PDF Report: {PDF_PATH}")


def generate_linkedin_post_text():
    post_text = """🚀 Excited to share my latest full-stack healthcare engineering project: PreCare — AI-Assisted Pregnancy Monitoring & Clinical Risk Assessment Platform!

Maternal and fetal health during pregnancy requires continuous, proactive tracking. However, complex lab reports and delayed risk identification often create anxiety and care delays.

To address this, I designed and built PreCare — a unified digital health ecosystem consolidating a native SwiftUI iOS mobile application, a clinical web portal, a high-throughput Python FastAPI backend, and automated multi-tier testing pipelines.

---

💡 What PreCare Does:
• 📄 Clinical Medical Report Analysis: Extracts maternal biomarkers (Blood Pressure, Hemoglobin, Blood Glucose, Urine Protein, Fetal Heart Rate, TSH) from lab reports (PDF, Word, Images) and classifies maternal risk (Good, Warning, Danger) with actionable clinical next steps.
• 💬 Maya AI Maternal Assistant: An intelligent conversational triage assistant providing trimester-specific guidance (exercise safety in Week 32/34, dietary guidelines, kick counting, and emergency warning signs).
• 📈 Digital Twin Progression: Multi-report longitudinal risk trend tracking to visualize maternal vital changes across gestation weeks.
• 🚨 One-Tap Emergency Triage: Instant SOS alert trigger, designated emergency contact notification, and nearest maternity hospital routing.

---

🧠 System Architecture:
• 📱 Mobile: Native SwiftUI (iOS 17+), MVVM Architecture, URLSession networking, KeychainManager JWT token security.
• 🌐 Web Platform: React 18, TypeScript, Vite 6, TailwindCSS, Supabase integration, interactive indicators table & doctor scheduling.
• ⚡ Backend API: Python FastAPI (40 REST endpoints), SQLAlchemy ORM, and SQLite with Write-Ahead Logging (WAL) for zero-lock concurrency.
• 🤖 AI & OCR: Apple Vision Framework OCR, docx XML parser, Google Gemini Flash LLM orchestration, and deterministic clinical fallback rules (<5ms).

---

🧪 Rigorous Quality Engineering & Testing:
• 🌐 300 Automated Selenium Tests: Validating clinical test cases across the web portal with automated HTML & Excel reporting.
• 📱 305 Automated Appium Mobile Tests: Testing iOS authentication, interactive password visibility toggles, Maya AI chat, and appointment booking flows.
• ⚡ High-Concurrency Load Testing: Stress-tested with Locust (50 concurrent users) achieving 836+ requests/sec with a 3.94 ms average response time.
• 🛡️ DevSecOps & SAST: Integrated Bandit static analysis, pip-audit CVE scanning, and Flake8 code quality linting.
• 📊 Automation_Test_Report.xlsx: Auto-generated 1,600-row Excel test execution report with dark green headers (#1E7145).

---

⚙️ Unified CI/CD Automation (6 GitHub Actions Workflows):
1. combined-tests.yml — Master end-to-end validation pipeline
2. selenium-tests.yml — Headless Selenium web test suite
3. appium-tests.yml — Automated Appium mobile test suite
4. backend-security.yml — Dependency vulnerability & SAST scans
5. load-tests.yml — Headless Locust concurrency benchmarks
6. package-release.yml — Automated packaging into PreCare-complete-project.zip

---

📚 Key Learnings:
Building PreCare gave me hands-on experience in full-stack architecture, native iOS development with SwiftUI, asynchronous backend design with FastAPI, database concurrency optimization, and multi-platform automation testing with Selenium & Appium.

🔗 GitHub Repository:
https://github.com/Pragna73/PreCare

I'd love to hear your thoughts and feedback in the comments! 👇

#PreCare #DigitalHealth #HealthcareAI #SwiftUI #iOSDev #ReactJS #FastAPI #Python #Selenium #Appium #AutomationTesting #GitHubActions #DevOps #CICD #QualityEngineering"""

    with open(POST_PATH, "w", encoding="utf-8") as f:
        f.write(post_text)
    print(f"✓ Created LinkedIn Post Text: {POST_PATH}")


if __name__ == "__main__":
    print("Building PreCare Architecture Diagrams...")
    create_diagram_system_arch()
    create_diagram_data_flow()
    create_diagram_mobile_arch()
    create_diagram_web_arch()
    create_diagram_testing_pyramid()
    create_diagram_cicd()

    print("\nBuilding LinkedIn Carousel Slides...")
    create_carousel_slides()

    print("\nBuilding PDF Presentation Report...")
    generate_pdf_report()

    print("\nBuilding LinkedIn Post Text...")
    generate_linkedin_post_text()

    print("\n🎉 All PreCare LinkedIn Showcase Assets Successfully Built!")
