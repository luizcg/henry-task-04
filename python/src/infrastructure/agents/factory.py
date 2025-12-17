"""Factory for creating agent instances."""
from src.domain.interfaces import ContextualizationAgent, ExtractionAgent
from src.infrastructure.agents.contextualization import OpenAIContextualizationAgent
from src.infrastructure.agents.extraction import OpenAIExtractionAgent
from src.config.settings import settings


class AgentFactory:
    """Factory for creating agent instances."""
    
    @staticmethod
    def create_contextualization_agent() -> ContextualizationAgent:
        """Create a contextualization agent instance."""
        return OpenAIContextualizationAgent(model=settings.model_name)
    
    @staticmethod
    def create_extraction_agent() -> ExtractionAgent:
        """Create an extraction agent instance."""
        return OpenAIExtractionAgent(model=settings.model_name)
