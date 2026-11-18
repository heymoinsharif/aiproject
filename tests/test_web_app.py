"""
Test Suite for Web Application Logic, Templates, Static Assets & Handlers
Non-async execution to ensure compatibility across all test runners and sandbox environments.
"""

import json
import os
import web_app

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_DIR = os.path.join(PROJECT_ROOT, "web")


def test_landing_page_serves_gsap_and_animejs_sections():
    index_path = os.path.join(WEB_DIR, "index.html")
    assert os.path.exists(index_path)
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    # GSAP ScrollTrigger story wrap requirement
    assert "scroll-trigger-ready__worm-wrap" in html
    # Pinned scrubbed windmill requirement
    assert 'id="pin-windmill"' in html
    assert 'id="pin-windmill-svg"' in html
    # Parallax data-speed requirements
    assert 'data-speed="0.8"' in html
    assert 'data-speed="2.0"' in html
    assert 'data-speed="1.2"' in html
    # ScrollSmoother & ScrollTrigger references
    assert "ScrollTrigger" in html
    assert "ScrollSmoother" in html
    assert "/static/js/landing.js" in html


def test_soc_app_page_serves_complete_workspace():
    app_path = os.path.join(WEB_DIR, "app.html")
    assert os.path.exists(app_path)
    with open(app_path, "r", encoding="utf-8") as f:
        html = f.read()

    assert 'id="view-analyzer"' in html
    assert 'id="view-benchmarks"' in html
    assert 'id="view-dataset"' in html
    assert 'id="view-history"' in html
    assert 'id="view-about"' in html
    assert "/static/js/soc.js" in html


def test_static_js_includes_gsap_and_animejs_v4_apis():
    js_path = os.path.join(WEB_DIR, "js", "landing.js")
    assert os.path.exists(js_path)
    with open(js_path, "r", encoding="utf-8") as f:
        js = f.read()

    # User-specified GSAP ScrollTrigger configs
    assert "ScrollTrigger" in js
    assert "rotateZ: 900" in js
    # User-specified animejs v4 configs
    assert "composition: 'blend'" in js
    assert "grid: [13, 13]" in js
    assert "createScope" in js
    assert "(orientation: portrait)" in js
    assert "[-50, 50, -50]" in js


def test_api_handlers_and_data_sources():
    eval_data = web_app.get_eval_data()
    assert "models" in eval_data
    assert "metadata" in eval_data
    assert "research_questions" in eval_data

    detector = web_app.get_detector()
    assert detector.is_ready() is True

    # Test analyze email contract
    phish_res = detector.analyze_email(
        subject="CRITICAL: Verify your account within 24 hours",
        body="Your account has been suspended. Click http://192.168.1.105/login to confirm your password immediately.",
        sender="alert@bank-verify-portal.top",
    )
    assert phish_res["verdict_code"] in ("phishing", "suspicious")
    assert phish_res["url_analysis"]["total_urls_found"] >= 1
    assert len(phish_res["observed_indicators"]) >= 1

    legit_res = detector.analyze_email(
        subject="End-Semester Examination Schedule - Winter 2026",
        body="Dear Faculty and Students, the official examination timetable has been published on https://portal.university.edu/schedule.",
        sender="coe@university.edu",
    )
    assert legit_res["classification"] == "Likely Legitimate"
