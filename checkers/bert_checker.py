from typing import Dict
try:
    import torch
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    
from checkers.regex_checker import BaseModerationChecker


class BertModerationChecker(BaseModerationChecker):
    """BERT-based moderation checker using transformers."""
    
    def __init__(self, model_name: str = "unitary/toxic-bert"):
        """
        Initialize BERT moderation checker.
        
        Args:
            model_name: HuggingFace model name for toxicity detection
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("transformers and torch are required for BertModerationChecker")
            
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        try:
            # Use a toxicity detection model
            self.classifier = pipeline(
                "text-classification",
                model=model_name,
                device=0 if self.device == "cuda" else -1,
                return_all_scores=True
            )
        except (OSError, ValueError) as e:
            # Fallback to a general sentiment model if toxic-bert is not available
            print(f"Could not load {model_name}, falling back to sentiment model: {e}")
            raise ImportError(
                "BertModerationChecker requires a valid HuggingFace model. "
                "Please install the transformers library and ensure the model is available."
            ) from e
        
        # Category mapping based on BERT toxic model outputs
        # Maps BERT labels to moderation categories
        self.category_mapping = {
            "harassment": ["toxic", "insult"],
            "harassment/threatening": ["threat"],
            "hate": ["identity_hate"],
            "hate/threatening": ["threat"],
            "violence": ["toxic", "threat", "severe_toxic"],
        }
    
    def check(self, text: str) -> Dict[str, float]:
        """Check text using BERT model and return category scores."""
        try:
            # Get predictions from the model
            results = self.classifier(text)[0]
            
            # Convert results list to a dictionary for easier lookup
            bert_scores = {result['label']: result['score'] for result in results}
            
            # Initialize scores dictionary
            scores = {}
            
            # Map BERT scores to moderation categories
            for category, bert_labels in self.category_mapping.items():
                # Get the maximum score from relevant BERT labels for this category
                # TODO: don't do mapping, just use the native BERT labels?
                category_score = max(
                    bert_scores.get(label, 0.0) for label in bert_labels
                )
                
                scores[category] = category_score
            
            return scores
            
        except (RuntimeError, ValueError, OSError) as e:
            # Return zero scores if model fails
            print(f"BERT checker error: {e}")
            return {category: 0.0 for category in self.category_mapping.keys()}
    
    def get_device_info(self) -> str:
        """Get information about the device being used."""
        return f"Using device: {self.device}"
