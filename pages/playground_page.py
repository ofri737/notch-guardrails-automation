from playwright.sync_api import expect

from pages.base_page import BasePage


class PlaygroundPage(BasePage):
    # =========================
    # LOCATORS
    # =========================

    EMAIL_INPUT = "textarea[placeholder*='mark@meta.com']"
    CONTENT_INPUT = "div.ql-editor[contenteditable='true']"
    SEND_AS_CUSTOMER_BUTTON = "button:has-text('Send as customer')"
    POLICY_FAILED_MESSAGE = "h6:has-text('Policy Failed')"

    # =========================
    # NAVIGATION
    # =========================

    def open(self, playground_base_url, version_id):
        url = (
            f"{playground_base_url}"
            f"?updatedAt=last48h"
            f"&category=Playground"
            f"&version={version_id}"
        )

        self.navigate(url)

    # =========================
    # ACTIONS
    # =========================

    def fill_email_input(self, email):
        self.fill(self.EMAIL_INPUT, email)

    def fill_content_input(self, content):
        content_input = self.page.locator(self.CONTENT_INPUT)
        content_input.click()
        content_input.fill(content)

    def click_send_as_customer(self):
        self.click(self.SEND_AS_CUSTOMER_BUTTON)

    def send_customer_message(self, email, content):
        self.fill_email_input(email)
        self.fill_content_input(content)
        self.click_send_as_customer()

    # =========================
    # WAITS
    # =========================

    def wait_for_policy_failed(self):
        self.page.locator(
            self.POLICY_FAILED_MESSAGE
        ).last.wait_for(
            state="visible",
            timeout=90000,
        )

    def wait_after_customer_message(self, timeout_ms=10000):
        self.page.wait_for_timeout(timeout_ms)

    # =========================
    # VALIDATIONS
    # =========================

    def is_policy_failed_displayed(self):
        policy_failed = self.page.locator(
            self.POLICY_FAILED_MESSAGE
        ).last

        return policy_failed.is_visible()

    def assert_policy_failed_displayed(self):
        self.wait_for_policy_failed()

        policy_failed = self.page.locator(
            self.POLICY_FAILED_MESSAGE
        ).last

        expect(policy_failed).to_be_visible()

    def assert_policy_failed_not_displayed(self):
        self.page.wait_for_timeout(10000)

        policy_failed = self.page.locator(
            self.POLICY_FAILED_MESSAGE
        ).last

        expect(policy_failed).not_to_be_visible()