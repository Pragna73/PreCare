from __future__ import annotations

from datetime import datetime, timedelta

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from sqlalchemy.orm import Session

from app.config import settings
from app.llm_factory import get_llm
from app.models import HealthMetricEntry, MayaMessage, Report

NON_HEALTH_REPLY = (
    "I don't know the answer for you provided. I only assisted you through the health related questions."
)


import re


def _fallback_reply(user_message: str, latest_risk: str | None, user_name: str = "there") -> str:
    msg = user_message.lower().strip()

    # 1. Severe Clinical Emergencies (Immediate Triage)
    if any(k in msg for k in ["heavy bleeding", "severe pain", "faint", "unconscious", "chest pain", "leakage", "fluid leak", "water broke"]):
        return (
            "⚠️ **Immediate Clinical Attention Recommended**:\n\n"
            "These symptoms require urgent in-person medical evaluation. Please contact your nearest maternity hospital emergency department immediately and remain accompanied by a family member or caregiver."
        )

    # 2. Tea, Coffee, & Caffeine Limits
    if re.search(r"\b(tea|coffee|caffeine|green tea|espresso|cappuccino)\b", msg):
        return (
            "☕ **Caffeine Guidelines in Pregnancy**:\n\n"
            "• **Safe Limit**: Health organizations (ACOG/WHO) recommend keeping daily caffeine intake below **200 mg** (roughly 1 to 2 standard cups of brewed coffee or 2–3 cups of black/green tea).\n"
            "• **Tips**: Switch to decaf, herbal infusions (like chamomile or peppermint), or tender coconut water in the afternoon to avoid interfering with iron absorption and sleep."
        )

    # 3. Fruits & Foods to Avoid (Papaya, Pineapple, Seafood, Raw Eggs)
    if re.search(r"\b(papaya|pineapple|raw egg|sushi|seafood|fish|unpasteurized|cheese|alcohol|smoke|safe to eat)\b", msg):
        return (
            "🥑 **Food Safety & Dietary Precautions**:\n\n"
            "• **Papaya**: Ripe sweet papaya (yellow/orange) is safe in moderation. Strictly avoid **unripe or semi-ripe green papaya**, as its latex and papain can trigger uterine contractions.\n"
            "• **Pineapple**: Safe in normal culinary quantities. Bromelain is concentrated mainly in the core/stem.\n"
            "• **Strictly Avoid**: Unpasteurized soft cheeses, raw/undercooked eggs, sushi/raw fish, high-mercury fish (shark, swordfish, king mackerel), and alcohol."
        )

    # 4. Swelling in Feet & Legs (Edema)
    if re.search(r"\b(swollen|swelling|feet|ankle|edema|puffy|leg cramp|cramps in leg)\b", msg):
        return (
            "🦶 **Managing Swollen Feet & Leg Cramps**:\n\n"
            "• **Elevation**: Rest with your feet elevated above heart level for 15–20 minutes several times a day.\n"
            "• **Left-Side Resting**: Lie on your left side to relieve pressure from the inferior vena cava and improve venous return.\n"
            "• **Hydration & Compression**: Drink plenty of water and consider wearing graduated maternity compression stockings.\n"
            "• ⚠️ *Warning Sign*: If swelling is sudden, asymmetrical in one calf, or involves your hands and face, notify your doctor promptly to rule out preeclampsia."
        )

    # 5. Acidity, Heartburn & GERD
    if re.search(r"\b(acidity|heartburn|gerd|acid reflux|burning chest|indigestion|gas|bloating)\b", msg):
        return (
            "🔥 **Relief for Prenatal Acidity & Heartburn**:\n\n"
            "• **Small, Frequent Meals**: Eat 5–6 small meals throughout the day rather than 3 large ones to avoid gastric distension.\n"
            "• **Timing**: Avoid lying down within 2 hours after meals; keep your head elevated 6 inches with extra pillows while sleeping.\n"
            "• **Soothing Remedies**: Sip cold milk, chew a few fennel seeds (saunf), or drink coconut water.\n"
            "• **Avoid**: Greasy fried foods, strong citrus, excessive chili, carbonated sodas, and chocolate."
        )

    # 6. Hemoglobin, Anemia & Iron Intake
    if re.search(r"\b(hemoglobin|hb|anemia|anaemia|iron|low blood|ferritin)\b", msg):
        return (
            "🩸 **Boosting Hemoglobin (Hb) & Treating Prenatal Anemia**:\n\n"
            "• **Target Range**: Optimal prenatal hemoglobin is between **11.0 – 14.0 g/dL**.\n"
            "• **Iron-Rich Foods**: Spinach, drumstick leaves (moringa), lentils, beetroot, dates, raisins, pomegranate, jaggery, and eggs/lean meat.\n"
            "• **Enhance Absorption**: Pair iron sources with Vitamin C (lemon juice, oranges, amla).\n"
            "• **Avoid Interference**: Do not take your prenatal iron tablet with milk, tea, or coffee; take it with water or citrus juice."
        )

    # 7. Prenatal Vitamins, Supplements & Folic Acid
    if re.search(r"\b(vitamin|vitamins|supplement|folic acid|folate|calcium tablet|iron tablet|dha)\b", msg):
        return (
            "💊 **Essential Prenatal Vitamins & Supplements**:\n\n"
            "• **Folic Acid (400–800 mcg)**: Crucial in the 1st trimester for neural tube development and spine formation.\n"
            "• **Iron & Calcium**: Taken separately (at different times of the day) as calcium inhibits iron absorption.\n"
            "• **DHA / Omega-3**: Supports fetal brain and retinal development.\n"
            "• **Vitamin D3**: Enhances maternal calcium uptake for fetal bone density."
        )

    # 8. Travel, Flights & Seatbelt Safety (with week personalization & stemmed matching)
    if re.search(r"\b(travel\w*|fly\w*|flight\w*|trip\w*|driv\w*|car\w*|seatbelt\w*|journey\w*|vacation\w*|holiday\w*|transit\w*)\b", msg):
        week_match = re.search(r"\b(?:week|wk)\s*(\d{1,2})\b", msg) or re.search(r"\b(\d{1,2})\s*(?:th|st|nd|rd)?\s*(?:weeks?|wks?)\b", msg) or re.search(r"\bin\s*(\d{1,2})\b", msg)
        week = int(week_match.group(1)) if week_match else None

        if week and week >= 28:
            return (
                f"✈️ **Travel Guidance for Week {week} (3rd Trimester)**:\n\n"
                f"Traveling at **Week {week}** is generally permitted for low-risk pregnancies, with key precautions:\n\n"
                "• **Doctor Clearance & Fit-to-Fly**: Obtain a travel certificate from your obstetrician confirming your estimated due date and uncomplicated status.\n"
                "• **Airlines Cutoffs**: Most domestic airlines permit travel up to 36 weeks (32 weeks for twins), but check carrier guidelines before booking.\n"
                "• **Road Trips & Car Travel**: Stop every 60–90 minutes to step out, walk, and stretch your calves to maintain venous circulation.\n"
                "• **Seatbelt Rule**: Position the lap strap low across your hips *under* your baby bump, with the diagonal strap between your breasts.\n"
                "• **Hydration & Compression**: Wear maternity compression stockings and drink plenty of fluids to prevent deep vein thrombosis (DVT).\n"
                "• **Emergency Preparedness**: Carry your antenatal medical file and identify the nearest maternity hospital at your destination.\n\n"
                "⚠️ *Avoid Travel If*: You have high blood pressure, preeclampsia symptoms, vaginal bleeding, or cervical shortening."
            )
        else:
            return (
                "✈️ **Travel Safety During Pregnancy**:\n\n"
                "• **Safest Window**: The 2nd trimester (14–28 weeks) is typically the safest and most comfortable for travel.\n"
                "• **Airlines**: Most airlines allow travel up to 36 weeks with obstetric clearance.\n"
                "• **In Transit**: Wear loose clothing, stay hydrated, wear compression socks, and walk every 60–90 minutes to prevent blood clots.\n"
                "• **Seatbelt Rule**: Position the lap belt low across your hips *under* your bump, and the shoulder strap across your collarbone."
            )

    # 9. Exercise, Walking & Prenatal Yoga (with typo tolerance & week personalization)
    if re.search(r"\b(ex[ce]{0,2}r[sc]{1,2}i[sc]{1,2}e?s?|workout[s]?|walk|walking|yoga|kegel[s]?|squat[s]?|stretch|stretching|gym|physical\s*activit\w*|birth(?:ing)?\s*ball|pelvic\s*floor|posture)\b", msg):
        week_match = re.search(r"\b(?:week|wk)\s*(\d{1,2})\b", msg) or re.search(r"\b(\d{1,2})\s*(?:th|st|nd|rd)?\s*week\b", msg)
        week = int(week_match.group(1)) if week_match else None

        if week and week >= 28:
            return (
                f"🧘‍♀️ **Safe & Gentle Exercises for Week {week} (3rd Trimester)**:\n\n"
                "As your baby grows and your center of gravity shifts, focus on pelvic opening and lower back relief:\n\n"
                "• **Pelvic Floor & Kegels**: 3 sets of 10 contractions daily to prepare the pelvic floor for delivery.\n"
                "• **Birthing Ball Hip Circles & Pelvic Tilts**: Sitting on an exercise ball making gentle circles helps baby's head engage.\n"
                "• **Cat-Cow on All Fours**: Eases lumbar pressure and relieves sciatic nerve strain.\n"
                "• **Tailor Sitting / Butterfly Stretch**: Gently opens inner thighs and pelvic outlet.\n"
                "• **Gentle 15–20 Min Walking**: On flat ground to maintain circulation and reduce foot swelling.\n\n"
                "⚠️ *Safety Tips*: Avoid lying flat on your back, heavy lifting, and stop immediately if you feel breathless, dizzy, or notice pelvic pressure."
            )
        elif week and week >= 14:
            return (
                f"🧘‍♀️ **Recommended Exercises for Week {week} (2nd Trimester)**:\n\n"
                "• **Brisk Walking**: 25–30 minutes daily strengthens cardiovascular fitness and stamina.\n"
                "• **Prenatal Yoga & Pelvic Rocking**: Stretches the hamstrings, opens hips, and strengthens back muscles.\n"
                "• **Squats & Wall Sits**: Strengthens glutes and thighs to support extra pregnancy weight.\n"
                "• **Kegel Exercises**: Helps maintain pelvic organ support.\n\n"
                "💡 *Stay well-hydrated and avoid high-impact jumping or contact sports.*"
            )
        else:
            return (
                "🧘‍♀️ **Safe Prenatal Exercises & Physical Activity**:\n\n"
                "• **Brisk Walking**: 20–30 minutes daily on level ground.\n"
                "• **Prenatal Yoga & Gentle Stretches**: Relieves muscular tension and calms the nervous system.\n"
                "• **Pelvic Floor (Kegels)**: 10–15 repetitions, 3 times daily.\n"
                "• **Swimming / Water Aerobics**: Takes pressure off joints and provides soothing buoyancy.\n\n"
                "💡 *Stay hydrated, avoid overheating, and always warm up and cool down gently.*"
            )

    # 10. Hospital Bag Checklist
    if re.search(r"\b(hospital bag|delivery bag|pack|packing|what to take to hospital)\b", msg):
        return (
            "🎒 **Hospital Bag Packing Checklist (Pack by Week 35–36)**:\n\n"
            "• **For Mother**: Medical records, ID/insurance cards, 2–3 nursing gowns, comfortable loose clothes, maternity sanitary pads, non-slip slippers, nursing bra, toiletries, and phone charger.\n"
            "• **For Baby**: 3–4 newborn onesies/sleepsuits, swaddle wraps, newborn diapers, wipes, baby blanket, cap, mittens, and infant car seat for discharge.\n"
            "• **For Birth Partner**: Snacks, water bottle, cash/cards, camera, and spare clothes."
        )

    # 11. Water Breaking & Early Labor
    if re.search(r"\b(water break|water breaks|water broke|water breaking|amniotic fluid|mucus plug|bloody show|labor start)\b", msg):
        return (
            "💧 **Water Breaking (Rupture of Membranes) & Early Labor**:\n\n"
            "• **Signs**: A sudden gush or a continuous slow trickle of clear or pale fluid from the vagina.\n"
            "• **COAT Assessment**: Note the **C**olor, **O**dor, **A**mount, and **T**ime.\n"
            "• **Immediate Step**: Put on a clean sanitary pad (do not use tampons) and proceed to your maternity hospital, even if you are not yet feeling strong contractions."
        )

    # 12. Round Ligament Pain & Pelvic Aches
    if re.search(r"\b(round ligament|groin|pelvic pain|pelvic pressure|pubic pain|lightning crotch)\b", msg):
        return (
            "⚡ **Managing Round Ligament & Pelvic Girdle Pain**:\n\n"
            "• **Causes**: Sharp, stretching aches in the lower abdomen or groin caused by hormones (relaxin) and the expanding uterus.\n"
            "• **Relief**: Move gently when changing positions, apply a warm compress to the area, wear a supportive maternity belly band, and practice gentle pelvic rocking.\n"
            "• ⚠️ *Call Doctor If*: Pain is accompanied by fever, chills, burning urination, or spotting."
        )

    # 13. Sex & Intimacy During Pregnancy
    if re.search(r"\b(sex|intimacy|intercourse|sexual)\b", msg):
        return (
            "❤️ **Intimacy & Sex During Pregnancy**:\n\n"
            "• In an uncomplicated, low-risk pregnancy, sexual intercourse is completely safe and will not harm the baby (who is cushioned by the amniotic sac and uterine wall).\n"
            "• **When to Abstain**: If you have placenta previa, cervical insufficiency, unexplained vaginal bleeding, or a history of preterm labor. Always follow your obstetrician's personalized advice."
        )

    # 14. Breastfeeding Preparation & Postpartum Care
    if re.search(r"\b(breastfeed|breastfeeding|lactation|colostrum|milk supply|postpartum|after delivery|c section recovery|normal recovery)\b", msg):
        return (
            "🤱 **Breastfeeding & Postpartum Essentials**:\n\n"
            "• **Colostrum**: In the first 2–4 days, your breasts produce nutrient-rich, antibody-dense liquid gold (colostrum) perfectly sized for a newborn's tiny stomach.\n"
            "• **Latching Tip**: Ensure baby takes a deep latch covering the lower areola, not just the nipple.\n"
            "• **Postpartum Care**: Stay well-rested, eat warm balanced meals, stay hydrated with 3+ liters of fluids, and practice gentle sitz baths for perineal healing."
        )

    # 15. Diet & Nutrition by Trimester/Week
    if re.search(r"\b(diet|food|nutrition|eat|meal|calories|recipe|fruits?|vegetables?|protein|breakfast|lunch|dinner|snack)\b", msg):
        week_match = re.search(r"\b(?:week|wk)\s*(\d{1,2})\b", msg) or re.search(r"\b(\d{1,2})\s*(?:th|st|nd|rd)?\s*week\b", msg)
        week = int(week_match.group(1)) if week_match else 20

        if week <= 13:
            trimester_diet = (
                "• **Folate & Vitamin B6**: Spinach, lentils, fortified cereals, and bananas to curb early nausea.\n"
                "• **Small, Frequent Meals**: Keeps blood sugar steady and eases morning sickness.\n"
                "• **Hydration**: 8–10 glasses of water, ginger tea, or coconut water."
            )
        elif 14 <= week <= 27:
            trimester_diet = (
                "• **Iron-Rich Foods**: Spinach, lentils, beetroot, beans, and lean proteins to support expanding blood volume.\n"
                "• **Calcium & Vitamin D**: Milk, yogurt, paneer, and ragi for baby's bone and teeth calcification.\n"
                "• **Omega-3 Fatty Acids**: Walnuts, chia seeds, and flaxseeds for fetal brain and vision development.\n"
                "• **High Fiber**: Oats, whole grains, and fresh fruits to prevent digestive sluggishness.\n"
                "• **Hydration**: At least 2.5–3 liters of water daily."
            )
        else:
            trimester_diet = (
                "• **Complex Carbs & Protein**: Sprouted pulses, eggs/tofu, and quinoa to sustain fetal weight gain.\n"
                "• **Vitamin C & Iron Combo**: Citrus fruits with greens for optimal iron absorption.\n"
                "• **Electrolytes & Fluid**: Fresh fruit juices and tender coconut water to maintain healthy amniotic fluid levels."
            )

        return (
            f"Here is a balanced, nutrient-dense diet recommendation for **Week {week}**:\n\n"
            f"{trimester_diet}\n\n"
            f"💡 *Tip: Avoid raw/unpasteurized dairy, excess caffeine, and overly processed salty foods.*"
        )

    # 16. Doctor Consultation Follow-up
    if re.search(r"\b(consulted|visited|saw|met|talked to|spoke with)\s*(?:the|my|a)?\s*doctor\b|\bi have consulted doctor\b", msg):
        return (
            "That's wonderful that you have consulted your doctor! 🩺\n\n"
            "• Please ensure you follow all medications and clinical instructions given by your obstetrician.\n"
            "• If your doctor advised any specific blood tests, blood pressure tracking, or dietary modifications, keep monitoring them here in PreCare.\n\n"
            "Feel free to share any instructions or symptoms if you'd like guidance on tracking them!"
        )

    # 17. Fetal Movements & Kicks
    if re.search(r"\b(kick|movement|kicks|baby moving|fetal movement)\b", msg):
        return (
            "👶 **Fetal Movement & Kick Counts**:\n\n"
            "• From around 24–28 weeks, kick counts become regular.\n"
            "• **Standard Goal**: You should feel around 10 distinct movements within 2 hours while resting comfortably on your left side.\n"
            "• If you notice a sudden drop or absence in fetal movements, please contact your maternity clinic promptly for a quick Doppler check."
        )

    # 18. Common Symptoms (Nausea, Fatigue, Back Pain, Sleep)
    if re.search(r"\b(nausea|vomit|morning sickness)\b", msg):
        return (
            "🌸 **Soothing Tips for Nausea**:\n\n"
            "• Eat dry toast or crackers before getting out of bed.\n"
            "• Sip warm ginger or peppermint tea throughout the day.\n"
            "• Avoid oily, spicy, or heavy foods, and eat smaller meals every 2–3 hours."
        )

    if re.search(r"\b(back pain|backache|sleep|sleeping position|sleep position)\b", msg):
        return (
            "🛌 **Comfort & Sleep Posture**:\n\n"
            "• Sleep on your **left side** (SOS position) to optimize blood flow to the placenta and uterus.\n"
            "• Place a maternity pillow between your knees and behind your back for lumbar support.\n"
            "• Practice gentle pelvic tilts and avoid lifting heavy weights."
        )

    # 19. Fever, Headaches & Minor Ailments
    if re.search(r"\b(fever|headache|headaches|chills|cold|cough)\b", msg):
        return (
            "🌡️ **Fever & Headache Care During Pregnancy**:\n\n"
            "• **Hydration & Rest**: Rest in a cool, quiet room, drink plenty of fluids, and place a cool damp cloth across your forehead.\n"
            "• **Medications**: Avoid NSAIDs (like ibuprofen or aspirin). Only take medications explicitly prescribed by your obstetrician.\n"
            "• **When to seek care**: If your fever rises above 100.4°F (38°C) or if the headache is severe and accompanied by visual spots or facial swelling, please contact your healthcare provider immediately."
        )

    # 20. Blood Pressure & Preeclampsia Awareness
    if re.search(r"\b(bp|blood pressure|hypertension|preeclampsia)\b", msg):
        return (
            "❤️ **Maternal Blood Pressure Care**:\n\n"
            "• Healthy prenatal blood pressure is typically below **120/80 mmHg**.\n"
            "• Rest adequately on your left side and limit sodium intake.\n"
            "• If your BP reading is elevated or accompanied by severe headaches, visual spots, or sudden facial swelling, inform your doctor immediately."
        )

    # 21. Labor, Contractions & VBAC
    if re.search(r"\b(labor|labour|contraction|contractions|vbac|c section|normal delivery)\b", msg):
        return (
            "🤰 **Labor Signs & Delivery Preparedness**:\n\n"
            "• **True Labor**: Contractions that occur at regular intervals, get progressively closer, last 30–70 seconds, and do not ease with rest.\n"
            "• **Braxton Hicks**: Irregular 'practice' tightenings that subside when you change position or drink water.\n"
            "• **5-1-1 Rule**: Go to the hospital when contractions are 5 minutes apart, lasting 1 minute each, for at least 1 hour."
        )

    # 22. Greetings & General Inquiries
    if re.search(r"^(hi|hello|hey|good morning|good afternoon|good evening|maya)\b", msg):
        return (
            f"Hi {user_name}! I'm Maya, your personal maternal health assistant. 💕\n\n"
            "I can help you with:\n"
            "• Weekly nutrition and diet plans 🥗\n"
            "• Fetal development milestones 👶\n"
            "• Managing pregnancy symptoms 🌸\n"
            "• Tracking vitals & lab results 📊\n\n"
            "How are you feeling today?"
        )

    # 23. Supportive General Maternal Guidance
    return (
        f"Hi {user_name}! I'm here to support your prenatal wellness journey. You can ask me anything about weekly diet plans, fetal growth milestones, managing pregnancy symptoms, labor preparedness, or tracking your vitals. What would you like to know?"
    )


def _llm_reply(
    db: Session,
    user_id: int,
    user_message: str,
    latest_risk: str | None,
) -> str | None:
    try:
        llm = get_llm(settings.llm_model, temperature=0.3)
    except Exception:
        return None

    recent_messages = (
        db.query(MayaMessage)
        .filter(MayaMessage.user_id == user_id)
        .order_by(MayaMessage.created_at.desc())
        .limit(10)
        .all()
    )
    recent_messages.reverse()

    latest_metrics = (
        db.query(HealthMetricEntry)
        .filter(HealthMetricEntry.user_id == user_id)
        .order_by(HealthMetricEntry.created_at.desc())
        .first()
    )

    metrics_context = "No recent vitals uploaded."
    if latest_metrics:
        metrics_context = (
            f"Hemoglobin: {latest_metrics.hemoglobin:.1f} g/dL, "
            f"BP: {latest_metrics.systolic_bp}/{latest_metrics.diastolic_bp} mmHg, "
            f"Glucose: {latest_metrics.blood_glucose:.0f} mg/dL, "
            f"Weight: {latest_metrics.weight_kg:.1f} kg"
        )

    system_prompt = f"""
You are Maya, a caring pregnancy health assistant.

Rules:
- Only answer pregnancy and health related topics.
- If user asks non-health topics, reply exactly:
  "{NON_HEALTH_REPLY}"
- Never provide medical diagnosis.
- If symptoms are severe (heavy bleeding, fainting, severe pain, high fever), advise emergency care immediately.
- Be empathetic, concise, and action-oriented.
- Suggest next steps (upload report, book appointment, emergency) when helpful.

Context:
Latest risk: {latest_risk or 'N/A'}
Latest vitals: {metrics_context}
"""

    messages = [SystemMessage(content=system_prompt)]

    for item in recent_messages:
        if item.role == "assistant":
            messages.append(AIMessage(content=item.content))
        else:
            messages.append(HumanMessage(content=item.content))

    messages.append(HumanMessage(content=user_message))

    try:
        out = llm.invoke(messages)
    except Exception:
        return None

    reply = out.content if hasattr(out, "content") else str(out)
    return reply.strip() if reply else None


def chat_with_maya(db: Session, user_id: int, message: str) -> dict:
    from app.models import User
    user = db.query(User).filter(User.id == user_id).first()
    user_name = user.full_name.split()[0] if user and user.full_name else "there"

    # 🔐 Safe query (works with or without user_id column)
    query = db.query(Report).order_by(Report.created_at.desc())

    if hasattr(Report, "user_id"):
        query = query.filter(Report.user_id == user_id)

    last_report = query.first()
    latest_risk = last_report.risk_level if last_report else None

    try:
        user_row = MayaMessage(user_id=user_id, role="user", content=message)
        db.add(user_row)
        db.flush()
    except Exception:
        db.rollback()

    reply = _fallback_reply(message, latest_risk, user_name)
    if not reply:
        reply = _llm_reply(
            db=db,
            user_id=user_id,
            user_message=message,
            latest_risk=latest_risk,
        ) or NON_HEALTH_REPLY

    try:
        bot_row = MayaMessage(user_id=user_id, role="assistant", content=reply)
        db.add(bot_row)
        db.commit()
    except Exception:
        db.rollback()

    return {
        "reply": reply,
        "latest_risk": latest_risk or "N/A",
    }


def get_chat_history(db: Session, user_id: int, limit: int = 30) -> list[MayaMessage]:
    return (
        db.query(MayaMessage)
        .filter(MayaMessage.user_id == user_id)
        .order_by(MayaMessage.created_at.asc())
        .limit(limit)
        .all()
    )


def get_grouped_chat_history(db: Session, user_id: int, limit: int = 100) -> dict[str, list[MayaMessage]]:
    rows = (
        db.query(MayaMessage)
        .filter(MayaMessage.user_id == user_id)
        .order_by(MayaMessage.created_at.asc())
        .limit(limit)
        .all()
    )

    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)

    grouped = {
        "today": [],
        "yesterday": [],
        "earlier": [],
    }

    for row in rows:
        message_date = row.created_at.date() if row.created_at else today
        if message_date == today:
            grouped["today"].append(row)
        elif message_date == yesterday:
            grouped["yesterday"].append(row)
        else:
            grouped["earlier"].append(row)

    return grouped
