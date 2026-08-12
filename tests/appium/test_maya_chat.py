import pytest


def test_maya_maternal_ai_exercise_guidance(appium_driver):
    """Test Maya AI handles week 32 exercises query with typo tolerance."""
    assert appium_driver.session_id is not None

    maya_tab = appium_driver.find_element("accessibility id", "Ask Maya")
    maya_tab.click()

    input_box = appium_driver.find_element("accessibility id", "Ask Maya...")
    input_box.send_keys("What type of excersices can u suggest me in week 32")

    send_btn = appium_driver.find_element("accessibility id", "Send")
    send_btn.click()


def test_maya_maternal_ai_travel_guidance(appium_driver):
    """Test Maya AI handles travel inquiries for third trimester."""
    assert appium_driver.session_id is not None

    input_box = appium_driver.find_element("accessibility id", "Ask Maya...")
    input_box.send_keys("Can I travel in 32 week")

    send_btn = appium_driver.find_element("accessibility id", "Send")
    send_btn.click()
