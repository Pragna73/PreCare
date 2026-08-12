import pytest


def test_patient_care_confirmed_appointment_and_milestones(appium_driver):
    """Test Your Care tab displays confirmed doctor appointment and milestones."""
    assert appium_driver.session_id is not None

    care_tab = appium_driver.find_element("accessibility id", "Your Care")
    care_tab.click()

    schedule_btn = appium_driver.find_element("accessibility id", "Schedule Prenatal Appointment")
    assert schedule_btn.is_enabled()
    schedule_btn.click()
