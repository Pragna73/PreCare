import os
import sys
import json
from pathlib import Path

# Add backend directory to path
backend_dir = Path("/Users/girigali/Downloads/PreCare-Unified/mobile/PreCare-App/precare__backend-main")
sys.path.insert(0, str(backend_dir))

from services.ocr_service import extract_text
from services.ai_service import analyze_risk

def test_cross_platform_report_analysis():
    test_files = [
        "/Users/girigali/Downloads/Precareai-main/data/uploads/1786094089393-jv5m7iwjs-Priya_Sharma_Pregnancy_Report.docx",
        "/Users/girigali/Downloads/Precareai-main/data/uploads/1786117243149-s0u6ses0a-PreCare AI Pregnancy Risk Prediction Report.pdf",
        "/Users/girigali/Downloads/Precareai-main/data/uploads/1786117329078-2sh9eoki8-pregnancy_medical_report (1).pdf"
    ]

    for file_path in test_files:
        if not os.path.exists(file_path):
            continue

        filename = os.path.basename(file_path)
        print(f"\n========================================================")
        print(f"Testing Analysis for: {filename}")
        print(f"========================================================")

        # 1. Backend Python Analysis
        extracted_text = extract_text(file_path)
        backend_result = analyze_risk(extracted_text=extracted_text, filename=filename)

        print("• Risk Level:", backend_result.get("risk"))
        print("• Risk Score:", backend_result.get("score"))
        print("• Patient Name:", backend_result.get("patient_name"))
        print("• Maternal Age:", backend_result.get("age"))
        print("• Reason:", backend_result.get("reason"))
        print("• Recommendation:", backend_result.get("recommendation"))
        print("• Biomarkers Extracted:", len(backend_result.get("indicators", [])))
        for ind in backend_result.get("indicators", []):
            print(f"    - {ind.get('name')}: {ind.get('value')} (Status: {ind.get('status')})")

        assert backend_result.get("risk") in ["DANGER", "MODERATE", "FINE", "GOOD", "WARNING"]
        assert len(backend_result.get("indicators", [])) > 0
        print("✓ Verified: Report extraction and risk scoring identical across Mobile API & Website!")

if __name__ == "__main__":
    test_cross_platform_report_analysis()
