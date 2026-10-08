from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class LLMExtractorInterface(ABC):
    """
    Abstract interface for LLM-based fallback extraction.
    Allows testing without live network calls.
    """
    
    @abstractmethod
    def extract_structured_json(
        self, 
        prompt: str, 
        schema: Dict[str, Any],
        raw_text: str
    ) -> Dict[str, Any]:
        """
        Executes a schema-constrained structured extraction call.
        """
        pass


class MockLLMExtractor(LLMExtractorInterface):
    """Deterministic mock extractor for unit tests and offline testing."""
    
    def __init__(self, predefined_responses: Optional[Dict[str, Any]] = None):
        self.predefined_responses = predefined_responses or {}

    def extract_structured_json(
        self, 
        prompt: str, 
        schema: Dict[str, Any],
        raw_text: str
    ) -> Dict[str, Any]:
        for key, res in self.predefined_responses.items():
            if key in prompt or key in raw_text:
                return res
        return {}
