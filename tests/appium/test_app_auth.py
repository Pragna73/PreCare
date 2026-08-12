import pytest


def test_app_login_and_password_eye_toggle(appium_driver):
    """Test mobile login screen and password eye icon visibility toggle."""
    assert appium_driver.session_id is not None

    email_field = appium_driver.find_element("accessibility id", "Email address")
    email_field.send_keys("priya.sharma@example.com")

    password_field = appium_driver.find_element("accessibility id", "Password")
    password_field.send_keys("SecurePass123!")

    # Test Eye icon toggle button
    eye_button = appium_driver.find_element("accessibility id", "eye.fill")
    assert eye_button.is_displayed()
    eye_button.click()

    # Test Sign In button
    sign_in_btn = appium_driver.find_element("accessibility id", "Sign in")
    assert sign_in_btn.is_enabled()
    sign_in_btn.click()


def test_app_registration_with_mandatory_emergency_contact(appium_driver):
    """Test mobile signup requiring emergency family contact."""
    assert appium_driver.session_id is not None

    name_field = appium_driver.find_element("accessibility id", "Full name")
    name_field.send_keys("Priya Sharma")

    contact_field = appium_driver.find_element("accessibility id", "Emergency Contact Phone (Mandatory)")
    contact_field.send_keys("+91 98765 43210")
    assert contact_field.is_displayed()
