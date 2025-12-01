"""
Database Service
Handles all database operations with Supabase
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from supabase import create_client, Client
from app.core.config import settings


class DatabaseService:
    """
    Service for handling database operations with Supabase.
    """
    
    def __init__(self):
        """Initialize Supabase client"""
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            print("⚠️  Supabase not configured. Database features will be disabled.")
            self.client = None
        else:
            self.client: Client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_KEY
            )
    
    def is_configured(self) -> bool:
        """Check if database is configured"""
        return self.client is not None
    
    # ========== PROFILE OPERATIONS ==========
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """
        Get user profile by ID.
        
        Args:
            user_id: User UUID
            
        Returns:
            User profile dict or None
        """
        if not self.client:
            return None
        
        try:
            response = self.client.table('profiles').select('*').eq('id', user_id).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error getting user profile: {e}")
            return None
    
    async def update_user_profile(self, user_id: str, updates: Dict) -> bool:
        """
        Update user profile.
        
        Args:
            user_id: User UUID
            updates: Dictionary of fields to update
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            return False
        
        try:
            self.client.table('profiles').update(updates).eq('id', user_id).execute()
            return True
        except Exception as e:
            print(f"Error updating user profile: {e}")
            return False
    
    # ========== DOCUMENT OPERATIONS ==========
    
    async def create_document(
        self,
        user_id: str,
        filename: str,
        file_size: int,
        file_type: str,
        file_path: str,
        document_type: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a document record.
        
        Args:
            user_id: User UUID
            filename: Original filename
            file_size: File size in bytes
            file_type: MIME type
            file_path: Storage path
            document_type: Type of document
            
        Returns:
            Document ID if successful, None otherwise
        """
        if not self.client:
            return None
        
        try:
            response = self.client.table('documents').insert({
                'user_id': user_id,
                'filename': filename,
                'file_size': file_size,
                'file_type': file_type,
                'file_path': file_path,
                'document_type': document_type,
                'upload_status': 'uploaded'
            }).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]['id']
            return None
        except Exception as e:
            print(f"Error creating document: {e}")
            return None
    
    async def get_user_documents(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """
        Get user's documents.
        
        Args:
            user_id: User UUID
            limit: Maximum number of documents
            offset: Offset for pagination
            
        Returns:
            List of document dicts
        """
        if not self.client:
            return []
        
        try:
            response = self.client.table('documents')\
                .select('*')\
                .eq('user_id', user_id)\
                .order('uploaded_at', desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()
            
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting user documents: {e}")
            return []
    
    # ========== ANALYSIS OPERATIONS ==========
    
    async def create_analysis(
        self,
        user_id: str,
        analysis_type: str,
        results: Dict[str, Any],
        document_id: Optional[str] = None,
        word_count: Optional[int] = None,
        risk_score: Optional[int] = None,
        risk_level: Optional[str] = None,
        processing_time_ms: Optional[float] = None
    ) -> Optional[str]:
        """
        Create an analysis record.
        
        Args:
            user_id: User UUID
            analysis_type: Type of analysis
            results: Analysis results as dict
            document_id: Related document ID (optional)
            word_count: Word count
            risk_score: Risk score
            risk_level: Risk level
            processing_time_ms: Processing time
            
        Returns:
            Analysis ID if successful, None otherwise
        """
        if not self.client:
            return None
        
        try:
            response = self.client.table('analyses').insert({
                'user_id': user_id,
                'document_id': document_id,
                'analysis_type': analysis_type,
                'status': 'completed',
                'results': results,
                'word_count': word_count,
                'risk_score': risk_score,
                'risk_level': risk_level,
                'processing_time_ms': processing_time_ms,
                'completed_at': datetime.utcnow().isoformat()
            }).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]['id']
            return None
        except Exception as e:
            print(f"Error creating analysis: {e}")
            return None
    
    async def get_user_analyses(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        analysis_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Get user's analyses.
        
        Args:
            user_id: User UUID
            limit: Maximum number of analyses
            offset: Offset for pagination
            analysis_type: Filter by type (optional)
            
        Returns:
            List of analysis dicts
        """
        if not self.client:
            return []
        
        try:
            query = self.client.table('analyses')\
                .select('*')\
                .eq('user_id', user_id)\
                .order('created_at', desc=True)
            
            if analysis_type:
                query = query.eq('analysis_type', analysis_type)
            
            response = query.range(offset, offset + limit - 1).execute()
            
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting user analyses: {e}")
            return []
    
    async def get_analysis_by_id(self, analysis_id: str, user_id: str) -> Optional[Dict]:
        """
        Get specific analysis by ID.
        
        Args:
            analysis_id: Analysis UUID
            user_id: User UUID (for authorization)
            
        Returns:
            Analysis dict or None
        """
        if not self.client:
            return None
        
        try:
            response = self.client.table('analyses')\
                .select('*')\
                .eq('id', analysis_id)\
                .eq('user_id', user_id)\
                .execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error getting analysis: {e}")
            return None
    
    # ========== STATISTICS ==========
    
    async def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get user statistics.
        
        Args:
            user_id: User UUID
            
        Returns:
            Statistics dict
        """
        if not self.client:
            return {
                'total_documents': 0,
                'total_analyses': 0,
                'avg_risk_score': 0,
                'total_processing_time_ms': 0
            }
        
        try:
            response = self.client.table('user_statistics')\
                .select('*')\
                .eq('user_id', user_id)\
                .execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            
            return {
                'total_documents': 0,
                'total_analyses': 0,
                'avg_risk_score': 0,
                'total_processing_time_ms': 0
            }
        except Exception as e:
            print(f"Error getting user statistics: {e}")
            return {
                'total_documents': 0,
                'total_analyses': 0,
                'avg_risk_score': 0,
                'total_processing_time_ms': 0
            }
    
    # ========== API USAGE TRACKING ==========
    
    async def log_api_usage(
        self,
        user_id: str,
        endpoint: str,
        method: str,
        tokens_used: int = 0,
        response_time_ms: Optional[float] = None,
        status_code: Optional[int] = None
    ) -> bool:
        """
        Log API usage.
        
        Args:
            user_id: User UUID
            endpoint: API endpoint
            method: HTTP method
            tokens_used: Number of tokens used
            response_time_ms: Response time
            status_code: HTTP status code
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            return False
        
        try:
            self.client.table('api_usage').insert({
                'user_id': user_id,
                'endpoint': endpoint,
                'method': method,
                'tokens_used': tokens_used,
                'response_time_ms': response_time_ms,
                'status_code': status_code
            }).execute()
            return True
        except Exception as e:
            print(f"Error logging API usage: {e}")
            return False


# Create service instance
db_service = DatabaseService()