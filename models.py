from typing import List, Optional, Union
from pydantic import BaseModel, Field


class ModerationRequest(BaseModel):
    """Request model for moderation API."""
    input: Union[str, List[str]] = Field(..., description="Text to analyze for moderation")
    model: Optional[str] = Field(default="omni-moderation-latest", description="Model to use for moderation")


class Categories(BaseModel):
    """Categories for PII detection results."""
    #  PII Categories
    pii_phone: bool = Field(default=False, alias="pii/phone")
    pii_email: bool = Field(default=False, alias="pii/email") 
    pii_credit_card: bool = Field(default=False, alias="pii/credit_card")
    pii_ip_address: bool = Field(default=False, alias="pii/ip_address")
    pii_iban: bool = Field(default=False, alias="pii/iban")
    
    # Legacy content moderation categories (for compatibility)
    sexual: bool = False
    hate: bool = False
    harassment: bool = False
    illicit: bool = False
    violence: bool = False
    sexual_minors: bool = Field(default=False, alias="sexual/minors")
    hate_threatening: bool = Field(default=False, alias="hate/threatening") 
    harassment_threatening: bool = Field(default=False, alias="harassment/threatening")
    illicit_violent: bool = Field(default=False, alias="illicit/violent")
    violence_graphic: bool = Field(default=False, alias="violence/graphic")
    self_harm: bool = Field(default=False, alias="self-harm")
    self_harm_intent: bool = Field(default=False, alias="self-harm/intent")
    self_harm_instructions: bool = Field(default=False, alias="self-harm/instructions")
    
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
    sexual: float = 0.0
    hate: float = 0.0
    harassment: float = 0.0
    illicit: float = 0.0
    violence: float = 0.0
    sexual_minors: float = Field(default=0.0, alias="sexual/minors")
    hate_threatening: float = Field(default=0.0, alias="hate/threatening")
    harassment_threatening: float = Field(default=0.0, alias="harassment/threatening") 
    illicit_violent: float = Field(default=0.0, alias="illicit/violent")
    violence_graphic: float = Field(default=0.0, alias="violence/graphic")
    self_harm: float = Field(default=0.0, alias="self-harm")
    self_harm_intent: float = Field(default=0.0, alias="self-harm/intent")
    self_harm_instructions: float = Field(default=0.0, alias="self-harm/instructions")
    
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
    sexual: List[str] = []
    hate: List[str] = []
    harassment: List[str] = []
    illicit: List[str] = []
    violence: List[str] = []
    sexual_minors: List[str] = Field(default=[], alias="sexual/minors")
    hate_threatening: List[str] = Field(default=[], alias="hate/threatening")
    harassment_threatening: List[str] = Field(default=[], alias="harassment/threatening")
    illicit_violent: List[str] = Field(default=[], alias="illicit/violent") 
    violence_graphic: List[str] = Field(default=[], alias="violence/graphic")
    self_harm: List[str] = Field(default=[], alias="self-harm")
    self_harm_intent: List[str] = Field(default=[], alias="self-harm/intent")
    self_harm_instructions: List[str] = Field(default=[], alias="self-harm/instructions")
    
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
