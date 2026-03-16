"""Run the Synzept FastAPI backend.

This script ensures the backend package is importable even if the current working
directory changes (e.g., when uvicorn spawns a reloader process).
"""

import sys
from pathlib import Path

# Ensure backend package is on the path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from main import app

if __name__ == "__main__":
    import os
    import uvicorn

    # Allow enabling reload via environment (useful for local dev)
    reload = os.getenv("UVICORN_RELOAD", "false").lower() in ("1", "true", "yes")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=reload,
    )
