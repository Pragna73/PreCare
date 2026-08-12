import csv
from pathlib import Path
import pytest


CSV_FILE = (
    Path(__file__).resolve().parent.parent
    / "test_data"
    / "pregnancy_test_cases_300.csv"
)


def load_test_cases():
    with CSV_FILE.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


test_cases = load_test_cases()


@pytest.mark.parametrize(
    "case",
    test_cases,
    ids=[case["case_id"] for case in test_cases],
)
def test_precare_appium_pregnancy_case(case, appium_driver):
    # Verify driver session is active
    assert appium_driver.session_id is not None
    assert "PreCare" in appium_driver.page_source

    age = float(case["age"])
    gestational_age = float(case["gestational_age"])
    hb = float(case["hemoglobin"])
    systolic = float(case["systolic"])
    diastolic = float(case["diastolic"])
    fhr = float(case["fetal_heart_rate"])

    # Clinical validation rules
    is_hypertensive = systolic >= 140 or diastolic >= 90
    is_anemic = hb < 10.0
    is_fhr_abnormal = fhr < 110 or fhr > 160

    risk = "HIGH" if (is_hypertensive or (is_anemic and is_fhr_abnormal)) else ("MEDIUM" if (is_anemic or is_fhr_abnormal) else "LOW")

    assert risk in ["LOW", "MEDIUM", "HIGH"]

    print(
        f"Appium Mobile Test {case['case_id']}: "
        f"Age={age}, "
        f"GestationalAge={gestational_age}w, "
        f"Hb={hb}g/dL, "
        f"BP={systolic}/{diastolic}, "
        f"FHR={fhr}bpm -> Risk={risk}"
    )
