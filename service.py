import uuid
from typing import Dict, List, Union
from checkers import RegexModerationChecker, BERT_AVAILABLE
from models import ModerationResponse, ModerationResult, Categories, CategoryScores, CategoryAppliedInputTypes


class ModerationService:
    """Main moderation service that combines multiple checkers."""
    
    def __init__(self, use_bert: bool = True, flagging_threshold: float = 0.5):
        """
        Initialize the moderation service.
        
        Args:
            use_bert: Whether to use BERT-based checking
            flagging_threshold: Threshold above which content is flagged
        """
        self.regex_checker = RegexModerationChecker()
        self.use_bert = use_bert and BERT_AVAILABLE
        self.flagging_threshold = flagging_threshold
        
        if self.use_bert:
            try:
                from checkers import BertModerationChecker
                self.bert_checker = BertModerationChecker()
                print("BERT checker initialized successfully")
            except (ImportError, RuntimeError, OSError) as e:
                print(f"Could not initialize BERT checker: {e}")
                self.use_bert = False
        else:
            self.bert_checker = None
            if use_bert:
                print("BERT checker not available, using regex only")
    
    def _combine_scores(self, regex_scores: Dict[str, float], bert_scores: Dict[str, float] = None) -> Dict[str, float]:
        """
        Combine scores from different checkers.
        
        Args:
            regex_scores: Scores from regex checker
            bert_scores: Scores from BERT checker (optional)
            
        Returns:
            Combined scores
        """
        if bert_scores is None:
            return regex_scores
        
        # Get all unique categories from both checkers
        all_categories = set(regex_scores.keys()) | set(bert_scores.keys())
        
        combined = {}
        for category in all_categories:
            # Take maximum of both scores
            regex_score = regex_scores.get(category, 0.0)
            bert_score = bert_scores.get(category, 0.0)
            combined[category] = max(regex_score, bert_score)
        
        return combined
    
    def _scores_to_categories(self, scores: Dict[str, float]) -> Categories:
        """Convert scores to boolean categories."""
        return Categories(
            #  PII Categories
            **{
                "pii/phone": scores.get("pii/phone", 0.0) > self.flagging_threshold,
                "pii/email": scores.get("pii/email", 0.0) > self.flagging_threshold,
                "pii/credit_card": scores.get("pii/credit_card", 0.0) > self.flagging_threshold,
                "pii/ip_address": scores.get("pii/ip_address", 0.0) > self.flagging_threshold,
                "pii/iban": scores.get("pii/iban", 0.0) > self.flagging_threshold,
            },
            # Content moderation categories
            hate=scores.get("hate", 0.0) > self.flagging_threshold,
            harassment=scores.get("harassment", 0.0) > self.flagging_threshold,
            illicit=scores.get("illicit", 0.0) > self.flagging_threshold,
            violence=scores.get("violence", 0.0) > self.flagging_threshold,
            **{
                "hate/threatening": scores.get("hate/threatening", 0.0) > self.flagging_threshold,
                "harassment/threatening": scores.get("harassment/threatening", 0.0) > self.flagging_threshold, 
            }
        )
    
    def _scores_to_category_scores(self, scores: Dict[str, float]) -> CategoryScores:
        """Convert scores to CategoryScores model."""
        return CategoryScores(
            #  PII Categories
            **{
                "pii/phone": scores.get("pii/phone", 0.0),
                "pii/email": scores.get("pii/email", 0.0),
                "pii/credit_card": scores.get("pii/credit_card", 0.0),
                "pii/ip_address": scores.get("pii/ip_address", 0.0),
                "pii/iban": scores.get("pii/iban", 0.0),
            },
            # Content moderation categories
            hate=scores.get("hate", 0.0),
            harassment=scores.get("harassment", 0.0),
            illicit=scores.get("illicit", 0.0),
            violence=scores.get("violence", 0.0),
            **{
                "hate/threatening": scores.get("hate/threatening", 0.0),
                "harassment/threatening": scores.get("harassment/threatening", 0.0),
                "illicit/violent": scores.get("illicit/violent", 0.0),
            }
        )
    
    def _get_applied_input_types(self, categories: Categories) -> CategoryAppliedInputTypes:
        """
        Get applied input types for each category.
        Since we only support text input currently, return 'text' for flagged categories.
        """
        applied_types = CategoryAppliedInputTypes()
        
        # For now, we only support text input
        input_type = ["text"]
        
        # PII Categories - use actual field names, not aliases
        if categories.pii_phone:
            applied_types.pii_phone = input_type
        if categories.pii_email:
            applied_types.pii_email = input_type
        if categories.pii_credit_card:
            applied_types.pii_credit_card = input_type
        if categories.pii_ip_address:
            applied_types.pii_ip_address = input_type
        if categories.pii_iban:
            applied_types.pii_iban = input_type
        
        # Content moderation categories
        if categories.hate:
            applied_types.hate = input_type
        if categories.harassment:
            applied_types.harassment = input_type
        if categories.violence:
            applied_types.violence = input_type
        if categories.hate_threatening:
            applied_types.hate_threatening = input_type
        if categories.harassment_threatening:
            applied_types.harassment_threatening = input_type
            
        return applied_types
    
    def moderate_text(self, text: str) -> ModerationResult:
        """
        Moderate a single text input.
        
        Args:
            text: Text to moderate
            
        Returns:
            ModerationResult
        """
        # Get scores from regex checker
        regex_scores = self.regex_checker.check(text)
        
        # Get scores from BERT checker if available
        bert_scores = None
        if self.use_bert and self.bert_checker:
            bert_scores = self.bert_checker.check(text)
        
        # Combine scores
        combined_scores = self._combine_scores(regex_scores, bert_scores)
        
        # Convert to response format
        categories = self._scores_to_categories(combined_scores)
        category_scores = self._scores_to_category_scores(combined_scores)
        applied_input_types = self._get_applied_input_types(categories)
        
        # Check if any category is flagged
        flagged = any([
            #  PII categories
            categories.pii_phone, categories.pii_email,
            categories.pii_ip_address, categories.pii_iban,
            # Legacy categories (for compatibility)
            categories.violence, 
            categories.hate_threatening, categories.harassment_threatening,
        ])
        
        return ModerationResult(
            flagged=flagged,
            categories=categories,
            category_scores=category_scores,
            category_applied_input_types=applied_input_types
        )
    
    def moderate(self, input_data: Union[str, List[str]], model: str = "omni-moderation-latest") -> ModerationResponse:
        """
        Moderate input data (text or list of texts).
        
        Args:
            input_data: Text or list of texts to moderate
            model: Model name (for compatibility)
            
        Returns:
            ModerationResponse
        """
        # Convert single string to list
        if isinstance(input_data, str):
            texts = [input_data]
        else:
            texts = input_data
        
        # Process each text
        results = []
        for text in texts:
            result = self.moderate_text(text)
            results.append(result)
        
        # Generate response
        response_id = f"modr-{uuid.uuid4().hex}"
        
        return ModerationResponse(
            id=response_id,
            model=model,
            results=results
        )
