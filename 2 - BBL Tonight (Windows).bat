@echo off
REM Builds the Best & Worst tables and the Top 10 image for one night of NBA games.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (echo Run "1 - Setup (Windows)" first. & pause & exit /b 1)
if not "%~1"=="" (
  .venv\Scripts\python -X utf8 bbl\run.py %*
  pause & exit /b
)
echo BBL Best ^& Worst
set "D="
set /p D=Press Enter for the latest night, type a date like 20261020, or type demo for the sample: 
if /i "%D%"=="demo" (
  .venv\Scripts\python -X utf8 bbl\run.py --demo
) else (
  .venv\Scripts\python -X utf8 bbl\run.py %D%
)
pause
