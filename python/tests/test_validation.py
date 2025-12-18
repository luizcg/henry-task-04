import pytest
from pydantic import ValidationError

from src.domain.models import (
    ContractChangeResult,
    DocumentStructure,
    ContextualizationResult,
    ProcessingResult,
)


class TestContractChangeResult:
    """Tests for ContractChangeResult Pydantic model validation."""
    
    def test_valid_result(self):
        """Test that valid data passes validation."""
        data = {
            "sections_changed": ["Section 1", "Section 3.2"],
            "topics_touched": ["Payment Terms", "Liability"],
            "summary_of_the_change": (
                "The amendment modifies the payment terms in Section 1, changing the "
                "due date from 30 days to 45 days. Additionally, Section 3.2 updates "
                "the liability cap from $100,000 to $250,000."
            ),
        }
        result = ContractChangeResult.model_validate(data)
        
        assert result.sections_changed == ["Section 1", "Section 3.2"]
        assert result.topics_touched == ["Payment Terms", "Liability"]
        assert len(result.summary_of_the_change) >= 50
    
    def test_empty_sections_changed_fails(self):
        """Test that empty sections_changed list fails validation."""
        data = {
            "sections_changed": [],
            "topics_touched": ["Payment Terms"],
            "summary_of_the_change": "A" * 50,
        }
        with pytest.raises(ValidationError) as exc_info:
            ContractChangeResult.model_validate(data)
        
        assert "sections_changed" in str(exc_info.value)
    
    def test_empty_topics_touched_fails(self):
        """Test that empty topics_touched list fails validation."""
        data = {
            "sections_changed": ["Section 1"],
            "topics_touched": [],
            "summary_of_the_change": "A" * 50,
        }
        with pytest.raises(ValidationError) as exc_info:
            ContractChangeResult.model_validate(data)
        
        assert "topics_touched" in str(exc_info.value)
    
    def test_short_summary_fails(self):
        """Test that summary shorter than 50 chars fails validation."""
        data = {
            "sections_changed": ["Section 1"],
            "topics_touched": ["Payment"],
            "summary_of_the_change": "Too short",
        }
        with pytest.raises(ValidationError) as exc_info:
            ContractChangeResult.model_validate(data)
        
        assert "summary_of_the_change" in str(exc_info.value)
    
    def test_missing_required_field_fails(self):
        """Test that missing required fields fail validation."""
        data = {
            "sections_changed": ["Section 1"],
            "topics_touched": ["Payment"],
        }
        with pytest.raises(ValidationError):
            ContractChangeResult.model_validate(data)


class TestDocumentStructure:
    """Tests for DocumentStructure Pydantic model."""
    
    def test_valid_structure(self):
        """Test valid document structure."""
        data = {
            "title": "Employment Agreement",
            "sections": ["1. Parties", "2. Terms", "3. Compensation"],
            "full_text": "This is a sample contract text with more content.",
            "document_type": "original",
        }
        doc = DocumentStructure.model_validate(data)
        
        assert doc.title == "Employment Agreement"
        assert len(doc.sections) == 3
        assert doc.document_type == "original"
    
    def test_empty_title_fails(self):
        """Test that empty title fails validation."""
        data = {
            "title": "",
            "sections": ["Section 1"],
            "full_text": "Sample text content here",
            "document_type": "original",
        }
        with pytest.raises(ValidationError):
            DocumentStructure.model_validate(data)
    
    def test_empty_sections_fails(self):
        """Test that empty sections list fails validation."""
        data = {
            "title": "Contract",
            "sections": [],
            "full_text": "Sample text content here",
            "document_type": "original",
        }
        with pytest.raises(ValidationError):
            DocumentStructure.model_validate(data)


class TestProcessingResult:
    """Tests for ProcessingResult model."""
    
    def test_success_result(self):
        """Test successful processing result."""
        data = {
            "contract_id": "test-123",
            "status": "success",
            "result": {
                "sections_changed": ["Section 1"],
                "topics_touched": ["Terms"],
                "summary_of_the_change": "A" * 50,
            },
            "error": None,
            "trace_id": "trace-456",
        }
        result = ProcessingResult.model_validate(data)
        
        assert result.status == "success"
        assert result.result is not None
        assert result.error is None
    
    def test_error_result(self):
        """Test error processing result."""
        data = {
            "contract_id": "test-123",
            "status": "error",
            "result": None,
            "error": "Failed to parse image",
            "trace_id": "trace-456",
        }
        result = ProcessingResult.model_validate(data)
        
        assert result.status == "error"
        assert result.result is None
        assert result.error == "Failed to parse image"
    
    def test_invalid_status_fails(self):
        """Test that invalid status fails validation."""
        data = {
            "contract_id": "test-123",
            "status": "pending",
            "result": None,
            "error": None,
        }
        with pytest.raises(ValidationError):
            ProcessingResult.model_validate(data)
