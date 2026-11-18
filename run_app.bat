@echo off
setlocal
title AI-Powered Phishing Detection System
echo ============================================================
echo Starting AI Phishing Detection Web Application...
echo ============================================================
cd /d "%~dp0"

set "PYTHON=python"
python -c "import sys; raise SystemExit(0 if sys.version_info[:2] in ((3, 11), (3, 12)) else 1)" >nul 2>nul
if errorlevel 1 (
	where py >nul 2>nul
	if errorlevel 1 goto python_missing
	set "PYTHON=py -3.12"
	%PYTHON% -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 12) else 1)" >nul 2>nul
	if errorlevel 1 (
		set "PYTHON=py -3.11"
		%PYTHON% -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 11) else 1)" >nul 2>nul
		if errorlevel 1 goto python_missing
	)
)

if not exist "models\best_model.joblib" (
	echo ERROR: models\best_model.joblib was not found.
	echo Restore the model files in the models folder before starting the app.
	goto failed
)
if not exist "models\vectorizer.joblib" (
	echo ERROR: models\vectorizer.joblib was not found.
	echo Restore the model files in the models folder before starting the app.
	goto failed
)

if not exist ".venv\Scripts\python.exe" (
	echo Creating a local Python environment...
	%PYTHON% -m venv .venv
	if errorlevel 1 goto setup_failed
)

".venv\Scripts\python.exe" -c "import sys; raise SystemExit(0 if sys.version_info[:2] in ((3, 11), (3, 12)) else 1)" >nul 2>nul
if errorlevel 1 (
	echo ERROR: The existing .venv does not use Python 3.11 or 3.12.
	echo Remove the .venv folder and run this script again.
	goto failed
)

".venv\Scripts\python.exe" -c "import joblib, numpy, pandas, plotly, sklearn, starlette, streamlit, uvicorn; raise SystemExit(0 if sklearn.__version__ == '1.9.0' else 1)" >nul 2>nul
if errorlevel 1 (
	echo Installing required packages. This may take a few minutes on first run...
	".venv\Scripts\python.exe" -m pip install -r requirements.txt
	if errorlevel 1 goto setup_failed
)

echo Opening SentinelMail AI Web Application at http://127.0.0.1:8000
echo   Landing Page : http://127.0.0.1:8000/
echo   SOC App      : http://127.0.0.1:8000/app
start "" http://127.0.0.1:8000
".venv\Scripts\python.exe" web_app.py
if errorlevel 1 goto launch_failed
goto end

:python_missing
echo ERROR: Python 3.11 or 3.12 was not found. Install a supported version and try again.
goto failed

:setup_failed
echo.
echo ERROR: Setup failed. Check your internet connection and Python installation, then try again.
goto failed

:launch_failed
echo.
echo ERROR: The web app stopped unexpectedly.
goto failed

:failed
pause
exit /b 1

:end
endlocal
