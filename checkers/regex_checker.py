import re
from typing import Dict
from abc import ABC, abstractmethod


class BaseModerationChecker(ABC):
    """Abstract base class for moderation checkers."""
    
    @abstractmethod
    def check(self, text: str) -> Dict[str, float]:
        """Check text and return category scores."""
        raise NotImplementedError


class RegexModerationChecker(BaseModerationChecker):
    """Regex-based personal data leakage detector."""
    
    def __init__(self):
        self.patterns = {
            "pii/phone": [
                r"\b(?:\+49[-.\s]?)?\(?0?[1-9][0-9]{1,4}\)?[-.\s]?[0-9]{3,12}\b",  #  phone numbers
                r"\b0[1-9][0-9]{1,4}[-.\s]?[0-9]{3,12}\b",  #  landline format
                r"\b(?:\+49|0049)[-.\s]?[1-9][0-9]{1,4}[-.\s]?[0-9]{3,12}\b",  # International  format
                r"\b01[5-7][0-9][-.\s]?[0-9]{7,8}\b",  #  mobile format
            ],
            "pii/email": [
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email addresses
            ],
            "pii/credit_card": [
                r"\b4[0-9]{12}(?:[0-9]{3})?\b",  # Visa
                r"\b5[1-5][0-9]{14}\b",  # MasterCard
                r"\b3[47][0-9]{13}\b",  # American Express
                r"\b3[0-9]{4}\s[0-9]{6}\s[0-9]{5}\b",  # AmEx with spaces
                r"\b(?:\d{4}[-\s]?){3}\d{4}\b",  # Generic credit card format
            ],
            "pii/ip_address": [
                r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",  # IPv4 addresses
                r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b",  # IPv6 addresses (simplified)
            ],
            "pii/iban": [
                r"\bDE\d{2}\s?[0-9]{4}\s?[0-9]{4}\s?[0-9]{4}\s?[0-9]{4}\s?[0-9]{2}\b",  #  IBAN format
                r"\b[A-Z]{2}\d{2}\s?(?:[0-9A-Z]{4}\s?){3,7}[0-9A-Z]{1,4}\b",  # General IBAN format
                r"\bIBAN[\s:]?[A-Z]{2}\d{2}[0-9A-Z]{4,}\b",  # With IBAN prefix
                r"\bBIC[\s:]?[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}(?:[A-Z0-9]{3})?\b",  # BIC/SWIFT codes
            ]
        }
        
        # Compile patterns for efficiency
        self.compiled_patterns = {}
        for category, patterns in self.patterns.items():
            self.compiled_patterns[category] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
    
    def check(self, text: str) -> Dict[str, float]:
        """Check text against PII detection patterns and return scores."""
        scores = {}
        
        for category, patterns in self.compiled_patterns.items():
            score = 0.0
            matches = 0
            
            for pattern in patterns:
                if pattern.search(text):
                    matches += 1
            
            # Higher scoring for PII detection: 0.8 for first match, +0.1 for each additional
            if matches > 0:
                score = min(0.8 + (matches - 1) * 0.1, 1.0)
            
            scores[category] = score
        
        return scores
