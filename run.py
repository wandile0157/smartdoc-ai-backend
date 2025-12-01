"""
Development server runner
Run this file to start the FastAPI server
"""

import uvicorn
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("🚀 Starting SmartDoc AI Development Server")
    logger.info("📍 API Documentation: http://localhost:8000/docs")
    logger.info("📍 ReDoc Documentation: http://localhost:8000/redoc")
    logger.info("📍 Health Check: http://localhost:8000/api/v1/health")
    logger.info("")
    logger.info("Press CTRL+C to stop the server")
    logger.info("=" * 60)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )