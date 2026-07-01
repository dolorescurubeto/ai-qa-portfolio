"""E2E Playwright tests — UI chat + Python factual validation."""

import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CHAT_DIR = ROOT / "week14-e2e-chat"
CHAT_URL = "http://127.0.0.1:5051"

sys.path.insert(0, str(ROOT / "week03-metrics"))
from factual import validate_factual  # noqa: E402

REFERENCE_CHECKING = "Your checking account balance is $1,847.32."


@pytest.fixture(scope="module")
def chat_server():
    """Start Flask chat mock for browser tests."""
    proc = subprocess.Popen(
        [sys.executable, str(CHAT_DIR / "chat_app.py")],
        cwd=str(CHAT_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    deadline = time.time() + 15
    while time.time() < deadline:
        try:
            import urllib.request

            with urllib.request.urlopen(f"{CHAT_URL}/health", timeout=1):
                break
        except OSError:
            time.sleep(0.3)
    else:
        proc.kill()
        pytest.fail("Chat server did not start on port 5051")

    yield CHAT_URL
    proc.terminate()
    proc.wait(timeout=5)


@pytest.mark.e2e
def test_chat_checking_balance_ui_and_factual_pass(chat_server, page):
    page.goto(chat_server)
    page.get_by_test_id("chat-input").fill("What is my checking account balance?")
    page.get_by_test_id("send-btn").click()
    bot = page.get_by_test_id("bot-message").last
    bot.wait_for(state="visible", timeout=5000)
    text = bot.inner_text()

    result = validate_factual(REFERENCE_CHECKING, text)
    assert result["pass"], f"UI response failed factual check: {text}"


@pytest.mark.e2e
def test_chat_wrong_amount_factual_fail(chat_server, page):
    page.goto(chat_server)
    page.get_by_test_id("chat-input").fill("Show incorrect checking balance please")
    page.get_by_test_id("send-btn").click()
    bot = page.get_by_test_id("bot-message").last
    bot.wait_for(state="visible", timeout=5000)
    text = bot.inner_text()

    result = validate_factual(REFERENCE_CHECKING, text)
    assert not result["pass"]
    assert "$1,800.32" in text


@pytest.mark.e2e
def test_chat_page_loads(chat_server, page):
    page.goto(chat_server)
    assert page.get_by_test_id("send-btn").is_visible()
    assert page.get_by_test_id("chat-input").is_visible()


def _api_ask(chat_server: str, query: str) -> str:
    import json
    import urllib.request

    payload = json.dumps({"query": query}).encode("utf-8")
    req = urllib.request.Request(
        f"{chat_server}/api/ask",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read().decode("utf-8"))["response"]


@pytest.mark.integration
def test_api_checking_balance_factual_pass(chat_server):
    """API-level E2E (no browser) — same validation pipeline."""
    text = _api_ask(chat_server, "checking balance please")
    assert validate_factual(REFERENCE_CHECKING, text)["pass"]


@pytest.mark.integration
def test_api_wrong_balance_factual_fail(chat_server):
    text = _api_ask(chat_server, "incorrect checking balance")
    assert not validate_factual(REFERENCE_CHECKING, text)["pass"]
