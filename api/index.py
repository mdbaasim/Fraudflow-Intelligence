import os
import sys
from pathlib import Path

# Add project root to sys.path so 'app' module can be found
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.main import app as fastapi_app

class VercelForwardedPathMiddleware:
    """
    ASGI middleware ensuring Vercel serverless request rewrites
    restore the original requested API path (/api/cases, /api/demo/seed, etc.)
    from any of Vercel's edge proxy headers.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            
            # Check all possible headers set by Vercel's edge routing
            forwarded = (
                headers.get(b"x-forwarded-uri") or 
                headers.get(b"x-matched-path") or
                headers.get(b"x-vercel-matched-path") or
                headers.get(b"x-rewrite-url") or
                headers.get(b"x-original-url")
            )
            
            if forwarded:
                target_path = forwarded.decode("utf-8", errors="ignore").split("?")[0]
                scope["path"] = target_path
            elif scope.get("path", "") in ("/api/index.py", "/api/index.py/", "/api", "/api/"):
                scope["path"] = "/api/cases"
            elif scope.get("path", "").startswith("/api/index.py/"):
                scope["path"] = scope["path"][len("/api/index.py"):]

        await self.app(scope, receive, send)

app = VercelForwardedPathMiddleware(fastapi_app)
