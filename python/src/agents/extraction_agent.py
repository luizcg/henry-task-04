import os
import json

from langfuse.openai import openai
from openai import APIError, APIConnectionError, RateLimitError, APITimeoutError
from pydantic import ValidationError
from dotenv import load_dotenv

from src.models import ContextualizationResult, ContractChangeResult

load_dotenv()

SYSTEM_PROMPT = """You are Agent 2: Contract Change Extraction Specialist.

Your role is to extract specific changes between an original contract and its amendment, using the contextual analysis provided by Agent 1.

You will receive:
1. The full text of both documents
2. Agent 1's analysis of corresponding sections
3. Agent 1's notes about the document relationship

Your task:
1. Identify ALL sections that were changed (added, modified, or removed)
2. Identify ALL topics/subjects touched by the changes
3. Write a comprehensive summary of what changed

Return your response in JSON format:
{
    "sections_changed": ["List of specific section names/numbers that changed"],
    "topics_touched": ["List of topics/subjects affected by changes"],
    "summary_of_the_change": "A detailed summary (minimum 50 words) explaining what changed, why it matters, and the impact"
}

Be specific and thorough. Your output will be used by legal professionals to understand contract amendments."""


def run_extraction_agent(
    contextualization: ContextualizationResult,
    trace=None,
) -> ContractChangeResult:
    """
    Agent 2: Extract specific changes using Agent 1's contextualization.
    
    Args:
        contextualization: Output from Agent 1 with document analysis
        trace: TracingContext for hierarchical tracing
    
    Returns:
        ContractChangeResult with extracted changes
    """
    model = os.getenv("MODEL_NAME", "gpt-5.2")
    
    # Create generation span for LLM call if trace is available
    generation = None
    if trace:
        generation = trace.generation(
            name="agent2_llm_call",
            model=model,
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

## ORIGINAL CONTRACT
Title: {contextualization.original_structure.title}

Full Text:
{contextualization.original_structure.full_text}

---

## AMENDMENT
Title: {contextualization.amendment_structure.title}

Full Text:
{contextualization.amendment_structure.full_text}

---

Extract all changes: sections modified, topics affected, and provide a comprehensive summary."""

    try:
        response = openai.chat.completions.create(
            name="extraction_agent",
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
        raise ValueError(f"Failed to parse Agent 2 response as JSON: {e}")
    
    try:
        return ContractChangeResult(
            sections_changed=parsed.get("sections_changed", []) or ["General"],
            topics_touched=parsed.get("topics_touched", []) or ["Contract Terms"],
            summary_of_the_change=parsed.get("summary_of_the_change", "Changes detected between contracts."),
        )
    except ValidationError as e:
        raise ValueError(f"Invalid extraction result: {e}")
