"""Extraction agent implementation."""
import os
import json
from typing import Optional, Any

from openai import OpenAI
from openai import APIError, APIConnectionError, RateLimitError, APITimeoutError
from pydantic import ValidationError

from src.domain.interfaces import ExtractionAgent
from src.domain.models import ContextualizationResult, ContractChangeResult
from src.config.settings import settings


SYSTEM_PROMPT = """You are Agent 2: Contract Change Extraction Specialist.

You receive the output from Agent 1 (contextualization) and must extract specific changes between the original contract and amendment.

Your output MUST be a JSON object with exactly these three fields:
1. sections_changed: List of section names/identifiers that were modified
2. topics_touched: List of business/legal topics affected by the changes
3. summary_of_the_change: Detailed description of what changed and its implications

Return your response in this exact JSON format:
{
    "sections_changed": ["Section 1", "Section 2", ...],
    "topics_touched": ["Compensation", "Termination", ...],
    "summary_of_the_change": "Detailed description of the changes..."
}

Be specific and thorough in your analysis."""


class OpenAIExtractionAgent(ExtractionAgent):
    """Extraction agent using OpenAI."""
    
    def __init__(self, model: Optional[str] = None):
        """Initialize the agent."""
        self.model = model or settings.model_name
        self.client = OpenAI(api_key=settings.openai_api_key)
    
    def run(
        self,
        contextualization: ContextualizationResult,
        trace: Optional[Any] = None,
    ) -> ContractChangeResult:
        """Extract specific changes using Agent 1's contextualization."""
        
        # Create generation span for LLM call if trace is available
        generation = None
        if trace:
            generation = trace.generation(
                name="agent2_llm_call",
                model=self.model,
                input_data={
                    "corresponding_sections_count": len(contextualization.corresponding_sections),
                },
                metadata={"agent": "extraction"},
            )
        
        sections_analysis = json.dumps(contextualization.corresponding_sections, indent=2)
        
        user_message = f"""Using Agent 1's contextual analysis, extract the specific changes between these contracts.

## AGENT 1's SECTION MAPPING
{sections_analysis}

## AGENT 1's ANALYSIS NOTES
{contextualization.analysis_notes}

## ORIGINAL CONTRACT SUMMARY
Title: {contextualization.original_structure.title}
Sections: {', '.join(contextualization.original_structure.sections)}

## AMENDMENT SUMMARY
Title: {contextualization.amendment_structure.title}
Sections: {', '.join(contextualization.amendment_structure.sections)}

---

Based on Agent 1's analysis, extract:
1. Which sections were changed
2. What topics/areas were affected
3. A detailed summary of the changes and their business/legal implications"""

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
            raise ValueError(f"Failed to parse Agent 2 response as JSON: {e}")
        
        try:
            return ContractChangeResult(
                sections_changed=parsed.get("sections_changed", []) or ["General"],
                topics_touched=parsed.get("topics_touched", []) or ["Contract Terms"],
                summary_of_the_change=parsed.get("summary_of_the_change", "Changes detected between contracts."),
            )
        except ValidationError as e:
            raise ValueError(f"Invalid extraction result: {e}")
