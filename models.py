from typing import List, Optional, Union
from pydantic import BaseModel, Field


class ModerationRequest(BaseModel):
    """Request model for moderation API."""
    input: Union[str, List[str]] = Field(..., description="Text to analyze for moderation")
    model: Optional[str] = Field(default="moderation-latest", description="Model to use for moderation")


class Categories(BaseModel):
    """Categories for PII detection results."""
    #  PII Categories
    pii_phone: bool = Field(default=False, alias="pii/phone")
    pii_email: bool = Field(default=False, alias="pii/email") 
    pii_credit_card: bool = Field(default=False, alias="pii/credit_card")
    pii_ip_address: bool = Field(default=False, alias="pii/ip_address")
    pii_iban: bool = Field(default=False, alias="pii/iban")
    
    # Legacy content moderation categories (for compatibility)
    hate: bool = False
    harassment: bool = False
    violence: bool = False
    hate_threatening: bool = Field(default=False, alias="hate/threatening") 
    harassment_threatening: bool = Field(default=False, alias="harassment/threatening")
    
    class Config:
        validate_by_name = True


class CategoryScores(BaseModel):
    """Category scores for PII detection results."""
    #  PII Categories
    pii_phone: float = Field(default=0.0, alias="pii/phone")
    pii_email: float = Field(default=0.0, alias="pii/email")
    pii_credit_card: float = Field(default=0.0, alias="pii/credit_card")
    pii_ip_address: float = Field(default=0.0, alias="pii/ip_address")
    pii_iban: float = Field(default=0.0, alias="pii/iban")
    
    # Legacy content moderation categories (for compatibility)
    hate: float = 0.0
    harassment: float = 0.0
    violence: float = 0.0
    hate_threatening: float = Field(default=0.0, alias="hate/threatening")
    harassment_threatening: float = Field(default=0.0, alias="harassment/threatening") 
    
    class Config:
        validate_by_name = True


class CategoryAppliedInputTypes(BaseModel):
    """Applied input types for each category."""
    #  PII Categories
    pii_phone: List[str] = Field(default=[], alias="pii/phone")
    pii_email: List[str] = Field(default=[], alias="pii/email")
    pii_credit_card: List[str] = Field(default=[], alias="pii/credit_card")
    pii_ip_address: List[str] = Field(default=[], alias="pii/ip_address")
    pii_iban: List[str] = Field(default=[], alias="pii/iban")
    
    # Legacy content moderation categories (for compatibility)
    hate: List[str] = []
    harassment: List[str] = []
    violence: List[str] = []
    hate_threatening: List[str] = Field(default=[], alias="hate/threatening")
    harassment_threatening: List[str] = Field(default=[], alias="harassment/threatening")
    
    class Config:
        validate_by_name = True


class ModerationResult(BaseModel):
    """Single moderation result."""
    flagged: bool
    categories: Categories
    category_scores: CategoryScores
    category_applied_input_types: CategoryAppliedInputTypes


class ModerationResponse(BaseModel):
    """Response model for moderation API."""
    id: str
    model: str
    results: List[ModerationResult]
