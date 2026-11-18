@echo off
title Run Pytest Automated Tests
echo ============================================================
echo Running Automated Unit Tests for Phishing Detection System...
echo ============================================================
cd /d "%~dp0"
python -m pytest tests -v
pause
