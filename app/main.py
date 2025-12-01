"""
SmartDoc AI - Main FastAPI Application
Legal Document Analysis Platform for South African Businesses
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import sys
from datetime import datetime

from app.api.routes import router
from app.core.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)
settings = get_settings()


# ==================== LIFESPAN EVENTS ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events - startup and shutdown
    """
    # STARTUP
    logger.info("=" * 60)
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"OpenAI API Key configured: {bool(settings.OPENAI_API_KEY)}")
    logger.info(f"Supabase configured: {bool(settings.SUPABASE_URL)}")
    logger.info("=" * 60)
    
    yield
    
    # SHUTDOWN
    logger.info("=" * 60)
    logger.info(f"🛑 Shutting down {settings.APP_NAME}")
    logger.info("=" * 60)


# ==================== CREATE APP ====================

app = FastAPI(
    title=settings.APP_NAME,
    description="""
    # SmartDoc AI - Legal Document Analysis Platform
    
    AI-powered document analysis platform specifically designed for South African businesses.
    
    ## Features
    
    ### 📄 Text Analysis
    - Word count, sentence count, character count
    - Readability scoring (Flesch Reading Ease)
    - Sentiment analysis
    - Keyword extraction
    
    ### ⚖️ Legal Document Analysis
    - Document type identification (Employment, Lease, NDA, etc.)
    - Party extraction (companies with Pty Ltd, CC, etc.)
    - Date extraction
    - Monetary amount extraction (Rands)
    - Clause identification (confidentiality, termination, payment, etc.)
    - Risk assessment scoring
    
    ### 💬 Feedback Analysis
    - Sentiment detection
    - Key points extraction
    - Readability metrics
    
    ### 🔄 Batch Processing
    - Process multiple documents at once
    - Up to 10 documents per batch
    
    ### 📊 Document Comparison
    - Compare two documents for similarity
    - Identify key differences
    - Find common elements
    
    ## South African Context
    
    This platform is specifically designed for the South African market:
    - Currency: Rands (R, ZAR)
    - Company formats: Pty Ltd, CC, NPC, SOC Ltd
    - Legal frameworks: Labour Relations Act, CCMA, Rental Housing Act
    - Locations: Johannesburg, Sandton, Gauteng, Pretoria
    
    ## Technology Stack
    
    - **Backend**: Python 3.10+, FastAPI
    - **AI/NLP**: OpenAI API, NLTK, TextBlob
    - **Document Processing**: python-docx, PyPDF2, pdfplumber
    - **Database**: Supabase (PostgreSQL)
    
    ## Getting Started
    
    1. Try the `/health` endpoint to verify API is running
    2. Use `/analyze/text` for simple text analysis
    3. Use `/analyze/legal` for legal document analysis
    4. Check the interactive documentation at `/docs`
    
    ## Support
    
    For issues or questions, contact: support@smartdocai.com
    """,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)


# ==================== MIDDLEWARE ====================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all incoming requests
    """
    start_time = datetime.now()
    
    # Log request
    logger.info(f"→ {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = (datetime.now() - start_time).total_seconds()
    
    # Log response
    logger.info(f"← {request.method} {request.url.path} - {response.status_code} ({duration:.2f}s)")
    
    return response


# ==================== EXCEPTION HANDLERS ====================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(f"Validation error on {request.url.path}: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Validation error",
            "details": errors,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle general exceptions
    """
    logger.error(f"Unhandled exception on {request.url.path}: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "timestamp": datetime.now().isoformat()
        }
    )


# ==================== ROUTES ====================

# Include API routes
app.include_router(router, prefix="/api/v1")


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "AI-powered legal document analysis for South African businesses",
        "documentation": "/docs",
        "health_check": "/api/v1/health",
        "status": "operational",
        "environment": settings.ENVIRONMENT
    }


# ==================== STARTUP MESSAGE ====================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting server directly (for development only)")
    logger.info("For production, use: uvicorn app.main:app --host 0.0.0.0 --port 8000")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )