import pytest
from unittest.mock import Mock, patch, MagicMock
import json

from src.models import DocumentStructure, ContextualizationResult, ContractChangeResult
from src.agents.contextualization_agent import run_contextualization_agent
from src.agents.extraction_agent import run_extraction_agent


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
    
    @patch("src.agents.extraction_agent.openai")
    def test_extraction_agent_uses_contextualization(self, mock_openai):
        """Test that extraction agent properly uses contextualization data."""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content=json.dumps({
                        "sections_changed": ["2. Terms"],
                        "topics_touched": ["Contract Duration", "Renewal Terms"],
                        "summary_of_the_change": (
                            "The amendment modifies Section 2 (Terms) to extend the contract "
                            "duration from 12 months to 24 months and adds automatic renewal "
                            "provisions. This significantly impacts the long-term commitment."
                        ),
                    })
                )
            )
        ]
        mock_response.usage = MagicMock(prompt_tokens=100, completion_tokens=50)
        
        mock_openai.chat.completions.create.return_value = mock_response
        
        ctx = create_mock_contextualization()
        result = run_extraction_agent(ctx, trace=None)
        
        assert isinstance(result, ContractChangeResult)
        assert "2. Terms" in result.sections_changed
        assert len(result.topics_touched) > 0
        assert len(result.summary_of_the_change) >= 50
        
        call_args = mock_openai.chat.completions.create.call_args
        messages = call_args.kwargs["messages"]
        user_message = messages[1]["content"]
        
        assert "AGENT 1" in user_message
        assert ctx.analysis_notes in user_message


class TestAgentIntegration:
    """Integration tests for agent workflow."""
    
    @patch("src.agents.contextualization_agent.openai")
    def test_contextualization_agent_output(self, mock_openai):
        """Test Agent 1 produces valid output."""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content=json.dumps({
                        "corresponding_sections": [
                            {
                                "original_section": "3. Payment",
                                "amendment_section": "3. Payment Terms",
                                "relationship": "modified",
                            }
                        ],
                        "analysis_notes": "Payment section was renamed and modified.",
                    })
                )
            )
        ]
        mock_response.usage = MagicMock(prompt_tokens=200, completion_tokens=100)
        
        mock_openai.chat.completions.create.return_value = mock_response
        
        original = create_mock_document("original")
        amendment = create_mock_document("amendment")
        
        result = run_contextualization_agent(original, amendment, trace=None)
        
        assert isinstance(result, ContextualizationResult)
        assert result.original_structure == original
        assert result.amendment_structure == amendment
        assert len(result.corresponding_sections) > 0
