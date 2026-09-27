#!/usr/bin/env bash
echo "======================================================================"
echo "Starting FraudFlow Intelligence - Money-Flow & Cash-Out Intelligence"
echo "SIH Problem Statement SIH26184"
echo "======================================================================"

python3 -m pip install -r requirements.txt

echo ""
echo "Starting FastAPI application server on http://127.0.0.1:8001 ..."
echo "Open your web browser and navigate to: http://127.0.0.1:8001"
echo ""
python3 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
