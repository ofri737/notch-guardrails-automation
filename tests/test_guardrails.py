import json
from pathlib import Path

from config import settings

from flows.guardrails_flow import (
    deploy_email_guardrail,
    validate_guardrails_in_playground,
)


# ================================================================================
# LOAD JSON FILE
# ================================================================================

def load_json(file_path):
    with open(file_path, "r", encoding="utf-8-sig") as file:
        return json.load(file)


# ================================================================================
# TEST - EMAIL GUARDRAIL
# ================================================================================

def test_email_guardrail_blocks_response(
    page,
    env_config,
):
    # =========================
    # LOAD TEST DATA
    # =========================

    patterns_data = load_json(
        Path("data/guardrails_patterns.json")
    )

    prompts_data = load_json(
        Path("data/prompts.json")
    )

    email_pattern = (
        patterns_data["email_guardrail"]["input_pattern"]
    )

    scenario_name = (
        prompts_data["email_guardrail"]["scenario"]
    )

    test_cases = (
        prompts_data["email_guardrail"]["test_cases"]
    )

    # =========================
    # DEPLOY PATTERN ONCE
    # =========================

    version_id = deploy_email_guardrail(
        page=page,
        guardrails_url=env_config[
            "guardrails_url"
        ],
        email_pattern=email_pattern,
    )

    # =========================
    # FULL SCENARIO ATTEMPTS
    # =========================

    final_failures = []

    for attempt in range(
        1,
        settings.MAX_SCENARIO_ATTEMPTS + 1,
    ):

        print("=" * 80)
        print(
            f"STARTING SCENARIO ATTEMPT "
            f"{attempt}/"
            f"{settings.MAX_SCENARIO_ATTEMPTS}"
        )
        print("=" * 80)

        attempt_failures = []

        # =========================
        # RUN ALL PROMPTS
        # =========================

        for test_case in test_cases:

            case_label = test_case.get(
                "test_case",
                "unnamed",
            )

            customer_email = (
                test_case["customer_email"]
            )

            customer_message = (
                test_case["customer_message"]
            )

            expected_behavior = (
                test_case["expected_behavior"]
            )

            try:

                validate_guardrails_in_playground(
                    page=page,
                    playground_base_url=env_config[
                        "playground_base_url"
                    ],
                    version_id=version_id,
                    customer_email=customer_email,
                    customer_message=customer_message,
                    expected_behavior=expected_behavior,
                )

                print(
                    f"PASSED: [{case_label}] "
                    f"expected={expected_behavior}"
                )

            except Exception as exc:

                failure_detail = (
                    f"SCENARIO={scenario_name!r} | "
                    f"TEST_CASE={case_label!r} | "
                    f"EMAIL={customer_email!r} | "
                    f"EXPECTED={expected_behavior!r} | "
                    f"ERROR={str(exc)!r}"
                )

                print(f"FAILED: {failure_detail}")

                attempt_failures.append(
                    failure_detail
                )

        # =========================
        # ATTEMPT RESULT
        # =========================

        if not attempt_failures:

            print("=" * 80)
            print(
                f"SCENARIO PASSED "
                f"ON ATTEMPT {attempt}"
            )
            print("=" * 80)

            final_failures = []
            break

        print("=" * 80)
        print(
            f"SCENARIO FAILED "
            f"ON ATTEMPT {attempt}"
        )
        print("=" * 80)

        final_failures = attempt_failures

    # =========================
    # FINAL SUMMARY
    # =========================

    total_cases = len(test_cases)
    failed_cases = len(final_failures)
    passed_cases = total_cases - failed_cases

    print("=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)

    print(f"Scenario: {scenario_name}")
    print(f"Total cases: {total_cases}")
    print(f"Passed cases: {passed_cases}")
    print(f"Failed cases: {failed_cases}")

    assert not final_failures, (
        "One or more prompts failed:\n"
        + "\n".join(final_failures)
    )