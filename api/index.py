"""
Vercel Serverless Entrypoint Adapter
Wraps web_app ASGI application with fallback error handling for Vercel Serverless.
"""

import os
import sys

# Add project root directory to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from web_app import app
except Exception as e:
    import traceback
    err_msg = traceback.format_exc()
    print("FATAL ERROR IMPORTING WEB_APP:", err_msg)
    from starlette.applications import Starlette
    from starlette.responses import PlainTextResponse
    from starlette.routing import Route

    async def fallback_error(request):
        return PlainTextResponse(f"Startup Exception in Vercel Lambda:\n\n{err_msg}", status_code=500)

    app = Starlette(routes=[Route("/{path:path}", fallback_error)])

