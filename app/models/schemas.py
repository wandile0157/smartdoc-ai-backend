"""
Pydantic models for request/response validation
Defines data structures for API endpoints
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ==================== ENUMS ====================

class DocumentType(str, Enum):
    """Supported document types"""
    EMPLOYMENT_CONTRACT = "employment_contract"
    LEASE_AGREEMENT = "lease_agreement"
    NDA = "nda"
    SERVICE_AGREEMENT = "service_agreement"
    SALES_AGREEMENT = "sales_agreement"
    OTHER = "other"


class AnalysisType(str, Enum):
    """Types of analysis available"""
    TEXT = "text"
    LEGAL = "legal"
    FEEDBACK = "feedback"


class RiskLevel(str, Enum):
    """Risk assessment levels"""
    LOW = "Low Risk"
    MEDIUM = "Medium Risk"
    HIGH = "High Risk"


# ==================== BASE MODELS ====================

class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# ==================== TEXT ANALYSIS MODELS ====================

class TextAnalysisRequest(BaseModel):
    """Request model for text analysis"""
    text: str = Field(..., min_length=10, description="Text content to analyze")
    analysis_type: AnalysisType = Field(default=AnalysisType.TEXT, description="Type of analysis")
    
    @validator('text')
    def text_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Text content cannot be empty')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "This is a sample text for analysis. It contains multiple sentences.",
                "analysis_type": "text"
            }
        }


class BasicStats(BaseModel):
    """Basic text statistics"""
    word_count: int
    sentence_count: int
    character_count: int
    character_count_no_spaces: int
    average_word_length: float
    average_sentence_length: float


class ReadabilityScore(BaseModel):
    """Readability metrics"""
    flesch_reading_ease: float = Field(..., ge=0, le=100)
    readability_level: str


class SentimentAnalysis(BaseModel):
    """Sentiment analysis results"""
    polarity: float = Field(..., ge=-1, le=1)
    subjectivity: float = Field(..., ge=0, le=1)
    sentiment: str


class Keyword(BaseModel):
    """Keyword with frequency"""
    word: str
    frequency: int


class TextAnalysisResponse(BaseResponse):
    """Response model for text analysis"""
    basic_stats: BasicStats
    readability: ReadabilityScore
    sentiment: SentimentAnalysis
    top_keywords: List[Keyword]


# ==================== LEGAL ANALYSIS MODELS ====================

class LegalAnalysisRequest(BaseModel):
    """Request model for legal document analysis"""
    text: str = Field(..., min_length=50, description="Legal document text")
    document_type: Optional[DocumentType] = Field(None, description="Type of legal document")
    
    @validator('text')
    def text_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Legal document text cannot be empty')
        if len(v.strip()) < 50:
            raise ValueError('Legal document text too short (minimum 50 characters)')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "This Employment Contract is entered into between TechCorp (Pty) Ltd and John Doe...",
                "document_type": "employment_contract"
            }
        }


class Party(BaseModel):
    """Legal party information"""
    name: str
    type: str
    role: str


class DateInfo(BaseModel):
    """Date information from document"""
    date: str
    format: str
    context: str


class MonetaryAmount(BaseModel):
    """Monetary amount information"""
    amount: str
    currency: str
    context: str


class RiskAssessment(BaseModel):
    """Risk assessment results"""
    risk_score: float = Field(..., ge=0, le=100)
    risk_level: RiskLevel
    color: str
    high_risk_terms_found: int
    medium_risk_terms_found: int
    total_risk_terms: int


class DocumentInfo(BaseModel):
    """Document metadata"""
    document_type: str
    analysis_date: str


class LegalAnalysisResponse(BaseResponse):
    """Response model for legal analysis"""
    document_info: DocumentInfo
    parties: List[Party]
    key_dates: List[DateInfo]
    monetary_amounts: List[MonetaryAmount]
    identified_clauses: Dict[str, int]
    risk_assessment: RiskAssessment
    text_statistics: Dict[str, Any]


# ==================== FEEDBACK ANALYSIS MODELS ====================

class FeedbackAnalysisRequest(BaseModel):
    """Request model for feedback/review analysis"""
    text: str = Field(..., min_length=10, description="Feedback or review text")
    source: Optional[str] = Field(None, description="Source of feedback (e.g., 'customer_review', 'employee_feedback')")
    
    @validator('text')
    def text_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Feedback text cannot be empty')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "The service was excellent and the staff were very helpful. However, the waiting time was too long.",
                "source": "customer_review"
            }
        }


class FeedbackAnalysisResponse(BaseResponse):
    """Response model for feedback analysis"""
    sentiment: SentimentAnalysis
    key_points: List[str]
    word_count: int
    readability: ReadabilityScore


# ==================== FILE UPLOAD MODELS ====================

class FileUploadResponse(BaseResponse):
    """Response model for file upload"""
    filename: str
    file_size: int
    file_type: str
    extracted_text: str
    text_length: int


# ==================== ANALYSIS HISTORY MODELS ====================

class AnalysisHistoryItem(BaseModel):
    """Single analysis history item"""
    id: str
    user_id: Optional[str] = None
    analysis_type: AnalysisType
    document_type: Optional[str] = None
    created_at: datetime
    summary: Dict[str, Any]


class AnalysisHistoryResponse(BaseResponse):
    """Response model for analysis history"""
    total_count: int
    items: List[AnalysisHistoryItem]


# ==================== ERROR MODELS ====================

class ErrorDetail(BaseModel):
    """Detailed error information"""
    field: Optional[str] = None
    message: str
    type: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    error: str
    details: Optional[List[ErrorDetail]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "Validation error",
                "details": [
                    {
                        "field": "text",
                        "message": "Text content cannot be empty",
                        "type": "value_error"
                    }
                ],
                "timestamp": "2024-11-30T10:30:00"
            }
        }


# ==================== HEALTH CHECK MODELS ====================

class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    version: str
    timestamp: datetime = Field(default_factory=datetime.now)
    services: Dict[str, str] = {
        "database": "unknown",
        "api": "operational"
    }


# ==================== USER MODELS (for future auth) ====================

class UserBase(BaseModel):
    """Base user model"""
    email: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation model"""
    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    """User response model"""
    id: str
    created_at: datetime
    is_active: bool = True


# ==================== STATISTICS MODELS ====================

class UserStats(BaseModel):
    """User statistics"""
    total_analyses: int = 0
    text_analyses: int = 0
    legal_analyses: int = 0
    feedback_analyses: int = 0
    total_documents_processed: int = 0
    average_document_length: float = 0.0
    last_analysis_date: Optional[datetime] = None


class UserStatsResponse(BaseResponse):
    """User statistics response"""
    stats: UserStats


# ==================== BATCH ANALYSIS MODELS ====================

class BatchAnalysisRequest(BaseModel):
    """Request for batch analysis"""
    texts: List[str] = Field(..., min_items=1, max_items=10)
    analysis_type: AnalysisType = Field(default=AnalysisType.TEXT)
    
    @validator('texts')
    def texts_not_empty(cls, v):
        if not v:
            raise ValueError('At least one text is required')
        for text in v:
            if not text or not text.strip():
                raise ValueError('All texts must have content')
        return [text.strip() for text in v]


class BatchAnalysisResponse(BaseResponse):
    """Response for batch analysis"""
    total_processed: int
    results: List[Dict[str, Any]]
    failed_count: int = 0
    errors: Optional[List[str]] = None


# ==================== OPENAI INTEGRATION MODELS ====================

class OpenAIAnalysisRequest(BaseModel):
    """Request for OpenAI-powered analysis"""
    text: str = Field(..., min_length=10)
    prompt: Optional[str] = Field(None, description="Custom analysis prompt")
    model: str = Field(default="gpt-4o-mini", description="OpenAI model to use")
    max_tokens: int = Field(default=500, ge=100, le=2000)


class OpenAIAnalysisResponse(BaseResponse):
    """Response from OpenAI analysis"""
    analysis: str
    tokens_used: int
    model_used: str


# ==================== DOCUMENT COMPARISON MODELS ====================

class DocumentComparisonRequest(BaseModel):
    """Request to compare two documents"""
    document1: str = Field(..., min_length=50)
    document2: str = Field(..., min_length=50)
    comparison_type: str = Field(default="similarity", description="Type: similarity, differences, or both")


class DocumentComparisonResponse(BaseResponse):
    """Response for document comparison"""
    similarity_score: float = Field(..., ge=0, le=100)
    key_differences: List[str]
    common_elements: List[str]
    recommendation: str



