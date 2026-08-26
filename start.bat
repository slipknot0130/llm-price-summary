@echo off
chcp 65001 >nul
cd /d "%~dp0"
python main.py || py main.py
if exist "llm-price.html" start "" "llm-price.html"
pause
