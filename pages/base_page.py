from playwright.sync_api import expect


class BasePage:
    def __init__(self, page):
        self.page = page

    # =========================
    # LOCATORS
    # =========================
    def get_locator(self, locator):
        return self.page.locator(locator)

    # =========================
    # NAVIGATION
    # =========================
    def navigate(self, url):
        self.page.goto(url)

    # =========================
    # ACTIONS
    # =========================
    def click(self, locator):
        self.get_locator(locator).click()

    def fill(self, locator, value):
        self.get_locator(locator).fill(value)

    def press(self, locator, key):
        self.get_locator(locator).press(key)

    # =========================
    # GETTERS
    # =========================
    def get_text(self, locator):
        return self.get_locator(locator).inner_text()

    # =========================
    # WAITS
    # =========================
    def wait_for_visible(self, locator):
        self.get_locator(locator).wait_for(state="visible")

    def wait_for_hidden(self, locator):
        self.get_locator(locator).wait_for(state="hidden")

    # =========================
    # VALIDATIONS
    # =========================
    def is_visible(self, locator):
        return self.get_locator(locator).is_visible()

    def assert_visible(self, locator):
        expect(self.get_locator(locator)).to_be_visible()

    def assert_text_contains(self, locator, expected_text):
        expect(self.get_locator(locator)).to_contain_text(expected_text)

    # =========================
    # SCREENSHOTS
    # =========================
    def take_screenshot(self, path):
        self.page.screenshot(path=path, full_page=True)