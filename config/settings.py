#--------------------------------
# FRAMEWORK CONFIGURATION
#--------------------------------

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Browser Configurations
BROWSER = "chromium"
BROWSER_CHANNEL = "chrome"
HEADLESS = False
SLOW_MO = 2000
IGNORE_DEFAULT_ENABLE_AUTOMATION = True

# Viewport
VIEWPORT = {
    "width": 1920,
    "height": 1080,
}

# Timeouts
DEFAULT_TIMEOUT = 30000
NAVIGATION_TIMEOUT = 60000

# Artifacts
SCREENSHOTS_DIR = BASE_DIR / "screenshots"
TRACES_DIR = BASE_DIR / "traces"
REPORTS_DIR = BASE_DIR / "reports"
VIDEOS_DIR = REPORTS_DIR / "videos"

# Auth
AUTH_STATE = BASE_DIR / "auth.json"
USER_DATA_DIR = BASE_DIR / ".user-data" / "chrome-profile"

MANUAL_GOOGLE_AUTH_ENABLED = True
MANUAL_GOOGLE_AUTH_WAIT_FOR_ENTER = False
MANUAL_GOOGLE_AUTH_USE_PAGE_PAUSE = True
MANUAL_GOOGLE_AUTH_TIMEOUT_MS = 300000

# Optional Chrome executable
CHROME_PATH = (
    r"C:\Program Files\Google\Chrome\Application\chrome.exe"
)

# Failure Handling
SCREENSHOT_ON_FAILURE = True

# Traces / Video
TRACE_ENABLED = True
VIDEO_ENABLED = False

# Test Execution
MAX_SCENARIO_ATTEMPTS = 5
