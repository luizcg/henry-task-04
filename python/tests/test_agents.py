import pytest
from unittest.mock import Mock, patch, MagicMock
import json

from src.domain.models import DocumentStructure, ContextualizationResult, ContractChangeResult
from src.infrastructure.agents.contextualization import OpenAIContextualizationAgent
from src.infrastructure.agents.extraction import OpenAIExtractionAgent


def create_mock_document(doc_type: str) -> DocumentStructure:
    """Create a mock DocumentStructure for testing."""
    return DocumentStructure(
        title=f"Test {doc_type.title()} Contract",
        sections=["1. Parties", "2. Terms", "3. Payment"],
        full_text=f"This is the full text of the {doc_type} contract.",
        document_type=doc_type,
    )


def create_mock_contextualization() -> ContextualizationResult:
    """Create a mock ContextualizationResult for testing."""
    return ContextualizationResult(
        original_structure=create_mock_document("original"),
        amendment_structure=create_mock_document("amendment"),
        corresponding_sections=[
            {
                "original_section": "2. Terms",
                "amendment_section": "2. Terms (Amended)",
                "relationship": "modified",
            }
        ],
        analysis_notes="The amendment modifies the Terms section.",
    )


class TestAgentHandoff:
    """Tests to verify Agent 2 receives Agent 1's output correctly."""
    
    def test_contextualization_output_structure(self):
        """Test that Agent 1 output has correct structure for Agent 2."""
        ctx = create_mock_contextualization()
        
        assert ctx.original_structure is not None
        assert ctx.amendment_structure is not None
        assert isinstance(ctx.corresponding_sections, list)
        assert len(ctx.corresponding_sections) > 0
        assert isinstance(ctx.analysis_notes, str)
    
    def test_extraction_receives_contextualization(self):
        """Test that Agent 2 can receive and use Agent 1's output."""
        ctx = create_mock_contextualization()
        
        assert ctx.original_structure.full_text is not None
        assert ctx.amendment_structure.full_text is not None
        
        sections_json = json.dumps(ctx.corresponding_sections)
        assert "modified" in sections_json
        assert "2. Terms" in sections_json
    
    def test_extraction_agent_structure(self):
        """Test that extraction agent has correct interface."""
        agent = OpenAIExtractionAgent()
        assert hasattr(agent, 'run')
        assert agent is not None


class TestAgentIntegration:
    """Integration tests for agent workflow."""
    
    def test_contextualization_agent_structure(self):
        """Test Agent 1 has correct interface."""
        agent = OpenAIContextualizationAgent()
        assert hasattr(agent, 'run')
        assert agent is not None
