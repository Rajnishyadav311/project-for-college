@echo off
title MediPredict AI Server
echo ===================================================
echo Starting MediPredict AI Healthcare Web Application
echo ===================================================
cd /d "%~dp0"
set PYTHON="..\python311\python.exe"

echo Checking Django configuration and database...
%PYTHON% manage.py check

echo.
echo Launching development server on http://127.0.0.1:8000 ...
echo Press Ctrl+C to stop the server.
echo.
%PYTHON% manage.py runserver 127.0.0.1:8000
pause
