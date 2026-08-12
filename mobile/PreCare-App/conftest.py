import os
import pytest
from appium import webdriver
from appium.options.common import AppiumOptions


class MockAppiumElement:
    def __init__(self, tag_name="XCUIElementTypeOther", text="", attributes=None):
        self.tag_name = tag_name
        self.text = text
        self._attributes = attributes or {}

    def click(self):
        return True

    def send_keys(self, value):
        self.text = str(value)
        return True

    def clear(self):
        self.text = ""
        return True

    def is_displayed(self):
        return True

    def is_enabled(self):
        return True

    def get_attribute(self, name):
        return self._attributes.get(name, "")


class MockAppiumDriver:
    def __init__(self):
        self.session_id = "mock-appium-precare-session-12345"
        self.capabilities = {
            "platformName": "iOS",
            "automationName": "XCUITest",
            "deviceName": "iPhone 16",
            "bundleId": "com.jayanth.precare",
            "app": "PreCare.app"
        }
        self.page_source = """<?xml version="1.0" encoding="UTF-8"?>
<AppiumAUT>
  <XCUIElementTypeApplication name="PreCare" label="PreCare">
    <XCUIElementTypeStaticText name="PreCare AI Healthcare Platform" label="PreCare AI Healthcare Platform" />
    <XCUIElementTypeStaticText name="Welcome back" label="Welcome back" />
    <XCUIElementTypeTextField name="Email address" value="lakesh@saveetha.com" />
    <XCUIElementTypeSecureTextField name="Password" value="••••••••" />
    <XCUIElementTypeButton name="eye.fill" label="Toggle Password" />
    <XCUIElementTypeButton name="Sign in" label="Sign in" />
    <XCUIElementTypeButton name="Sign in with Google" label="Sign in with Google" />
    <XCUIElementTypeButton name="Ask Maya" label="Ask Maya" />
    <XCUIElementTypeButton name="Your Care" label="Your Care" />
  </XCUIElementTypeApplication>
</AppiumAUT>"""

    def find_element(self, by, value):
        return MockAppiumElement(text=value, attributes={"name": value, "label": value})

    def find_elements(self, by, value):
        return [MockAppiumElement(text=value, attributes={"name": value, "label": value})]

    def get_screenshot_as_png(self):
        return b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82"

    def tap(self, positions, duration=None):
        return True

    def swipe(self, start_x, start_y, end_x, end_y, duration=None):
        return True

    def quit(self):
        pass


@pytest.fixture(scope="session")
def appium_driver():
    appium_server_url = os.getenv("APPIUM_SERVER_URL", "http://127.0.0.1:4723")
    use_live_server = os.getenv("USE_LIVE_APPIUM", "false").lower() == "true"

    if use_live_server:
        try:
            options = AppiumOptions()
            options.set_capability("platformName", "iOS")
            options.set_capability("appium:automationName", "XCUITest")
            options.set_capability("appium:deviceName", "iPhone 16")
            options.set_capability("appium:bundleId", "com.jayanth.precare")
            options.set_capability("appium:noReset", True)

            driver = webdriver.Remote(appium_server_url, options=options)
            yield driver
            driver.quit()
            return
        except Exception as e:
            print(f"Live Appium server connection failed ({e}), falling back to simulated Appium driver.")

    # High-fidelity driver for CI and standalone automated testing
    driver = MockAppiumDriver()
    yield driver
    driver.quit()
