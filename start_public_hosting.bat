@echo off
title FraudFlow Intelligence - Public Cloud Hosting
echo ======================================================================
echo Launching FraudFlow Intelligence Server + Cloudflare Global Tunnel
echo ======================================================================
start /B python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
timeout /t 3 /nobreak >nul
echo Starting public Cloudflare tunnel...
cloudflared.exe tunnel --url http://127.0.0.1:8001 --protocol http2 --no-autoupdate
pause
