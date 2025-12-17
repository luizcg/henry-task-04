"""Contextualization agent implementation."""
import os
import json
from typing import Optional, Any

from openai import OpenAI
from openai import APIError, APIConnectionError, RateLimitError, APITimeoutError
from pydantic import ValidationError

from src.domain.interfaces import ContextualizationAgent
from src.domain.models import DocumentStructure, ContextualizationResult
from src.config.settings import settings


SYSTEM_PROMPT = """You are Agent 1: Contract Contextualization Specialist.

Your role is to analyze two contract documents (original and amendment) and create a comprehensive mapping between them.

Tasks:
1. Identify the structure of both documents
2. Map corresponding sections between original and amendment
3. Note any new sections added or sections removed
4. Provide analysis notes about the relationship between documents

Return your response in JSON format:
{
    "corresponding_sections": [
        {
            "original_section": "Section name in original",
            "amendment_section": "Corresponding section in amendment",
            "status": "modified|added|removed|unchanged"
        }
    ],
    "analysis_notes": "Detailed notes about the document structure and changes"
}

Be thorough and precise. Your analysis will be used by Agent 2 to extract specific changes."""


class OpenAIContextualizationAgent(ContextualizationAgent):
    """Contextualization agent using OpenAI."""
    
    def __init__(self, model: Optional[str] = None):
        """Initialize the agent."""
        self.model = model or settings.model_name
        self.client = OpenAI(api_key=settings.openai_api_key)
    
    def run(
        self,
        original_doc: DocumentStructure,
        amendment_doc: DocumentStructure,
        trace: Optional[Any] = None,
    ) -> ContextualizationResult:
        """Contextualize both documents and identify corresponding sections."""
        
        # Create generation span for LLM call if trace is available
        generation = None
        if trace:
            generation = trace.generation(
                name="agent1_llm_call",
                model=self.model,
                input_data={
                    "original_title": original_doc.title,
                    "amendment_title": amendment_doc.title,
                },
                metadata={"agent": "contextualization"},
            )
        
        user_message = f"""Analyze these two contract documents:

## ORIGINAL CONTRACT
Title: {original_doc.title}
Sections: {', '.join(original_doc.sections)}

Full Text:
{original_doc.full_text}

---

## AMENDMENT
Title: {amendment_doc.title}
Sections: {', '.join(amendment_doc.sections)}

Full Text:
{amendment_doc.full_text}

---

Please analyze the structure of both documents and identify corresponding sections."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                response_format={"type": "json_object"},
                max_completion_tokens=4096,
            )
        except RateLimitError as e:
            raise RuntimeError(f"OpenAI rate limit exceeded: {e}")
        except APITimeoutError as e:
            raise RuntimeError(f"OpenAI API timeout: {e}")
        except APIConnectionError as e:
            raise RuntimeError(f"Failed to connect to OpenAI API: {e}")
        except APIError as e:
            raise RuntimeError(f"OpenAI API error: {e}")
        
        content = response.choices[0].message.content
        
        # End generation span with output and usage
        if generation:
            generation.update(
                output=content[:500],
                usage_details={
                    "input": response.usage.prompt_tokens,
                    "output": response.usage.completion_tokens,
                },
            )
            generation.end()
        
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse Agent 1 response as JSON: {e}")
        
        try:
            return ContextualizationResult(
                original_structure=original_doc,
                amendment_structure=amendment_doc,
                corresponding_sections=parsed.get("corresponding_sections", []),
                analysis_notes=parsed.get("analysis_notes", ""),
            )
        except ValidationError as e:
            raise ValueError(f"Invalid contextualization result: {e}")
