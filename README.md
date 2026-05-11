# Notch Guardrails Automation

## Project Overview

This project automates Guardrails and Playground validation for QA scenarios in a Notch environment.  
It uses **Playwright + Pytest** to configure Guardrails policies (for example, email pattern rules), deploy a draft version, and validate runtime behavior in Playground (blocked vs allowed outcomes).

The goal is to provide reliable, repeatable coverage for policy behavior without manual UI regression checks.

## Architecture / Project Structure

```text
notch-guardrails-automation/
├─ config/
│  ├─ environments.json
│  └─ settings.py
├─ data/
│  ├─ guardrails_patterns.json
│  └─ prompts.json
├─ flows/
│  └─ guardrails_flow.py
├─ pages/
│  ├─ base_page.py
│  ├─ guardrails_page.py
│  └─ playground_page.py
├─ tests/
│  └─ test_guardrails.py
├─ screenshots/
├─ conftest.py
├─ pyproject.toml
├─ requirements.txt
└─ README.md
```

Design separation:
- **Pages**: UI locators and low-level interactions (Page Object Model)
- **Flows**: business-level automation steps across pages
- **Tests**: scenario orchestration, assertions, and retry behavior

## Main Automation Flow

1. Open the **Guardrails** page for the target environment.
2. Ensure draft mode is available (create/switch to draft if needed).
3. Add the configured **email input pattern**.
4. Execute save and deployment sequence:
   - Save
   - Confirm Save
   - Deploy
   - Publish Changes
   - Deploy Changes
   - Final Deploy
5. Extract deployed `version_id`.
6. Open **Playground** with the deployed version.
7. Send customer message payload (email + content).
8. Validate expected behavior:
   - **Blocked**: `Policy Failed` is shown
   - **Allowed**: no policy failure indication appears

## Technologies Used

- Python
- Playwright (sync API)
- Pytest
- JSON test/config data
- GitHub (source control and collaboration)

## Test Scenarios

Current scenario patterns include:
- **Blocked email pattern**: verify policy failure is triggered for disallowed input.
- **Allowed flow**: verify valid input continues without policy failure.
- **Regression / retry logic**: scenario-level retries reduce flakiness and provide clearer final failure reporting.

## API Flow Understanding

The assignment identified the following key backend calls in the Guardrails lifecycle:

- `POST /dashboard/tree/draft`
- `PUT /dashboard/settings/customization`
- `PUT /dashboard/tree/active/<VERSION>`
- `GET /dashboard/settings?version=<VERSION>`
- `POST /dashboard/webui`

Together, these represent draft creation, policy customization, active version promotion, version retrieval, and Playground execution.

## Running the Project

Install dependencies first, then run:

```bash
python -m pytest tests/test_guardrails.py --env=qa -v -s
```

## Notes

- Dynamic draft handling is built into the flow (create/switch draft when required).
- Retry mechanism exists at scenario level for stability in UI-based execution.
- Clear separation between **Pages / Flows / Tests** improves maintainability and debugging.
