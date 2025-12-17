"""Factory for creating parser instances."""
from src.domain.interfaces import ImageParserStrategy
from src.infrastructure.parsers.openai_parser import OpenAIVisionParser
from src.infrastructure.parsers.mock_parser import MockParser
from src.config.settings import settings


class ParserFactory:
    """Factory for creating image parser instances."""
    
    @staticmethod
    def create(parser_type: str = None) -> ImageParserStrategy:
        """
        Create a parser instance based on type.
        
        Args:
            parser_type: Type of parser ('openai', 'mock'). 
                        Defaults to settings.parser_type.
        
        Returns:
            ImageParserStrategy implementation
        """
        parser_type = parser_type or settings.parser_type
        
        if parser_type == "openai":
            return OpenAIVisionParser(model=settings.model_name)
        elif parser_type == "mock":
            return MockParser()
        else:
            raise ValueError(f"Unknown parser type: {parser_type}")
