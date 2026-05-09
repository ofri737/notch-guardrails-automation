import json

import pytest
from playwright.sync_api import sync_playwright

from config import settings


# =========================
# PYTEST OPTIONS
# =========================
def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default="qa",
        help="Target environment: qa, staging, or prod",
    )


# =========================
# ENVIRONMENT METADATA
# =========================
@pytest.fixture(scope="session")
def env_config(request):
    env_name = request.config.getoption("--env")

    env_file = settings.BASE_DIR / "config" / "environments.json"

    if not env_file.exists():
        pytest.fail(f"Environment metadata file not found: {env_file}")

    with open(env_file, "r", encoding="utf-8-sig") as f:
        environments = json.load(f)

    if env_name not in environments:
        available_envs = ", ".join(environments.keys())
        pytest.fail(
            f"Environment '{env_name}' not found. "
            f"Available environments: {available_envs}"
        )

    return environments[env_name]


# =========================
# ARTIFACT DIRECTORIES
# =========================
@pytest.fixture(scope="session", autouse=True)
def create_artifact_dirs():
    settings.REPORTS_DIR.mkdir(exist_ok=True)
    settings.SCREENSHOTS_DIR.mkdir(exist_ok=True)
    settings.TRACES_DIR.mkdir(exist_ok=True)

    if settings.VIDEO_ENABLED:
        settings.VIDEOS_DIR.mkdir(parents=True, exist_ok=True)


# =========================
# PLAYWRIGHT INSTANCE
# =========================
@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as playwright:
        yield playwright


# =========================
# BROWSER CONTEXT
# =========================
@pytest.fixture(scope="session")
def browser_context(playwright_instance):
    settings.USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

    browser_args = [
        "--start-maximized",
        "--disable-notifications",
        "--disable-extensions",
        "--disable-dev-shm-usage",
        "--disable-blink-features=AutomationControlled",
    ]

    launch_options = {
        "user_data_dir": str(settings.USER_DATA_DIR),
        "headless": settings.HEADLESS,
        "slow_mo": settings.SLOW_MO,
        "args": browser_args,
        "viewport": settings.VIEWPORT,
        "ignore_https_errors": True,
    }

    if settings.BROWSER_CHANNEL:
        launch_options["channel"] = settings.BROWSER_CHANNEL

    if settings.CHROME_PATH:
        launch_options["executable_path"] = settings.CHROME_PATH

    if settings.IGNORE_DEFAULT_ENABLE_AUTOMATION:
        launch_options["ignore_default_args"] = ["--enable-automation"]

    if settings.VIDEO_ENABLED:
        launch_options["record_video_dir"] = str(settings.VIDEOS_DIR)

    context = playwright_instance.chromium.launch_persistent_context(
        **launch_options
    )

    if settings.TRACE_ENABLED:
        context.tracing.start(
            screenshots=True,
            snapshots=True,
            sources=True,
        )

    def apply_page_defaults(page):
        page.set_default_timeout(settings.DEFAULT_TIMEOUT)
        page.set_default_navigation_timeout(settings.NAVIGATION_TIMEOUT)

    context.on("page", apply_page_defaults)

    for existing_page in context.pages:
        apply_page_defaults(existing_page)

    yield context

    if settings.TRACE_ENABLED:
        trace_path = settings.TRACES_DIR / "trace.zip"
        context.tracing.stop(path=str(trace_path))
        print(f"Trace saved: {trace_path}")

    context.close()


# =========================
# MANUAL GOOGLE AUTH CHECKPOINT
# =========================
@pytest.fixture(scope="session", autouse=True)
def ensure_manual_google_auth(browser_context, env_config):
    if not settings.MANUAL_GOOGLE_AUTH_ENABLED:
        return

    page = browser_context.new_page()
    target_app_url = env_config["guardrails_url"]

    print(
        "Manual Google authentication enabled. "
        "Automation will not enter Google credentials."
    )
    print(f"Opening app URL: {target_app_url}")
    page.goto(target_app_url)

    current_url = page.url.lower()
    requires_manual_login = (
        "accounts.google.com" in current_url
        or "/login" in current_url
        or "signin" in current_url
    )

    if requires_manual_login:
        print(
            "Authentication required. Complete Google login manually in the "
            "existing headed Chrome window."
        )

        google_blocked = page.locator("text=This browser or app may not be secure").is_visible()
        if google_blocked:
            raise AssertionError(
                "Google blocked login in automated browser context "
                "('This browser or app may not be secure'). "
                "Close the running test, then bootstrap login manually in the same "
                "profile folder and rerun tests. "
                f"Profile path: {settings.USER_DATA_DIR}"
            )

        if settings.MANUAL_GOOGLE_AUTH_WAIT_FOR_ENTER:
            try:
                print(
                    "AUTH CHECKPOINT: login is complete? Press Enter in this terminal "
                    "to continue test execution."
                )
                input(
                    "After login is complete and app is loaded, "
                    "press Enter to continue tests..."
                )
            except EOFError:
                pass
        elif settings.MANUAL_GOOGLE_AUTH_USE_PAGE_PAUSE:
            print(
                "AUTH CHECKPOINT: Playwright is pausing now. "
                "To continue, switch to Playwright Inspector and click Resume "
                "(or press F8)."
            )
            page.pause()

    try:
        page.wait_for_url("**/guardrails**", timeout=settings.MANUAL_GOOGLE_AUTH_TIMEOUT_MS)
    except Exception as exc:
        raise AssertionError(
            "Manual Google login checkpoint did not reach Guardrails page. "
            "Please complete login and ensure Guardrails is loaded before continuing."
        ) from exc
    finally:
        page.close()


# =========================
# PAGE FIXTURE
# =========================
@pytest.fixture()
def page(browser_context):
    page = browser_context.new_page()

    page.set_default_timeout(settings.DEFAULT_TIMEOUT)
    page.set_default_navigation_timeout(settings.NAVIGATION_TIMEOUT)

    yield page

    page.close()


# =========================
# FAILURE HANDLING
# =========================
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")

        if page and settings.SCREENSHOT_ON_FAILURE:
            settings.SCREENSHOTS_DIR.mkdir(exist_ok=True)
            screenshot_path = settings.SCREENSHOTS_DIR / f"{item.name}.png"

            page.screenshot(path=str(screenshot_path), full_page=True)

            print(f"Screenshot saved: {screenshot_path}")
