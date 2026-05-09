from pages.guardrails_page import GuardrailsPage
from pages.playground_page import PlaygroundPage


# ================================================================================
# DEPLOY EMAIL GUARDRAIL
# ================================================================================

def deploy_email_guardrail(
    page,
    guardrails_url,
    email_pattern,
):
    """
    Deploy the email guardrail pattern once
    and return the deployed version id.
    """

    print("Starting email guardrail deployment")

    guardrails_page = GuardrailsPage(page)

    print("Opening Guardrails page")
    guardrails_page.open(guardrails_url)

    print("Ensuring Guardrails page is in draft mode")
    guardrails_page.ensure_draft_mode(
        guardrails_url
    )

    print(
        f"Adding email pattern: "
        f"{email_pattern}"
    )

    guardrails_page.add_email_pattern(
        email_pattern
    )

    print("Clicking Save")
    guardrails_page.click_save()

    print("Confirming Save")
    guardrails_page.click_confirm_save()

    print("Clicking Deploy")
    guardrails_page.click_deploy()

    print("Clicking Publish Changes")
    guardrails_page.click_publish_changes()

    print("Clicking Deploy Changes")
    guardrails_page.click_deploy_changes()

    print("Clicking final Deploy")
    guardrails_page.click_final_deploy()

    print("Deployment completed")

    version_id = (
        guardrails_page.get_current_version_id()
    )

    print(
        f"Extracted version_id={version_id}"
    )

    return version_id


# ================================================================================
# CONTEXT MESSAGE
# ================================================================================

def _guardrails_context_message(
    customer_email,
    customer_message,
    expected_behavior,
    version_id,
):
    return (
        f"customer_email={customer_email!r}, "
        f"customer_message={customer_message!r}, "
        f"expected_behavior={expected_behavior!r}, "
        f"version_id={version_id!r}"
    )


# ================================================================================
# VALIDATE GUARDRAILS IN PLAYGROUND
# ================================================================================

def validate_guardrails_in_playground(
    page,
    playground_base_url,
    version_id,
    customer_email,
    customer_message,
    expected_behavior,
):
    """
    Validate a single prompt case
    inside Playground.
    """

    playground_page = PlaygroundPage(page)

    print(
        f"Opening Playground "
        f"with version_id={version_id}"
    )

    playground_page.open(
        playground_base_url,
        version_id,
    )

    print(
        f"Sending customer message "
        f"for email={customer_email}"
    )

    playground_page.send_customer_message(
        email=customer_email,
        content=customer_message,
    )

    print(
        f"Validating expected_behavior="
        f"{expected_behavior}"
    )

    if expected_behavior == "Blocked":

        try:

            playground_page.assert_policy_failed_displayed()

        except Exception as exc:

            raise AssertionError(
                "Expected policy to fail, "
                "but it did not. "
                + _guardrails_context_message(
                    customer_email,
                    customer_message,
                    expected_behavior,
                    version_id,
                )
            ) from exc

    elif expected_behavior == "Allowed":

        playground_page.wait_after_customer_message()

        if playground_page.is_policy_failed_displayed():

            raise AssertionError(
                "Expected policy to allow "
                "the message, but "
                "Policy Failed was displayed. "
                + _guardrails_context_message(
                    customer_email,
                    customer_message,
                    expected_behavior,
                    version_id,
                )
            )

    else:

        raise ValueError(
            f"Unsupported expected_behavior: "
            f"{expected_behavior!r}. "
            "Use 'Blocked' or 'Allowed'."
        )
