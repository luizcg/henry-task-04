import os
import json

from langfuse.openai import openai
from openai import APIError, APIConnectionError, RateLimitError, APITimeoutError
from pydantic import ValidationError
from dotenv import load_dotenv

from src.models import DocumentStructure, ContextualizationResult

load_dotenv()

SYSTEM_PROMPT = """You are Agent 1: Contract Contextualization Specialist.

Your role is to analyze two contract documents (an original contract and its amendment) and provide comprehensive context about their structure and relationships.

Your responsibilities:
1. Analyze the structure of both documents (sections, clauses, paragraphs)
2. Identify corresponding sections between the original and amendment
3. Note any new sections added in the amendment
4. Note any sections removed or significantly restructured
5. Provide analysis notes about the overall document relationship

You will receive the extracted text from both documents. Analyze them carefully and return a structured analysis.

Return your response in JSON format:
{
    "corresponding_sections": [
        {
            "original_section": "Section name/number from original",
            "amendment_section": "Corresponding section in amendment",
            "relationship": "modified|added|removed|unchanged"
        }
    ],
    "analysis_notes": "Your detailed analysis of how these documents relate to each other"
}

Be thorough and precise. Your analysis will be used by Agent 2 to extract specific changes."""


def run_contextualization_agent(
    original_doc: DocumentStructure,
    amendment_doc: DocumentStructure,
    trace=None,
) -> ContextualizationResult:
    """
    Agent 1: Contextualize both documents and identify corresponding sections.
    
    Args:
        original_doc: Parsed structure of the original contract
        amendment_doc: Parsed structure of the amendment
        trace: TracingContext for hierarchical tracing
    
    Returns:
        ContextualizationResult with document analysis
    """
    model = os.getenv("MODEL_NAME", "gpt-5.2")
    
    # Create generation span for LLM call if trace is available
    generation = None
    if trace:
        generation = trace.generation(
            name="agent1_llm_call",
            model=model,
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

Provide your contextual analysis identifying corresponding sections and their relationships."""

    try:
        response = openai.chat.completions.create(
            name="contextualization_agent",
            model=model,
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
            output=content[:500],  # Truncate for readability
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
