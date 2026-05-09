from pages.base_page import BasePage


class GuardrailsPage(BasePage):
    # =========================
    # LOCATORS
    # =========================

    EMAIL_TAB = "button:has-text('Email'), [role='tab']:has-text('Email')"
    EMAIL_INPUT = "div:has-text('Email') textarea:visible"
    ADD_PATTERN_BUTTON = "button:has-text('Enter'):visible"

    SAVE_BUTTON = "[data-testid='config-save-button']"
    CONFIRM_SAVE_BUTTON = "button:has-text('Save'):visible"

    DEPLOY_BUTTON = "button:has-text('Deploy')"
    PUBLISH_CHANGES_BUTTON = "button:has-text('Publish Changes')"
    DEPLOY_CHANGES_BUTTON = "button:has-text('Deploy Changes')"
    FINAL_DEPLOY_BUTTON = "button:has-text('Deploy'):visible"

    SUCCESS_POPUP_CLOSE_BUTTON = "button.MuiIconButton-root"

    CURRENT_VERSION_ID_INPUT = "input.MuiSelect-nativeInput"

    # Draft mode helpers
    CREATE_DRAFT_BUTTON = "button:has-text('Create draft'):visible"
    DRAFT_ENTRY_BUTTON = (
        "button:has-text('Edit Draft'), "
        "button:has-text('Switch to Draft'), "
        "[role='button']:has-text('Edit Draft'), "
        "[role='button']:has-text('Switch to Draft')"
    )

    # =========================
    # NAVIGATION
    # =========================

    def open(self, url):
        self.navigate(url)

    def click_create_draft(self):
        create_draft = self.page.get_by_role(
            "button",
            name="Create draft",
            exact=True,
        ).last

        create_draft.wait_for(
            state="visible",
            timeout=30000,
        )

        create_draft.click()

        self.page.wait_for_timeout(1000)

        second_create_draft = self.page.get_by_role(
            "button",
            name="Create draft",
            exact=True,
        ).last

        if second_create_draft.count() > 0:
            try:
                second_create_draft.wait_for(
                    state="visible",
                    timeout=3000,
                )
                second_create_draft.click()
            except Exception:
                pass

    def ensure_draft_mode(self, url):
        """
        Ensure Guardrails page is in draft/edit mode.
        """
        publish_changes = self.page.locator(
            self.PUBLISH_CHANGES_BUTTON
        ).first
        if publish_changes.is_visible():
            return

        create_draft = self.page.locator(
            self.CREATE_DRAFT_BUTTON
        ).first
        if create_draft.is_visible():
            print("Create draft button found")

            self.click_create_draft()

            print("Reopening Guardrails page after creating draft")
            self.open(url)

            self.page.wait_for_timeout(3000)

            return

        draft_entry = self.page.locator(
            self.DRAFT_ENTRY_BUTTON
        ).first
        if draft_entry.is_visible():
            self.click_create_draft()
            self.page.locator(
                self.PUBLISH_CHANGES_BUTTON
            ).first.wait_for(
                state="visible",
                timeout=30000,
            )
            return

        # Fallback: reload target guardrails URL once and continue.
        self.navigate(url)

    # =========================
    # ACTIONS - EMAIL PATTERNS
    # =========================

    def open_email_section(self):
        email_tab = self.page.locator(self.EMAIL_TAB).first

        if email_tab.count() > 0:
            email_tab.click()

    def add_email_pattern(self, pattern):
        self.open_email_section()

        email_input = self.page.locator(self.EMAIL_INPUT).first
        email_input.wait_for(state="visible", timeout=30000)
        email_input.scroll_into_view_if_needed()
        email_input.fill(pattern)

        add_button = self.page.locator(self.ADD_PATTERN_BUTTON).first

        if add_button.count() > 0:
            add_button.click()
        else:
            email_input.press("Enter")

    # =========================
    # ACTIONS - SAVE FLOW
    # =========================

    def click_save(self):
        self.click(self.SAVE_BUTTON)

    def click_confirm_save(self):
        confirm_save = self.page.locator(
            self.CONFIRM_SAVE_BUTTON
        ).last

        confirm_save.wait_for(
            state="visible",
            timeout=30000,
        )

        confirm_save.click()

    # =========================
    # ACTIONS - DEPLOY FLOW
    # =========================

    def click_deploy(self):
        self.click(self.DEPLOY_BUTTON)

    def click_publish_changes(self):
        self.click(self.PUBLISH_CHANGES_BUTTON)

    def click_deploy_changes(self):
        self.click(self.DEPLOY_CHANGES_BUTTON)

    def click_final_deploy(self):
        deploy_button = self.page.get_by_role(
            "button",
            name="Deploy",
            exact=True,
        )

        deploy_button.wait_for(
            state="visible",
            timeout=30000,
        )

        deploy_button.click()

    def close_success_popup(self):
        self.click(self.SUCCESS_POPUP_CLOSE_BUTTON)

    # =========================
    # GETTERS
    # =========================

    def get_current_version_id(self):
        return self.page.locator(
            self.CURRENT_VERSION_ID_INPUT
        ).input_value()
