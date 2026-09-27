#!/usr/bin/env python3
"""
FraudFlow Intelligence - Entry Point Runner
Launches the FastAPI application on 127.0.0.1:8001
"""
import sys
import uvicorn

if __name__ == "__main__":
    print("=" * 65)
    print("Starting FraudFlow Intelligence - Money-Flow & Cash-Out Intelligence")
    print("SIH Problem Statement SIH26184")
    print("Serving on http://127.0.0.1:8001")
    print("=" * 65)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8001, reload=True)
