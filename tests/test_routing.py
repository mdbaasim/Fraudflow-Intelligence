import sys
sys.path.insert(0, ".")
import asyncio
from app.main import VercelPathRewriteMiddleware

async def test_path_normalization():
    test_cases = [
        ("/api/cases", []),
        ("/cases", []),
        ("/api/index.py", [(b"x-forwarded-uri", b"/api/cases")]),
        ("/api/index.py", [(b"x-matched-path", b"/api/cases")]),
        ("/cases/CASE-DIN-2026-001/analyze", []),
        ("/api/cases/CASE-DIN-2026-001/analyze", []),
        ("/", []),
        ("/styles.css", []),
        ("/app.js", []),
    ]

    for p, h in test_cases:
        scope = {"type": "http", "path": p, "raw_path": p.encode(), "headers": h}
        async def dummy(s, r, snd): pass
        mw = VercelPathRewriteMiddleware(dummy)
        await mw(scope, None, None)
        print(f"{p:<38} -> {scope['path']}")

if __name__ == "__main__":
    asyncio.run(test_path_normalization())
