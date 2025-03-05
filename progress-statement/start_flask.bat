@echo off
cd /d %~dp0
call D:\src\python-tools-of-the-trade\.venv\Scripts\activate.bat
python serve_orderclerk_trades.py
