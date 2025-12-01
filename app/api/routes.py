"""
API Routes - All endpoint definitions with authentication support
Handles HTTP requests and returns responses
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any, Optional
import logging

from app.models.schemas import (
    TextAnalysisRequest, TextAnalysisResponse,
    LegalAnalysisRequest, LegalAnalysisResponse,
    FeedbackAnalysisRequest, FeedbackAnalysisResponse,
    BatchAnalysisRequest, BatchAnalysisResponse,
    DocumentComparisonRequest, DocumentComparisonResponse,
    HealthCheckResponse, ErrorResponse,
    UserStatsResponse, UserStats
)
from app.services.analysis_service import AnalysisService
from app.services.database_service import DatabaseService
from app.core.config import get_settings
from app.core.auth import get_current_user, get_current_user_optional

logger = logging.getLogger(__name__)
settings = get_settings()

# Create router
router = APIRouter()

# Initialize services
analysis_service = AnalysisService()
db_service = DatabaseService()


# ==================== HEALTH CHECK ====================

@router.get(
    "/health",
    response_model=HealthCheckResponse,
    tags=["Health"],
    summary="Health check endpoint"
)
async def health_check():
    """
    Check API health status.
    """
    return HealthCheckResponse(
        status="healthy",
        version=settings.APP_VERSION,
        services={
            "api": "operational",
            "database": "not configured" if not db_service.db_available else "operational",
            "auth": "configured" if settings.SUPABASE_URL else "not configured"
        }
    )


# ==================== TEXT ANALYSIS ====================

@router.post(
    "/analyze/text",
    response_model=TextAnalysisResponse,
    tags=["Analysis"],
    summary="Analyze text content",
    responses={
        200: {"description": "Successful text analysis"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def analyze_text(
    request: TextAnalysisRequest,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Perform comprehensive text analysis including:
    - Word count, sentence count, character count
    - Readability score (Flesch Reading Ease)
    - Sentiment analysis (polarity and subjectivity)
    - Top keywords extraction
    
    **Authentication:** Optional - Works with or without login
    - Logged in: Analysis saved to history
    - Not logged in: Analysis not saved
    """
    try:
        logger.info(f"Text analysis requested: {len(request.text)} characters, user={'authenticated' if current_user else 'anonymous'}")
        
        # Perform analysis
        result = analysis_service.analyze_text(request.text)
        
        # Save to database if user is authenticated
        if current_user and db_service.db_available:
            try:
                await db_service.save_analysis(
                    user_id=current_user["id"],
                    analysis_type="text",
                    document_type=None,
                    text_preview=request.text[:200],
                    results=result
                )
                logger.info(f"Analysis saved for user {current_user['id']}")
            except Exception as db_error:
                logger.warning(f"Failed to save analysis: {db_error}")
        
        return TextAnalysisResponse(
            success=True,
            message="Text analysis completed successfully",
            **result
        )
    
    except ValueError as e:
        logger.error(f"Validation error in text analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in text analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Text analysis failed"
        )


# ==================== LEGAL ANALYSIS ====================

@router.post(
    "/analyze/legal",
    response_model=LegalAnalysisResponse,
    tags=["Analysis"],
    summary="Analyze legal document",
    responses={
        200: {"description": "Successful legal analysis"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def analyze_legal_document(
    request: LegalAnalysisRequest,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Perform comprehensive legal document analysis including:
    - Document type identification
    - Party extraction (companies, individuals)
    - Date extraction
    - Monetary amount extraction (Rands)
    - Clause identification (confidentiality, termination, etc.)
    - Risk assessment score
    - Complete text statistics
    
    **Authentication:** Optional - Works with or without login
    - Logged in: Analysis saved to history
    - Not logged in: Analysis not saved
    """
    try:
        logger.info(f"Legal analysis requested: {len(request.text)} characters, type={request.document_type}, user={'authenticated' if current_user else 'anonymous'}")
        
        # Perform legal analysis
        result = analysis_service.analyze_legal_document(
            text=request.text,
            document_type=request.document_type
        )
        
        # Save to database if user is authenticated
        if current_user and db_service.db_available:
            try:
                await db_service.save_analysis(
                    user_id=current_user["id"],
                    analysis_type="legal",
                    document_type=request.document_type,
                    text_preview=request.text[:200],
                    results=result
                )
                logger.info(f"Legal analysis saved for user {current_user['id']}")
            except Exception as db_error:
                logger.warning(f"Failed to save analysis: {db_error}")
        
        return LegalAnalysisResponse(
            success=True,
            message="Legal analysis completed successfully",
            **result
        )
    
    except ValueError as e:
        logger.error(f"Validation error in legal analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in legal analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Legal analysis failed"
        )


# ==================== FEEDBACK ANALYSIS ====================

@router.post(
    "/analyze/feedback",
    response_model=FeedbackAnalysisResponse,
    tags=["Analysis"],
    summary="Analyze feedback or reviews",
    responses={
        200: {"description": "Successful feedback analysis"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def analyze_feedback(
    request: FeedbackAnalysisRequest,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Analyze feedback, reviews, or customer comments focusing on:
    - Sentiment analysis (positive, negative, neutral)
    - Key points extraction
    - Readability metrics
    
    **Authentication:** Optional - Works with or without login
    """
    try:
        logger.info(f"Feedback analysis requested: {len(request.text)} characters, user={'authenticated' if current_user else 'anonymous'}")
        
        # Perform feedback analysis
        result = analysis_service.analyze_feedback(request.text)
        
        # Save to database if user is authenticated
        if current_user and db_service.db_available:
            try:
                await db_service.save_analysis(
                    user_id=current_user["id"],
                    analysis_type="feedback",
                    document_type=None,
                    text_preview=request.text[:200],
                    results=result
                )
            except Exception as db_error:
                logger.warning(f"Failed to save analysis: {db_error}")
        
        return FeedbackAnalysisResponse(
            success=True,
            message="Feedback analysis completed successfully",
            **result
        )
    
    except ValueError as e:
        logger.error(f"Validation error in feedback analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in feedback analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Feedback analysis failed"
        )


# ==================== BATCH ANALYSIS ====================

@router.post(
    "/analyze/batch",
    response_model=BatchAnalysisResponse,
    tags=["Analysis"],
    summary="Batch analyze multiple texts",
    responses={
        200: {"description": "Batch analysis completed"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def batch_analyze(
    request: BatchAnalysisRequest,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Analyze multiple texts in a single request.
    Maximum 10 texts per batch.
    
    **Authentication:** Optional
    """
    try:
        logger.info(f"Batch analysis requested: {len(request.texts)} texts, user={'authenticated' if current_user else 'anonymous'}")
        
        # Perform batch analysis
        result = analysis_service.batch_analyze(
            texts=request.texts,
            analysis_type=request.analysis_type.value
        )
        
        return BatchAnalysisResponse(
            success=True,
            message=f"Batch analysis completed: {result['total_processed']} texts processed",
            **result
        )
    
    except ValueError as e:
        logger.error(f"Validation error in batch analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in batch analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Batch analysis failed"
        )


# ==================== DOCUMENT COMPARISON ====================

@router.post(
    "/analyze/compare",
    response_model=DocumentComparisonResponse,
    tags=["Analysis"],
    summary="Compare two documents",
    responses={
        200: {"description": "Document comparison completed"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def compare_documents(
    request: DocumentComparisonRequest,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Compare two documents for similarity and differences.
    
    **Authentication:** Optional
    """
    try:
        logger.info(f"Document comparison requested, user={'authenticated' if current_user else 'anonymous'}")
        
        # Perform comparison
        result = analysis_service.compare_documents(
            doc1=request.document1,
            doc2=request.document2
        )
        
        return DocumentComparisonResponse(
            success=True,
            message="Document comparison completed successfully",
            **result
        )
    
    except ValueError as e:
        logger.error(f"Validation error in document comparison: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in document comparison: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document comparison failed"
        )


# ==================== USER STATISTICS (PROTECTED) ====================

@router.get(
    "/stats",
    response_model=UserStatsResponse,
    tags=["User"],
    summary="Get user statistics (requires authentication)"
)
async def get_user_stats(
    current_user: dict = Depends(get_current_user)
):
    """
    Get authenticated user's analysis statistics.
    
    **Authentication:** REQUIRED
    
    Returns:
    - Total analyses performed
    - Analysis breakdown by type
    - Average document length
    - Last analysis date
    """
    try:
        logger.info(f"Stats requested for user {current_user['id']}")
        
        # Get stats from database service
        stats = await db_service.get_user_stats(current_user["id"])
        
        return UserStatsResponse(
            success=True,
            message="User statistics retrieved successfully",
            stats=UserStats(**stats)
        )
    
    except Exception as e:
        logger.error(f"Error fetching user stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user statistics"
        )


# ==================== USER HISTORY (PROTECTED) ====================

@router.get(
    "/history",
    tags=["User"],
    summary="Get analysis history (requires authentication)"
)
async def get_user_history(
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """
    Get authenticated user's analysis history.
    
    **Authentication:** REQUIRED
    
    Args:
        limit: Maximum number of records to return (default: 10)
        
    Returns:
        List of user's past analyses
    """
    try:
        logger.info(f"History requested for user {current_user['id']}, limit={limit}")
        
        # Get history from database service
        history = await db_service.get_user_history(
            user_id=current_user["id"],
            limit=limit
        )
        
        return {
            "success": True,
            "message": "History retrieved successfully",
            "analyses": history,
            "total": len(history)
        }
    
    except Exception as e:
        logger.error(f"Error fetching history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve history"
        )