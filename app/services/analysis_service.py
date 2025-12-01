"""
Analysis Service - Business logic for text and legal document analysis
Orchestrates the analyzer classes and prepares data for API responses
"""

from typing import Dict, Any, Optional
from app.core.text_analyzer import TextAnalyzer
from app.core.legal_analyzer import LegalAnalyzer
from app.models.schemas import (
    BasicStats, ReadabilityScore, SentimentAnalysis, Keyword,
    Party, DateInfo, MonetaryAmount, RiskAssessment, DocumentInfo
)
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AnalysisService:
    """
    Service class for handling all analysis operations.
    Acts as a bridge between API routes and analyzer classes.
    """
    
    @staticmethod
    def analyze_text(text: str) -> Dict[str, Any]:
        """
        Perform comprehensive text analysis.
        
        Args:
            text (str): Text content to analyze
            
        Returns:
            Dict: Structured analysis results
        """
        try:
            # Create analyzer instance
            analyzer = TextAnalyzer(text)
            
            # Get summary statistics
            stats = analyzer.get_summary_statistics()
            
            # Structure the response
            return {
                "basic_stats": BasicStats(**stats["basic_stats"]),
                "readability": ReadabilityScore(**stats["readability"]),
                "sentiment": SentimentAnalysis(**stats["sentiment"]),
                "top_keywords": [
                    Keyword(word=kw["word"], frequency=kw["frequency"]) 
                    for kw in stats["top_keywords"]
                ]
            }
        except Exception as e:
            logger.error(f"Error in text analysis: {str(e)}")
            raise ValueError(f"Text analysis failed: {str(e)}")
    
    @staticmethod
    def analyze_legal_document(text: str, document_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform comprehensive legal document analysis.
        
        Args:
            text (str): Legal document text
            document_type (str, optional): Type of document
            
        Returns:
            Dict: Structured legal analysis results
        """
        try:
            # Create legal analyzer instance
            analyzer = LegalAnalyzer(text, document_type)
            
            # Get comprehensive legal analysis
            legal_summary = analyzer.get_legal_summary()
            
            # Structure the response with proper models
            return {
                "document_info": DocumentInfo(**legal_summary["document_info"]),
                "parties": [Party(**party) for party in legal_summary["parties"]],
                "key_dates": [DateInfo(**date) for date in legal_summary["key_dates"]],
                "monetary_amounts": [
                    MonetaryAmount(**amount) for amount in legal_summary["monetary_amounts"]
                ],
                "identified_clauses": legal_summary["identified_clauses"],
                "risk_assessment": RiskAssessment(**legal_summary["risk_assessment"]),
                "text_statistics": legal_summary["text_statistics"]
            }
        except Exception as e:
            logger.error(f"Error in legal analysis: {str(e)}")
            raise ValueError(f"Legal analysis failed: {str(e)}")
    
    @staticmethod
    def analyze_feedback(text: str) -> Dict[str, Any]:
        """
        Analyze feedback or review text with focus on sentiment.
        
        Args:
            text (str): Feedback text
            
        Returns:
            Dict: Feedback analysis results
        """
        try:
            # Create analyzer instance
            analyzer = TextAnalyzer(text)
            
            # Get sentiment and readability
            sentiment = analyzer.sentiment_analysis()
            readability = analyzer.readability_score()
            
            # Extract key points (sentences with strong sentiment)
            sentences = analyzer.sentences
            key_points = []
            
            for sentence in sentences[:5]:  # Top 5 sentences
                if len(sentence.split()) > 3:  # Skip very short sentences
                    key_points.append(sentence)
            
            return {
                "sentiment": SentimentAnalysis(**sentiment),
                "key_points": key_points,
                "word_count": analyzer.word_count(),
                "readability": ReadabilityScore(**readability)
            }
        except Exception as e:
            logger.error(f"Error in feedback analysis: {str(e)}")
            raise ValueError(f"Feedback analysis failed: {str(e)}")
    
    @staticmethod
    def compare_documents(doc1: str, doc2: str) -> Dict[str, Any]:
        """
        Compare two documents for similarity and differences.
        
        Args:
            doc1 (str): First document text
            doc2 (str): Second document text
            
        Returns:
            Dict: Comparison results
        """
        try:
            analyzer1 = TextAnalyzer(doc1)
            analyzer2 = TextAnalyzer(doc2)
            
            # Get keywords from both documents
            keywords1 = set(word for word, _ in analyzer1.extract_keywords(20))
            keywords2 = set(word for word, _ in analyzer2.extract_keywords(20))
            
            # Calculate similarity based on common keywords
            common_keywords = keywords1.intersection(keywords2)
            all_keywords = keywords1.union(keywords2)
            
            if all_keywords:
                similarity_score = (len(common_keywords) / len(all_keywords)) * 100
            else:
                similarity_score = 0.0
            
            # Find differences
            unique_to_doc1 = keywords1 - keywords2
            unique_to_doc2 = keywords2 - keywords1
            
            key_differences = []
            if unique_to_doc1:
                key_differences.append(f"Unique to Document 1: {', '.join(list(unique_to_doc1)[:10])}")
            if unique_to_doc2:
                key_differences.append(f"Unique to Document 2: {', '.join(list(unique_to_doc2)[:10])}")
            
            # Common elements
            common_elements = list(common_keywords)[:10]
            
            # Recommendation
            if similarity_score > 70:
                recommendation = "Documents are highly similar"
            elif similarity_score > 40:
                recommendation = "Documents have moderate similarity"
            else:
                recommendation = "Documents are substantially different"
            
            return {
                "similarity_score": round(similarity_score, 2),
                "key_differences": key_differences if key_differences else ["No significant differences found"],
                "common_elements": common_elements if common_elements else ["No common elements found"],
                "recommendation": recommendation
            }
        except Exception as e:
            logger.error(f"Error in document comparison: {str(e)}")
            raise ValueError(f"Document comparison failed: {str(e)}")
    
    @staticmethod
    def batch_analyze(texts: list, analysis_type: str = "text") -> Dict[str, Any]:
        """
        Perform batch analysis on multiple texts.
        
        Args:
            texts (list): List of text strings
            analysis_type (str): Type of analysis (text, legal, feedback)
            
        Returns:
            Dict: Batch analysis results
        """
        results = []
        failed_count = 0
        errors = []
        
        for idx, text in enumerate(texts):
            try:
                if analysis_type == "text":
                    result = AnalysisService.analyze_text(text)
                elif analysis_type == "legal":
                    result = AnalysisService.analyze_legal_document(text)
                elif analysis_type == "feedback":
                    result = AnalysisService.analyze_feedback(text)
                else:
                    raise ValueError(f"Unknown analysis type: {analysis_type}")
                
                results.append({
                    "index": idx,
                    "success": True,
                    "result": result
                })
            except Exception as e:
                failed_count += 1
                error_msg = f"Text {idx}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
                
                results.append({
                    "index": idx,
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "total_processed": len(texts),
            "results": results,
            "failed_count": failed_count,
            "errors": errors if errors else None
        }
    
    @staticmethod
    def get_analysis_summary(text: str, analysis_type: str) -> str:
        """
        Generate a brief text summary of the analysis.
        
        Args:
            text (str): Text to analyze
            analysis_type (str): Type of analysis
            
        Returns:
            str: Brief summary
        """
        try:
            if analysis_type == "text":
                analyzer = TextAnalyzer(text)
                sentiment = analyzer.sentiment_analysis()
                return f"{analyzer.word_count()} words, {sentiment['sentiment']} sentiment"
            
            elif analysis_type == "legal":
                analyzer = LegalAnalyzer(text)
                doc_type = analyzer.identify_document_type()
                risk = analyzer.calculate_risk_score()
                return f"{doc_type}, Risk: {risk['risk_level']}"
            
            elif analysis_type == "feedback":
                analyzer = TextAnalyzer(text)
                sentiment = analyzer.sentiment_analysis()
                return f"Feedback: {sentiment['sentiment']} ({sentiment['polarity']:.2f})"
            
            else:
                return "Unknown analysis type"
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return "Summary generation failed"