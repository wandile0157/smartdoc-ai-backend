"""
Text Analyzer - Base class for analyzing text content
Demonstrates OOP principles and text processing capabilities
"""

from typing import Dict, List, Optional
import re
from textblob import TextBlob


class TextAnalyzer:
    """
    Base text analyzer class that provides fundamental text analysis capabilities.
    This class demonstrates clean OOP design and serves as a foundation for
    specialized analyzers.
    """
    
    def __init__(self, text: str):
        """
        Initialize the text analyzer with content to analyze.
        
        Args:
            text (str): The text content to analyze
        """
        self.text = text
        self.cleaned_text = self._clean_text(text)
        self._word_list = None
        self._sentence_list = None
        
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text by removing extra whitespace.
        
        Args:
            text (str): Raw text to clean
            
        Returns:
            str: Cleaned text
        """
        # Remove extra whitespace and normalize line breaks
        cleaned = re.sub(r'\s+', ' ', text)
        return cleaned.strip()
    
    @property
    def words(self) -> List[str]:
        """
        Get list of words from the text (lazy loading).
        
        Returns:
            List[str]: List of words
        """
        if self._word_list is None:
            # Split on whitespace and punctuation, keep only alphanumeric
            self._word_list = re.findall(r'\b\w+\b', self.cleaned_text.lower())
        return self._word_list
    
    @property
    def sentences(self) -> List[str]:
        """
        Get list of sentences from the text (lazy loading).
        
        Returns:
            List[str]: List of sentences
        """
        if self._sentence_list is None:
            # Split on sentence-ending punctuation
            self._sentence_list = re.split(r'[.!?]+', self.cleaned_text)
            self._sentence_list = [s.strip() for s in self._sentence_list if s.strip()]
        return self._sentence_list
    
    def word_count(self) -> int:
        """
        Count total words in the text.
        
        Returns:
            int: Number of words
        """
        return len(self.words)
    
    def sentence_count(self) -> int:
        """
        Count total sentences in the text.
        
        Returns:
            int: Number of sentences
        """
        return len(self.sentences)
    
    def character_count(self, include_spaces: bool = True) -> int:
        """
        Count characters in the text.
        
        Args:
            include_spaces (bool): Whether to include spaces in count
            
        Returns:
            int: Number of characters
        """
        if include_spaces:
            return len(self.text)
        else:
            return len(self.text.replace(' ', '').replace('\n', '').replace('\t', ''))
    
    def average_word_length(self) -> float:
        """
        Calculate average word length.
        
        Returns:
            float: Average word length in characters
        """
        if not self.words:
            return 0.0
        total_chars = sum(len(word) for word in self.words)
        return round(total_chars / len(self.words), 2)
    
    def average_sentence_length(self) -> float:
        """
        Calculate average sentence length in words.
        
        Returns:
            float: Average words per sentence
        """
        if not self.sentences:
            return 0.0
        return round(self.word_count() / self.sentence_count(), 2)
    
    def readability_score(self) -> Dict[str, float]:
        """
        Calculate readability metrics (Flesch Reading Ease).
        Higher scores indicate easier readability (0-100 scale).
        
        Returns:
            Dict[str, float]: Readability metrics
        """
        words = self.word_count()
        sentences = self.sentence_count()
        
        if sentences == 0 or words == 0:
            return {
                "flesch_reading_ease": 0.0,
                "readability_level": "Unable to calculate"
            }
        
        # Count syllables (simplified approximation)
        syllables = self._count_syllables()
        
        # Flesch Reading Ease formula
        # Score = 206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)
        score = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
        score = max(0, min(100, score))  # Clamp between 0-100
        
        # Determine readability level
        if score >= 90:
            level = "Very Easy"
        elif score >= 80:
            level = "Easy"
        elif score >= 70:
            level = "Fairly Easy"
        elif score >= 60:
            level = "Standard"
        elif score >= 50:
            level = "Fairly Difficult"
        elif score >= 30:
            level = "Difficult"
        else:
            level = "Very Difficult"
        
        return {
            "flesch_reading_ease": round(score, 2),
            "readability_level": level
        }
    
    def _count_syllables(self) -> int:
        """
        Count approximate syllables in text (simplified method).
        
        Returns:
            int: Estimated syllable count
        """
        syllable_count = 0
        vowels = "aeiouy"
        
        for word in self.words:
            word = word.lower()
            count = 0
            previous_was_vowel = False
            
            for char in word:
                is_vowel = char in vowels
                if is_vowel and not previous_was_vowel:
                    count += 1
                previous_was_vowel = is_vowel
            
            # Adjust for silent 'e'
            if word.endswith('e'):
                count -= 1
            
            # Every word has at least one syllable
            if count == 0:
                count = 1
                
            syllable_count += count
        
        return syllable_count
    
    def sentiment_analysis(self) -> Dict[str, any]:
        """
        Perform sentiment analysis on the text using TextBlob.
        
        Returns:
            Dict: Sentiment polarity and subjectivity scores
        """
        try:
            blob = TextBlob(self.cleaned_text)
            polarity = blob.sentiment.polarity  # -1 to 1 (negative to positive)
            subjectivity = blob.sentiment.subjectivity  # 0 to 1 (objective to subjective)
            
            # Determine sentiment label
            if polarity > 0.3:
                sentiment = "Positive"
            elif polarity < -0.3:
                sentiment = "Negative"
            else:
                sentiment = "Neutral"
            
            return {
                "polarity": round(polarity, 3),
                "subjectivity": round(subjectivity, 3),
                "sentiment": sentiment
            }
        except Exception as e:
            return {
                "polarity": 0.0,
                "subjectivity": 0.0,
                "sentiment": "Unable to analyze",
                "error": str(e)
            }
    
    def extract_keywords(self, top_n: int = 10) -> List[tuple]:
        """
        Extract most frequent keywords (excluding common stop words).
        
        Args:
            top_n (int): Number of top keywords to return
            
        Returns:
            List[tuple]: List of (word, frequency) tuples
        """
        # Simple stop words list
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
        
        # Count word frequencies
        word_freq = {}
        for word in self.words:
            if word not in stop_words and len(word) > 2:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top N
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return sorted_words[:top_n]
    
    def get_summary_statistics(self) -> Dict[str, any]:
        """
        Get comprehensive statistics about the text.
        
        Returns:
            Dict: Complete text statistics
        """
        readability = self.readability_score()
        sentiment = self.sentiment_analysis()
        keywords = self.extract_keywords(5)
        
        return {
            "basic_stats": {
                "word_count": self.word_count(),
                "sentence_count": self.sentence_count(),
                "character_count": self.character_count(include_spaces=True),
                "character_count_no_spaces": self.character_count(include_spaces=False),
                "average_word_length": self.average_word_length(),
                "average_sentence_length": self.average_sentence_length()
            },
            "readability": readability,
            "sentiment": sentiment,
            "top_keywords": [{"word": word, "frequency": freq} for word, freq in keywords]
        }