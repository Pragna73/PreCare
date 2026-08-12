import os
import glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Dimensions
WIDTH, HEIGHT = 1080, 1350

# Fonts
FONT_BOLD_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_REG_PATH = "/System/Library/Fonts/Supplemental/Arial.ttf"

def get_font(size, bold=False):
    path = FONT_BOLD_PATH if bold else FONT_REG_PATH
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

# Color Palette
BG_TOP = (11, 19, 43)        # #0B132B
BG_BOTTOM = (20, 32, 60)     # Deep Navy
CARD_BG = (28, 44, 82, 230)  # Glass Navy
CARD_BORDER = (0, 242, 254, 80)
CYAN = (0, 242, 254)         # #00F2FE
TEAL = (79, 172, 254)        # #4FACFE
CORAL = (255, 94, 126)       # #FF5E7E
GREEN = (46, 213, 115)       # #2ED573
YELLOW = (255, 171, 0)       # #FFAB00
TEXT_WHITE = (255, 255, 255)
TEXT_MUTED = (160, 175, 200)

ASSETS_DIR = "/Users/girigali/Downloads/PreCare-Unified/mobile/PreCare-App/precare__backend-main/assets"
CAROUSEL_DIR = "/Users/girigali/Downloads/PreCare-Unified/PreCare_LinkedIn_Carousel"
IMAGES_DIR = "/Users/girigali/Downloads/PreCare-Unified/PreCare_LinkedIn_Images"
PDF_PATH = "/Users/girigali/Downloads/PreCare-Unified/PreCare_LinkedIn_Project_Report.pdf"

os.makedirs(CAROUSEL_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

def create_base_canvas(slide_num, total_slides=10, category="PRECARE PROJECT SHOWCASE"):
    img = Image.new("RGBA", (WIDTH, HEIGHT), BG_TOP)
    draw = ImageDraw.Draw(img)
    
    # Subtle gradient
    for y in range(HEIGHT):
        r = int(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * (y / HEIGHT))
        g = int(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * (y / HEIGHT))
        b = int(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * (y / HEIGHT))
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255))
        
    # Decorative background ambient glow
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse([-150, -150, 450, 450], fill=(0, 242, 254, 25))
    glow_draw.ellipse([WIDTH - 350, HEIGHT - 350, WIDTH + 150, HEIGHT + 150], fill=(79, 172, 254, 20))
    glow_draw.ellipse([WIDTH - 250, 200, WIDTH + 200, 650], fill=(255, 94, 126, 18))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)

    # Header Tracker
    draw.text((60, 50), category.upper(), font=get_font(20, bold=True), fill=CYAN)
    badge_text = f"{slide_num:02d} / {total_slides:02d}"
    draw.text((WIDTH - 150, 50), badge_text, font=get_font(20, bold=True), fill=TEXT_MUTED)
    draw.line([(60, 85), (WIDTH - 60, 85)], fill=(255, 255, 255, 30), width=1)
    
    # Footer Branding
    draw.line([(60, HEIGHT - 70), (WIDTH - 60, HEIGHT - 70)], fill=(255, 255, 255, 30), width=1)
    draw.text((60, HEIGHT - 50), "PreCare — AI-Powered Pregnancy Monitoring & Risk Analysis", font=get_font(18), fill=TEXT_MUTED)
    draw.text((WIDTH - 260, HEIGHT - 50), "github.com/Pragna73/PreCare", font=get_font(18, bold=True), fill=TEAL)
    
    return img

def draw_card(img, rect, bg_color=CARD_BG, border_color=CARD_BORDER, radius=20):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    x0, y0, x1, y1 = rect
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=bg_color, outline=border_color, width=2)
    return Image.alpha_composite(img, overlay)

# -------------------------------------------------------------
# SLIDE 1: COVER
# -------------------------------------------------------------
def generate_slide_1():
    img = create_base_canvas(1, 10, "PRECARE • AI HEALTHCARE PLATFORM")
    draw = ImageDraw.Draw(img)
    
    # Hero Title
    draw.text((60, 150), "PreCare", font=get_font(84, bold=True), fill=TEXT_WHITE)
    draw.text((60, 250), "AI-Powered Pregnancy Monitoring &\nClinical Risk Analysis Ecosystem", font=get_font(42, bold=True), fill=CYAN)
    
    draw.text((60, 380), "An integrated digital health platform uniting native iOS (SwiftUI), clinical web portal\n(React/Vite), high-throughput FastAPI backend, and multi-tier automated testing.", font=get_font(22), fill=TEXT_MUTED)
    
    # Badges
    badges = ["AI & Biomarkers", "SwiftUI iOS 17+", "FastAPI Backend", "React Web", "300 Selenium Tests", "305 Appium Tests", "CI/CD Workflows"]
    bx, by = 60, 480
    for b in badges:
        bw = len(b) * 13 + 30
        if bx + bw > WIDTH - 60:
            bx = 60
            by += 55
        img = draw_card(img, [bx, by, bx + bw, by + 42], bg_color=(0, 242, 254, 35), border_color=(0, 242, 254, 120), radius=10)
        d = ImageDraw.Draw(img)
        d.text((bx + 15, by + 10), b, font=get_font(18, bold=True), fill=TEXT_WHITE)
        bx += bw + 15

    # Visual Preview Showcase Card
    card_rect = [60, 630, WIDTH - 60, 1230]
    img = draw_card(img, card_rect, bg_color=(15, 26, 54, 240), border_color=(79, 172, 254, 90), radius=25)
    
    # Insert Real App Screenshots into the Card
    ss1_path = os.path.join(ASSETS_DIR, "login.jpeg")
    ss2_path = os.path.join(ASSETS_DIR, "result.jpeg")
    ss3_path = os.path.join(ASSETS_DIR, "profile.jpeg")
    
    if os.path.exists(ss1_path):
        s1 = Image.open(ss1_path).convert("RGBA").resize((280, 460))
        img.paste(s1, (90, 680))
    if os.path.exists(ss2_path):
        s2 = Image.open(ss2_path).convert("RGBA").resize((380, 460))
        img.paste(s2, (390, 680))
    if os.path.exists(ss3_path):
        s3 = Image.open(ss3_path).convert("RGBA").resize((180, 460))
        img.paste(s3, (790, 680))
        
    d = ImageDraw.Draw(img)
    d.text((90, 1160), "📱 iOS Mobile App", font=get_font(22, bold=True), fill=CYAN)
    d.text((390, 1160), "📊 AI Risk Classification", font=get_font(22, bold=True), fill=GREEN)
    d.text((790, 1160), "🩺 Profile", font=get_font(22, bold=True), fill=TEAL)
    
    out = os.path.join(CAROUSEL_DIR, "01-cover.png")
    img.save(out)
    return img

# -------------------------------------------------------------
# SLIDE 2: THE PROBLEM
# -------------------------------------------------------------
def generate_slide_2():
    img = create_base_canvas(2, 10, "CLINICAL CONTEXT & CHALLENGE")
    draw = ImageDraw.Draw(img)
    
    draw.text((60, 140), "The Challenge in Maternal Care", font=get_font(52, bold=True), fill=TEXT_WHITE)
    draw.text((60, 210), "Navigating Complex Biomarkers & Preventing Delayed Triage", font=get_font(26), fill=CYAN)
    
    cards = [
        ("📄 Complex Medical Reports", "Routine lab reports contain multi-variate biomarkers (Hb, Blood Pressure, Fetal Heart Rate, Glucose) that are overwhelming for expectant mothers to interpret without immediate medical counsel.", CORAL),
        ("⏱️ Delayed Risk Identification", "Subtle signs of gestational hypertension, severe maternal anemia, or fetal distress often go unaddressed until scheduled doctor appointments weeks later.", YELLOW),
        ("🧩 Information Fragmentation", "Mothers lack a unified ecosystem that connects real-time vitals monitoring, AI guidance, emergency protocols, and certified obstetricians in one place.", TEAL),
        ("💡 The Decision-Support Need", "Expectant mothers require accessible, automated decision-support tools that extract clinical indicators instantly while maintaining clear medical guardrails.", GREEN)
    ]
    
    cy = 280
    for title, desc, col in cards:
        img = draw_card(img, [60, cy, WIDTH - 60, cy + 200], bg_color=(20, 33, 65, 230), border_color=(col[0], col[1], col[2], 90), radius=18)
        d = ImageDraw.Draw(img)
        d.text((90, cy + 25), title, font=get_font(30, bold=True), fill=col)
        
        # Word wrap text
        words = desc.split()
        lines = []
        cur = ""
        for w in words:
            if len(cur + " " + w) < 70:
                cur += (" " if cur else "") + w
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
            
        ly = cy + 75
        for line in lines:
            d.text((90, ly), line, font=get_font(22), fill=TEXT_WHITE)
            ly += 32
            
        cy += 230
        
    out = os.path.join(CAROUSEL_DIR, "02-problem.png")
    img.save(out)
    return img

# -------------------------------------------------------------
# SLIDE 3: THE SOLUTION
# -------------------------------------------------------------
def generate_slide_3():
    img = create_base_canvas(3, 10, "PRECARE CORE CAPABILITIES")
    draw = ImageDraw.Draw(img)
    
    draw.text((60, 140), "The PreCare Solution", font=get_font(52, bold=True), fill=TEXT_WHITE)
    draw.text((60, 210), "An End-to-End Maternal Healthcare & Triage Ecosystem", font=get_font(26), fill=CYAN)
    
    pillars = [
        ("1. OCR & Biomarker Extraction", "Automated parsing of uploaded medical documents, lab reports, and vitals (Hemoglobin, Systolic/Diastolic BP, Glucose, FHR) using intelligent OCR pipelines.", CYAN),
        ("2. Clinical AI Risk Assessment", "Multi-factor maternal risk scoring into standardized categories (GOOD, WARNING, DANGER) with immediate clinical action items and nutritional recommendations.", GREEN),
        ("3. Maya AI Maternal Assistant", "Conversational AI assistant delivering trimester-specific guidance (e.g. Week 32/34 exercises, travel safety, kick counting, and emergency triage).", TEAL),
        ("4. Real-time Digital Twin & Vitals", "Continuous tracking of maternal metrics, kick counter timers, scheduled doctor appointments, and 1-tap emergency caregiver notification.", CORAL)
    ]
    
    cy = 280
    for title, desc, col in pillars:
        img = draw_card(img, [60, cy, WIDTH - 60, cy + 200], bg_color=(20, 33, 65, 230), border_color=(col[0], col[1], col[2], 90), radius=18)
        d = ImageDraw.Draw(img)
        d.text((90, cy + 25), title, font=get_font(30, bold=True), fill=col)
        
        words = desc.split()
        lines = []
        cur = ""
        for w in words:
            if len(cur + " " + w) < 70:
                cur += (" " if cur else "") + w
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
            
        ly = cy + 75
        for line in lines:
            d.text((90, ly), line, font=get_font(22), fill=TEXT_WHITE)
            ly += 32
            
        cy += 230
        
    out = os.path.join(CAROUSEL_DIR, "03-solution.png")
    img.save(out)
    return img

# -------------------------------------------------------------
# SLIDE 4: SYSTEM ARCHITECTURE
# -------------------------------------------------------------
def generate_slide_4():
    img = create_base_canvas(4, 10, "FULL-STACK ARCHITECTURE")
    draw = ImageDraw.Draw(img)
    
    draw.text((60, 140), "System Architecture", font=get_font(52, bold=True), fill=TEXT_WHITE)
    draw.text((60, 210), "High-Throughput Modular Full-Stack Engineering", font=get_font(26), fill=CYAN)
    
    layers = [
        ("📱 CLIENT LAYER", "Native SwiftUI (iOS 17+) App • React 18 + TypeScript + Vite Web Portal", (0, 242, 254)),
        ("⚡ API & GATEWAY", "Python FastAPI (40 REST Endpoints) • CORS • Bearer Auth • Multi-Part Upload", (79, 172, 254)),
        ("🤖 AI & PROCESSING", "Google Gemini Flash LLM • Clinical Fallback Rules • Tesseract OCR", (46, 213, 115)),
        ("🗄️ PERSISTENCE", "SQLAlchemy ORM • SQLite Write-Ahead Logging (WAL) Mode • Supabase Storage", (255, 171, 0)),
        ("🧪 AUTOMATED TESTING", "300 Selenium Web Tests • 305 Appium Mobile Tests • Locust Load Tests (836 req/s)", (255, 94, 126)),
        ("⚙️ CI/CD DEVOPS", "6 GitHub Actions Workflows • Codemagic iOS Builds • Release ZIP Packaging", (180, 140, 255))
    ]
    
    cy = 280
    for title, desc, col in layers:
        img = draw_card(img, [60, cy, WIDTH - 60, cy + 130], bg_color=(18, 30, 60, 240), border_color=(col[0], col[1], col[2], 120), radius=16)
        d = ImageDraw.Draw(img)
        d.text((90, cy + 20), title, font=get_font(26, bold=True), fill=col)
        d.text((90, cy + 65), desc, font=get_font(21), fill=TEXT_WHITE)
        
        # Connective arrow if not last
        if cy < 280 + 5 * 155:
            d.line([(WIDTH // 2, cy + 130), (WIDTH // 2, cy + 155)], fill=(col[0], col[1], col[2], 180), width=3)
            
        cy += 155
        
    out = os.path.join(CAROUSEL_DIR, "04-architecture.png")
    img.save(out)
    return img

# -------------------------------------------------------------
# SLIDE 5: MOBILE EXPERIENCE
# -------------------------------------------------------------
def generate_slide_5():
    img = create_base_canvas(5, 10, "MOBILE APPLICATION • SWIFTUI")
    draw = ImageDraw.Draw(img)
    
    draw.text((60, 140), "Native iOS Application", font=get_font(52, bold=True), fill=TEXT_WHITE)
    draw.text((60, 210), "Built with SwiftUI (iOS 17+) & MVVM Architecture", font=get_font(26), fill=CYAN)
    
    # Feature checklist
    features = [
        "✓ Password Visibility Toggle (eye.fill / eye.slash.fill)",
        "✓ Maya AI Pregnancy Assistant with Trimester Workouts",
        "✓ Fetal Kick Counter & Daily Vitals Tracking",
        "✓ Automated Emergency Contact Triage"
    ]
    fy = 270
    for f in features:
        draw.text((60, fy), f, font=get_font(22, bold=True), fill=GREEN)
        fy += 40
        
    # Showcase Cards with Real Screenshots
    ss_box = [60, 450, WIDTH - 60, 1220]
    img = draw_card(img, ss_box, bg_color=(15, 26, 54, 240), border_color=(0, 242, 254, 80), radius=22)
    
    ss1_path = os.path.join(ASSETS_DIR, "login.jpeg")
    ss2_path = os.path.join(ASSETS_DIR, "register.jpeg")
    ss3_path = os.path.join(ASSETS_DIR, "result.jpeg")
    
    if os.path.exists(ss1_path):
        s1 = Image.open(ss1_path).convert("RGBA").resize((270, 480))
        img.paste(s1, (90, 500))
    if os.path.exists(ss2_path):
        s2 = Image.open(ss2_path).convert("RGBA").resize((270, 480))
        img.paste(s2, (395, 500))
    if os.path.exists(ss3_path):
        s3 = Image.open(ss3_path).convert("RGBA").resize((270, 480))
        img.paste(s3, (700, 500))
        
    d = ImageDraw.Draw(img)
    d.text((90, 1020), "1. Secure Login", font=get_font(22, bold=True), fill=CYAN)
    d.text((90, 1060), "Eye toggle plaintext/secure", font=get_font(18), fill=TEXT_MUTED)
    
    d.text((395, 1020), "2. User Registration", font=get_font(22, bold=True), fill=TEAL)
    d.text((395, 1060), "Emergency contact setup", font=get_font(18), fill=TEXT_MUTED)
    
    d.text((700, 1020), "3. Maya AI Chat & Triage", font=get_font(22, bold=True), fill=GREEN)
    d.text((700, 1060), "Week 32 exercise advice", font=get_font(18), fill=TEXT_MUTED)
    
    d.text((90, 1140), "🔒 Privacy First: Zero patient identifiers or credentials exposed.", font=get_font(18), fill=(255, 171, 0))
    
    out = os.path.join(CAROUSEL_DIR, "05-mobile.png")
    img.save(out)
    return img

# -------------------------------------------------------------
# SLIDE 6: WEB APPLICATION
# -------------------------------------------------------------
def generate_slide_6():
    img = create_base_canvas(6, 10, "WEB APPLICATION • REACT & VITE")
    draw = ImageDraw.Draw(img)
    
    draw.text((60, 140), "Clinical Web Portal", font=get_font(52, bold=True), fill=TEXT_WHITE)
    draw.text((60, 210), "React 18, TypeScript, Vite & Supabase Integration", font=get_font(26), fill=CYAN)
    
    web_cards = [
        ("📁 Medical Report Upload & Parsing", "Supports multi-format report uploads (PDF, DOCX, JPG/PNG). Extracts maternal biomarkers including Hemoglobin, Blood Pressure, and Glucose in real time.", CYAN),
        ("📊 Dynamic Indicators & Risk Matrix", "Visual clinical scorecard grading vital signs into clear categories (Good, Warning, Danger) with reference ranges and abnormal flag alerts.", GREEN),
        ("🩺 Obstetrician & Clinic Locator", "Integrated doctor recommendation engine matching high-risk patients with nearby maternal-fetal medicine specialists and hospitals.", TEAL),
        ("⚡ High-Speed Vite Production Bundle", "Optimized with Vite 6 & TailwindCSS for sub-second page loads and seamless mobile/desktop responsiveness.", YELLOW)
    ]
    
    cy = 280
    for title, desc, col in web_cards:
        img = draw_card(img, [60, cy, WIDTH - 60, cy + 200], bg_color=(20, 33, 65, 230), border_color=(col[0], col[1], col[2], 90), radius=18)
        d = ImageDraw.Draw(img)
        d.text((90, cy + 25), title, font=get_font(30, bold=True), fill=col)
        
        words = desc.split()
        lines = []
        cur = ""
        for w in words:
            if len(cur + " " + w) < 70:
                cur += (" " if cur else "") + w
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
            
        ly = cy + 75
        for line in lines:
            d.text((90, ly), line, font=get_font(22), fill=TEXT_WHITE)
            ly += 32
            
        cy += 230
        
    out = os.path.join(CAROUSEL_DIR, "06-website.png")
    img.save(out)
    return img

# -------------------------------------------------------------
# SLIDE 7: AI & RISK ANALYSIS PIPELINE
# -------------------------------------------------------------
def generate_slide_7():
    img = create_base_canvas(7, 10, "CLINICAL RISK CLASSIFICATION")
    draw = ImageDraw.Draw(img)
    
    draw.text((60, 140), "AI & Risk Analysis Pipeline", font=get_font(52, bold=True), fill=TEXT_WHITE)
    draw.text((60, 210), "Multi-Tiered Biomarker Assessment & Decision Support", font=get_font(26), fill=CYAN)
    
    tiers = [
        ("🟢 GOOD / LOW RISK", "• Normal Blood Pressure (<120/80 mmHg)\n• Healthy Hemoglobin (Hb > 11 g/dL)\n• Normal Fetal Heart Rate (110–160 bpm)\n• Action: Routine prenatal monitoring & balanced diet", GREEN),
        ("🟡 WARNING / MODERATE RISK", "• Borderline Anemia (Hb 9.0–10.9 g/dL)\n• Elevated Blood Pressure (120-139 / 80-89 mmHg)\n• Mild Gestational Glucose elevation\n• Action: Diet adjustments & follow-up within 7 days", YELLOW),
        ("🔴 DANGER / HIGH RISK", "• Severe Hypertension (BP >= 140/90 mmHg)\n• Critical Anemia (Hb < 8.0 g/dL) or abnormal FHR\n• Heavy bleeding, fluid leakage, or severe cramps\n• Action: Immediate hospital triage & emergency contact", CORAL)
    ]
    
    cy = 280
    for title, desc, col in tiers:
        img = draw_card(img, [60, cy, WIDTH - 60, cy + 240], bg_color=(20, 33, 65, 230), border_color=(col[0], col[1], col[2], 120), radius=18)
        d = ImageDraw.Draw(img)
        d.text((90, cy + 25), title, font=get_font(30, bold=True), fill=col)
        
        ly = cy + 75
        for line in desc.split("\n"):
            d.text((90, ly), line, font=get_font(22), fill=TEXT_WHITE)
            ly += 34
            
        cy += 270

    d = ImageDraw.Draw(img)
    d.text((60, 1150), "⚠️ Disclaimer: PreCare provides decision-support risk scoring and does not replace medical diagnosis.", font=get_font(18), fill=TEXT_MUTED)
    
    out = os.path.join(CAROUSEL_DIR, "07-ai-analysis.png")
    img.save(out)
    return img

# -------------------------------------------------------------
# SLIDE 8: AUTOMATED TESTING
# -------------------------------------------------------------
def generate_slide_8():
    img = create_base_canvas(8, 10, "QUALITY & AUTOMATED TESTING")
    draw = ImageDraw.Draw(img)
    
    draw.text((60, 140), "Enterprise Automated Testing", font=get_font(52, bold=True), fill=TEXT_WHITE)
    draw.text((60, 210), "600+ Automated Tests Across Web, Mobile & Backend", font=get_font(26), fill=CYAN)
    
    # 4 Metric Cards
    metrics = [
        ("300", "Selenium Web Tests", "100% automated clinical test case validation on web portal with HTML reporting.", CYAN),
        ("305", "Appium Mobile Tests", "SwiftUI authentication, password toggle, Maya AI chat, and appointments in 0.16s.", GREEN),
        ("836", "Req / Sec Throughput", "Concurrent load stress testing with Locust (3.94 ms average latency).", TEAL),
        ("0", "Database Locks", "SQLite Write-Ahead Logging (WAL) mode for resilient concurrent multi-threading.", YELLOW)
    ]
    
    card_coords = [
        (60, 280, 520, 680),
        (560, 280, 1020, 680),
        (60, 720, 520, 1120),
        (560, 720, 1020, 1120)
    ]
    
    for (num, title, desc, col), (x0, y0, x1, y1) in zip(metrics, card_coords):
        img = draw_card(img, [x0, y0, x1, y1], bg_color=(20, 33, 65, 230), border_color=(col[0], col[1], col[2], 120), radius=20)
        d = ImageDraw.Draw(img)
        d.text((x0 + 30, y0 + 30), num, font=get_font(72, bold=True), fill=col)
        d.text((x0 + 30, y0 + 130), title, font=get_font(26, bold=True), fill=TEXT_WHITE)
        
        words = desc.split()
        lines = []
        cur = ""
        for w in words:
            if len(cur + " " + w) < 32:
                cur += (" " if cur else "") + w
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
            
        ly = y0 + 190
        for line in lines:
            d.text((x0 + 30, ly), line, font=get_font(20), fill=TEXT_MUTED)
            ly += 30
            
    out = os.path.join(CAROUSEL_DIR, "08-testing.png")
    img.save(out)
    return img

# -------------------------------------------------------------
# SLIDE 9: CI/CD WORKFLOWS
# -------------------------------------------------------------
def generate_slide_9():
    img = create_base_canvas(9, 10, "CI/CD & DEVOPS AUTOMATION")
    draw = ImageDraw.Draw(img)
    
    draw.text((60, 140), "GitHub Actions CI/CD Pipeline", font=get_font(52, bold=True), fill=TEXT_WHITE)
    draw.text((60, 210), "6 Automated Workflows Ensuring Continuous Quality", font=get_font(26), fill=CYAN)
    
    workflows = [
        ("combined-tests.yml", "Master Pipeline: Runs website Selenium tests, mobile Appium tests, and backend security in unified stages.", CYAN),
        ("selenium-tests.yml", "Web Testing: Executes 300 clinical cases with headless Chrome & uploads HTML artifact.", GREEN),
        ("appium-tests.yml", "Mobile Testing: Executes 305 Appium mobile tests in 0.16s with detailed test reports.", TEAL),
        ("backend-security.yml", "Security & Quality: Automated pip-audit dependency CVE scan, Bandit SAST, and Flake8.", YELLOW),
        ("load-tests.yml", "Performance: Headless Locust 50-user concurrent load test measuring p95 latencies.", CORAL),
        ("package-release.yml", "Release Packaging: Creates clean, single-archive PreCare-complete-project.zip artifact.", (180, 140, 255))
    ]
    
    cy = 280
    for name, desc, col in workflows:
        img = draw_card(img, [60, cy, WIDTH - 60, cy + 135], bg_color=(18, 30, 60, 240), border_color=(col[0], col[1], col[2], 120), radius=16)
        d = ImageDraw.Draw(img)
        d.text((90, cy + 20), f"⚡ {name}", font=get_font(26, bold=True), fill=col)
        
        words = desc.split()
        lines = []
        cur = ""
        for w in words:
            if len(cur + " " + w) < 70:
                cur += (" " if cur else "") + w
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
            
        ly = cy + 65
        for line in lines:
            d.text((90, ly), line, font=get_font(19), fill=TEXT_WHITE)
            ly += 28
            
        cy += 150
        
    out = os.path.join(CAROUSEL_DIR, "09-cicd.png")
    img.save(out)
    return img

# -------------------------------------------------------------
# SLIDE 10: TECH STACK & CONCLUSION
# -------------------------------------------------------------
def generate_slide_10():
    img = create_base_canvas(10, 10, "TECH STACK & SUMMARY")
    draw = ImageDraw.Draw(img)
    
    draw.text((60, 140), "Technology Stack & Key Highlights", font=get_font(52, bold=True), fill=TEXT_WHITE)
    draw.text((60, 210), "Full-Stack • Mobile • AI • Automation • Security", font=get_font(26), fill=CYAN)
    
    tech_stacks = [
        ("📱 Mobile Stack", "Swift, SwiftUI, iOS 17+, MVVM Architecture, Xcode, Codemagic", CYAN),
        ("🌐 Web Stack", "React 18, TypeScript, Vite, TailwindCSS, Supabase Integration", TEAL),
        ("⚡ Backend Stack", "Python 3.13, FastAPI (40 Endpoints), SQLAlchemy, SQLite WAL Mode", GREEN),
        ("🤖 AI & OCR", "Google Gemini Flash, Document Parsing, OCR Extraction, Rule Engine", YELLOW),
        ("🧪 Automation", "300 Selenium Tests, 305 Appium Tests, Locust Load Testing", CORAL),
        ("🛡️ DevOps & Security", "6 GitHub Actions Workflows, pip-audit, Bandit SAST, Zero-Leak Secrets", (180, 140, 255))
    ]
    
    cy = 280
    for category, items, col in tech_stacks:
        img = draw_card(img, [60, cy, WIDTH - 60, cy + 115], bg_color=(18, 30, 60, 240), border_color=(col[0], col[1], col[2], 100), radius=14)
        d = ImageDraw.Draw(img)
        d.text((90, cy + 18), category, font=get_font(24, bold=True), fill=col)
        d.text((90, cy + 60), items, font=get_font(20), fill=TEXT_WHITE)
        cy += 135
        
    # Closing Card
    close_rect = [60, 1100, WIDTH - 60, 1230]
    img = draw_card(img, close_rect, bg_color=(0, 242, 254, 25), border_color=(0, 242, 254, 180), radius=18)
    d = ImageDraw.Draw(img)
    d.text((90, 1125), "🌟 PreCare Consolidated Platform", font=get_font(26, bold=True), fill=TEXT_WHITE)
    d.text((90, 1170), "Download the complete project in ONE archive: github.com/Pragna73/PreCare", font=get_font(20, bold=True), fill=CYAN)
    
    out = os.path.join(CAROUSEL_DIR, "10-tech-stack.png")
    img.save(out)
    return img

# -------------------------------------------------------------
# BUILD ALL SLIDES & PDF
# -------------------------------------------------------------
print("Generating LinkedIn Carousel Slides...")
slide_images = [
    generate_slide_1(),
    generate_slide_2(),
    generate_slide_3(),
    generate_slide_4(),
    generate_slide_5(),
    generate_slide_6(),
    generate_slide_7(),
    generate_slide_8(),
    generate_slide_9(),
    generate_slide_10()
]

# Copy supporting diagrams to PreCare_LinkedIn_Images
for s_num in range(1, 11):
    src = os.path.join(CAROUSEL_DIR, f"{s_num:02d}-*.png")
    matches = glob.glob(src)
    for m in matches:
        dest = os.path.join(IMAGES_DIR, os.path.basename(m))
        Image.open(m).save(dest)

print("Compiling PreCare_LinkedIn_Project_Report.pdf...")
# Convert images to RGB for PDF
rgb_images = [im.convert("RGB") for im in slide_images]
rgb_images[0].save(
    PDF_PATH,
    save_all=True,
    append_images=rgb_images[1:],
    resolution=150.0
)

print(f"✓ Successfully generated all 10 Carousel PNGs in {CAROUSEL_DIR}")
print(f"✓ Successfully generated Supporting Images in {IMAGES_DIR}")
print(f"✓ Successfully generated PDF report at {PDF_PATH}")
