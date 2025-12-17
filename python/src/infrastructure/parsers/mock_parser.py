"""Mock parser for testing."""
from typing import Optional, Any

from src.domain.interfaces import ImageParserStrategy
from src.domain.models import DocumentStructure


class MockParser(ImageParserStrategy):
    """Mock parser for unit tests - returns predefined data."""
    
    def parse(
        self,
        image_path: str,
        document_type: str,
        trace: Optional[Any] = None,
    ) -> DocumentStructure:
        """Return mock document structure."""
        return DocumentStructure(
            title=f"Mock {document_type.title()} Contract",
            sections=["Section 1", "Section 2", "Section 3"],
            full_text=f"This is a mock {document_type} contract for testing purposes.",
            document_type=document_type,
        )
