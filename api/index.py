"""
Vercel Serverless Entrypoint Adapter
Exposes the Starlette ASGI application for Vercel Python Runtime.
"""

import os
import sys

# Add project root directory to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from web_app import app
