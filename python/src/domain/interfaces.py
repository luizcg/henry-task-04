"""Abstract base classes and interfaces for the domain layer."""
from abc import ABC, abstractmethod
from typing import Optional, Any

from src.domain.models import (
    DocumentStructure,
    ContextualizationResult,
    ContractChangeResult,
)


class ImageParserStrategy(ABC):
    """Abstract interface for image parsing strategies."""
    
    @abstractmethod
    def parse(
        self,
        image_path: str,
        document_type: str,
        trace: Optional[Any] = None,
    ) -> DocumentStructure:
        """
        Parse a contract image and extract its structure.
        
        Args:
            image_path: Path to the contract image
            document_type: Either 'original' or 'amendment'
            trace: Optional tracing context
        
        Returns:
            DocumentStructure with extracted text and structure
        """
        pass


class ContextualizationAgent(ABC):
    """Abstract interface for contextualization agent."""
    
    @abstractmethod
    def run(
        self,
        original_doc: DocumentStructure,
        amendment_doc: DocumentStructure,
        trace: Optional[Any] = None,
    ) -> ContextualizationResult:
        """
        Contextualize both documents and identify corresponding sections.
        
        Args:
            original_doc: Parsed structure of the original contract
            amendment_doc: Parsed structure of the amendment
            trace: Optional tracing context
        
        Returns:
            ContextualizationResult with document analysis
        """
        pass


class ExtractionAgent(ABC):
    """Abstract interface for extraction agent."""
    
    @abstractmethod
    def run(
        self,
        contextualization: ContextualizationResult,
        trace: Optional[Any] = None,
    ) -> ContractChangeResult:
        """
        Extract specific changes using contextualization.
        
        Args:
            contextualization: Output from contextualization agent
            trace: Optional tracing context
        
        Returns:
            ContractChangeResult with extracted changes
        """
        pass


class ContractRepository(ABC):
    """Abstract interface for contract storage."""
    
    @abstractmethod
    def get_image(self, path_or_url: str) -> bytes:
        """
        Retrieve image bytes from storage.
        
        Args:
            path_or_url: Path or URL to the image
        
        Returns:
            Image bytes
        """
        pass
    
    @abstractmethod
    def save_result(self, contract_id: str, result: Any) -> None:
        """
        Save processing result to storage.
        
        Args:
            contract_id: Contract identifier
            result: Processing result to save
        """
        pass
