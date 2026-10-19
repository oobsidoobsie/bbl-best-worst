@echo off
REM One-time setup on Windows: private Python environment + the image tool.
cd /d "%~dp0"
echo BBL Best ^& Worst - setup
echo.
set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY where python >nul 2>nul && set "PY=python"
if not defined PY (
  echo Python isn't installed. Get it from https://www.python.org/downloads/windows/
  echo During install, TICK "Add python.exe to PATH". Then run this Setup again.
  pause & exit /b 1
)
%PY% -c "import sys; sys.exit(0 if sys.version_info>=(3,9) else 1)" || (echo Python 3.9 or newer is needed. & pause & exit /b 1)
echo 1/3 Creating the environment...
%PY% -m venv .venv || (echo Couldn't create the environment. & pause & exit /b 1)
echo 2/3 Installing Playwright (draws the Top 10 image)...
.venv\Scripts\python -m pip install --quiet --upgrade pip playwright || (echo Install failed - check your internet. & pause & exit /b 1)
echo 3/3 Downloading the headless browser it uses (about 150 MB, one time)...
.venv\Scripts\python -m playwright install chromium || (echo Browser download failed - run Setup again. & pause & exit /b 1)
echo.
echo Setup done. Next: install the roster bookmark (README step 3), then double-click "2 - BBL Tonight (Windows)".
pause
