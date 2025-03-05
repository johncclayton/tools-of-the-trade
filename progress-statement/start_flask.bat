@echo off
cd /d %~dp0
call D:\src\python-tools-of-the-trade\.venv\Scripts\activate.bat
set FLASK_RUN_HOST=127.0.0.1
set FLASK_RUN_PORT=5050
python serve_orderclerk_trades.py
