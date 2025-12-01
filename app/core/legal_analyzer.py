"""
Legal Analyzer - Specialized analyzer for legal documents
Inherits from TextAnalyzer and adds legal-specific analysis capabilities
Focused on South African legal context
"""

from typing import Dict, List, Optional, Tuple
import re
from datetime import datetime
from .text_analyzer import TextAnalyzer


class LegalAnalyzer(TextAnalyzer):
    """
    Specialized analyzer for legal documents with South African context.
    Inherits from TextAnalyzer and extends with legal-specific functionality.
    """
    
    # South African legal keywords for risk assessment
    HIGH_RISK_TERMS = [
        'penalty', 'penalties', 'termination', 'breach', 'default',
        'liability', 'damages', 'indemnify', 'indemnification',
        'waiver', 'forfeit', 'forfeiture', 'non-refundable',
        'irrevocable', 'unconditional', 'binding', 'irreversible'
    ]
    
    MEDIUM_RISK_TERMS = [
        'obligation', 'obligations', 'requirement', 'requirements',
        'must', 'shall', 'mandatory', 'compulsory', 'necessary',
        'restricted', 'prohibition', 'prohibited', 'forbidden'
    ]
    
    # South African company suffixes
    SA_COMPANY_SUFFIXES = [
        'Pty Ltd', 'PTY LTD', '(Pty) Ltd', '(PTY) LTD',
        'CC', 'Close Corporation',
        'NPC', 'Non-Profit Company',
        'SOC Ltd', 'State Owned Company',
        'Inc', 'Incorporated'
    ]
    
    # Common legal clause types
    CLAUSE_PATTERNS = {
        'confidentiality': r'confidential(?:ity)?|non-disclosure|proprietary information',
        'termination': r'termination|cancellation|end(?:ing)? (?:of )?(?:this )?agreement',
        'payment': r'payment|compensation|remuneration|salary|fee|amount',
        'liability': r'liability|responsible|accountable|liable',
        'indemnity': r'indemnif(?:y|ication)|hold harmless',
        'dispute_resolution': r'dispute resolution|arbitration|mediation|jurisdiction',
        'force_majeure': r'force majeure|act of god|unforeseen circumstances',
        'amendment': r'amendment|modification|change|alteration',
        'notice': r'notice|notification|inform|advise in writing',
        'governing_law': r'governing law|applicable law|south african law'
    }
    
    def __init__(self, text: str, document_type: Optional[str] = None):
        """
        Initialize the legal analyzer.
        
        Args:
            text (str): Legal document text to analyze
            document_type (str, optional): Type of document (contract, lease, nda, etc.)
        """
        super().__init__(text)
        self.document_type = document_type
        self._parties = None
        self._dates = None
        self._amounts = None
        self._clauses = None
    
    def identify_document_type(self) -> str:
        """
        Attempt to identify the type of legal document.
        
        Returns:
            str: Identified document type
        """
        text_lower = self.text.lower()
        
        type_keywords = {
            'Employment Contract': ['employment', 'employee', 'employer', 'position', 'duties'],
            'Lease Agreement': ['lease', 'tenant', 'landlord', 'premises', 'rent', 'rental'],
            'NDA': ['non-disclosure', 'confidential', 'confidentiality agreement', 'nda'],
            'Service Agreement': ['service', 'services', 'provider', 'client', 'deliverables'],
            'Sales Agreement': ['sale', 'purchase', 'buyer', 'seller', 'goods'],
            'Partnership Agreement': ['partner', 'partnership', 'joint venture'],
            'Loan Agreement': ['loan', 'lender', 'borrower', 'principal', 'interest']
        }
        
        scores = {}
        for doc_type, keywords in type_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[doc_type] = score
        
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return 'Unknown Document Type'
    
    def extract_parties(self) -> List[Dict[str, str]]:
        """
        Extract parties mentioned in the legal document.
        Looks for names followed by SA company suffixes or in specific contexts.
        
        Returns:
            List[Dict]: List of identified parties with their roles
        """
        if self._parties is not None:
            return self._parties
        
        parties = []
        text = self.text
        
        # Pattern 1: Company names with SA suffixes
        for suffix in self.SA_COMPANY_SUFFIXES:
            # Match company name before suffix (up to 5 words)
            pattern = r'([A-Z][A-Za-z0-9\s&]{2,50})\s+' + re.escape(suffix)
            matches = re.finditer(pattern, text)
            for match in matches:
                company_name = f"{match.group(1).strip()} {suffix}"
                if company_name not in [p['name'] for p in parties]:
                    parties.append({
                        'name': company_name,
                        'type': 'Company',
                        'role': 'Party'
                    })
        
        # Pattern 2: "between X and Y" structure
        between_pattern = r'between\s+([A-Z][A-Za-z\s&\.]{2,100})\s+(?:and|&)\s+([A-Z][A-Za-z\s&\.]{2,100})'
        between_matches = re.finditer(between_pattern, text, re.IGNORECASE)
        for match in between_matches:
            party1 = match.group(1).strip()
            party2 = match.group(2).strip()
            
            if len(party1.split()) <= 10 and party1 not in [p['name'] for p in parties]:
                parties.append({'name': party1, 'type': 'Entity', 'role': 'First Party'})
            if len(party2.split()) <= 10 and party2 not in [p['name'] for p in parties]:
                parties.append({'name': party2, 'type': 'Entity', 'role': 'Second Party'})
        
        # Pattern 3: Role-based identification
        role_patterns = {
            'Employer': r'(?:the\s+)?Employer[:\s]+([A-Z][A-Za-z\s&\.]{2,50})',
            'Employee': r'(?:the\s+)?Employee[:\s]+([A-Z][A-Za-z\s&\.]{2,50})',
            'Landlord': r'(?:the\s+)?Landlord[:\s]+([A-Z][A-Za-z\s&\.]{2,50})',
            'Tenant': r'(?:the\s+)?Tenant[:\s]+([A-Z][A-Za-z\s&\.]{2,50})',
            'Client': r'(?:the\s+)?Client[:\s]+([A-Z][A-Za-z\s&\.]{2,50})',
            'Service Provider': r'(?:the\s+)?(?:Service\s+)?Provider[:\s]+([A-Z][A-Za-z\s&\.]{2,50})'
        }
        
        for role, pattern in role_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                party_name = match.group(1).strip()
                if len(party_name.split()) <= 8 and party_name not in [p['name'] for p in parties]:
                    parties.append({'name': party_name, 'type': 'Entity', 'role': role})
        
        self._parties = parties if parties else [{'name': 'Not identified', 'type': 'Unknown', 'role': 'Unknown'}]
        return self._parties
    
    def extract_dates(self) -> List[Dict[str, str]]:
        """
        Extract dates mentioned in the document.
        
        Returns:
            List[Dict]: List of dates with context
        """
        if self._dates is not None:
            return self._dates
        
        dates = []
        
        # Pattern 1: DD Month YYYY (e.g., 15 March 2024)
        pattern1 = r'\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b'
        matches = re.finditer(pattern1, self.text, re.IGNORECASE)
        for match in matches:
            dates.append({
                'date': match.group(0),
                'format': 'DD Month YYYY',
                'context': self._get_context(match.start(), match.end())
            })
        
        # Pattern 2: YYYY-MM-DD or YYYY/MM/DD
        pattern2 = r'\b(\d{4})[/-](\d{1,2})[/-](\d{1,2})\b'
        matches = re.finditer(pattern2, self.text)
        for match in matches:
            dates.append({
                'date': match.group(0),
                'format': 'YYYY-MM-DD',
                'context': self._get_context(match.start(), match.end())
            })
        
        # Pattern 3: DD/MM/YYYY
        pattern3 = r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b'
        matches = re.finditer(pattern3, self.text)
        for match in matches:
            dates.append({
                'date': match.group(0),
                'format': 'DD/MM/YYYY',
                'context': self._get_context(match.start(), match.end())
            })
        
        self._dates = dates if dates else [{'date': 'No dates found', 'format': 'N/A', 'context': ''}]
        return self._dates
    
    def extract_monetary_amounts(self) -> List[Dict[str, str]]:
        """
        Extract monetary amounts (prioritizing South African Rands).
        
        Returns:
            List[Dict]: List of monetary amounts with context
        """
        if self._amounts is not None:
            return self._amounts
        
        amounts = []
        
        # Pattern 1: R followed by amount (South African Rands)
        pattern1 = r'R\s*(\d+(?:[,\s]\d{3})*(?:\.\d{2})?)'
        matches = re.finditer(pattern1, self.text)
        for match in matches:
            amounts.append({
                'amount': match.group(0),
                'currency': 'ZAR (Rands)',
                'context': self._get_context(match.start(), match.end())
            })
        
        # Pattern 2: Amount followed by Rand/Rands
        pattern2 = r'(\d+(?:[,\s]\d{3})*(?:\.\d{2})?)\s*Rands?'
        matches = re.finditer(pattern2, self.text, re.IGNORECASE)
        for match in matches:
            amounts.append({
                'amount': match.group(0),
                'currency': 'ZAR (Rands)',
                'context': self._get_context(match.start(), match.end())
            })
        
        # Pattern 3: ZAR amounts
        pattern3 = r'ZAR\s*(\d+(?:[,\s]\d{3})*(?:\.\d{2})?)'
        matches = re.finditer(pattern3, self.text)
        for match in matches:
            amounts.append({
                'amount': match.group(0),
                'currency': 'ZAR (Rands)',
                'context': self._get_context(match.start(), match.end())
            })
        
        self._amounts = amounts if amounts else [{'amount': 'No amounts found', 'currency': 'N/A', 'context': ''}]
        return self._amounts
    
    def identify_clauses(self) -> Dict[str, List[str]]:
        """
        Identify common legal clauses in the document.
        
        Returns:
            Dict: Dictionary of clause types and their occurrences
        """
        if self._clauses is not None:
            return self._clauses
        
        identified_clauses = {}
        text_lower = self.text.lower()
        
        for clause_type, pattern in self.CLAUSE_PATTERNS.items():
            matches = re.finditer(pattern, text_lower)
            occurrences = []
            
            for match in matches:
                context = self._get_context(match.start(), match.end(), chars=150)
                occurrences.append(context)
            
            if occurrences:
                identified_clauses[clause_type] = occurrences
        
        self._clauses = identified_clauses
        return self._clauses
    
    def calculate_risk_score(self) -> Dict[str, any]:
        """
        Calculate risk score based on presence of high/medium risk terms.
        
        Returns:
            Dict: Risk assessment with score and breakdown
        """
        text_lower = self.text.lower()
        
        high_risk_count = sum(1 for term in self.HIGH_RISK_TERMS if term in text_lower)
        medium_risk_count = sum(1 for term in self.MEDIUM_RISK_TERMS if term in text_lower)
        
        # Calculate risk score (0-100)
        # High risk terms worth 3 points, medium worth 1 point
        raw_score = (high_risk_count * 3) + medium_risk_count
        
        # Normalize to 0-100 scale (assuming max 50 points is very high risk)
        risk_score = min(100, (raw_score / 50) * 100)
        
        # Determine risk level
        if risk_score >= 70:
            risk_level = "High Risk"
            color = "red"
        elif risk_score >= 40:
            risk_level = "Medium Risk"
            color = "orange"
        else:
            risk_level = "Low Risk"
            color = "green"
        
        return {
            'risk_score': round(risk_score, 2),
            'risk_level': risk_level,
            'color': color,
            'high_risk_terms_found': high_risk_count,
            'medium_risk_terms_found': medium_risk_count,
            'total_risk_terms': high_risk_count + medium_risk_count
        }
    
    def _get_context(self, start: int, end: int, chars: int = 100) -> str:
        """
        Get context around a match position.
        
        Args:
            start (int): Start position of match
            end (int): End position of match
            chars (int): Number of characters to include on each side
            
        Returns:
            str: Context string
        """
        context_start = max(0, start - chars)
        context_end = min(len(self.text), end + chars)
        context = self.text[context_start:context_end].strip()
        
        if context_start > 0:
            context = '...' + context
        if context_end < len(self.text):
            context = context + '...'
        
        return context
    
    def get_legal_summary(self) -> Dict[str, any]:
        """
        Get comprehensive legal document analysis.
        
        Returns:
            Dict: Complete legal analysis
        """
        # Get base text statistics
        base_stats = self.get_summary_statistics()
        
        # Get legal-specific analysis
        document_type = self.identify_document_type()
        parties = self.extract_parties()
        dates = self.extract_dates()
        amounts = self.extract_monetary_amounts()
        clauses = self.identify_clauses()
        risk_assessment = self.calculate_risk_score()
        
        return {
            'document_info': {
                'document_type': document_type,
                'analysis_date': datetime.now().isoformat(),
            },
            'parties': parties,
            'key_dates': dates[:5] if len(dates) > 5 else dates,  # Limit to top 5
            'monetary_amounts': amounts[:5] if len(amounts) > 5 else amounts,  # Limit to top 5
            'identified_clauses': {
                clause_type: len(occurrences) 
                for clause_type, occurrences in clauses.items()
            },
            'risk_assessment': risk_assessment,
            'text_statistics': base_stats
        }