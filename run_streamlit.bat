@echo off
setlocal
title AI-Powered Phishing Detection System (Streamlit SOC)
cd /d "%~dp0"
echo Opening the Streamlit SOC Dashboard at http://localhost:8501
".venv\Scripts\python.exe" -m streamlit run app.py
endlocal
