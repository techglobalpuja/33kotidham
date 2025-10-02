#!/usr/bin/env python3
"""
Development server runner for 33 Koti Dham API
"""

import uvicorn
from app.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )
