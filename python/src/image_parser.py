import base64
import os
import json
from pathlib import Path

from langfuse.openai import openai
from openai import APIError, APIConnectionError, RateLimitError, APITimeoutError
from pydantic import ValidationError
from dotenv import load_dotenv

from src.models import DocumentStructure

load_dotenv()

SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_IMAGE_SIZE_MB = 20


def validate_image(image_path: str) -> Path:
    """Validate image file exists and has supported format."""
    path = Path(image_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    if path.suffix.lower() not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported image format: {path.suffix}. Supported: {SUPPORTED_FORMATS}")
    
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > MAX_IMAGE_SIZE_MB:
        raise ValueError(f"Image too large: {size_mb:.1f}MB. Max: {MAX_IMAGE_SIZE_MB}MB")
    
    return path


def encode_image_base64(image_path: str) -> str:
    """Encode image to base64 string."""
    path = validate_image(image_path)
    
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def get_image_media_type(image_path: str) -> str:
    """Get media type from image extension."""
    ext = Path(image_path).suffix.lower()
    media_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    return media_types.get(ext, "image/jpeg")


def parse_contract_image(
    image_path: str,
    document_type: str,
    trace=None,
) -> DocumentStructure:
    """
    Parse a contract image using multimodal LLM.
    
    Args:
        image_path: Path to the contract image
        document_type: Either 'original' or 'amendment'
        trace: TracingContext for hierarchical tracing
    
    Returns:
        DocumentStructure with extracted text and structure
    """
    model = os.getenv("MODEL_NAME", "gpt-5.2")
    
    # Create generation span for LLM call if trace is available
    generation = None
    if trace:
        generation = trace.generation(
            name=f"parse_{document_type}_llm_call",
            model=model,
            input_data={"image_path": image_path, "document_type": document_type},
            metadata={"step": "image_parsing"},
        )
    
    base64_image = encode_image_base64(image_path)
    media_type = get_image_media_type(image_path)
    
    system_prompt = """You are a legal document parser. Extract the complete text and structure from the provided contract image.

Your task:
1. Extract ALL text from the document, preserving the hierarchy and structure
2. Identify all section headers/titles
3. Identify the document title
4. Maintain the original formatting as much as possible

Return your response in the following JSON format:
{
    "title": "Document title",
    "sections": ["Section 1 Title", "Section 2 Title", ...],
    "full_text": "Complete extracted text with preserved structure"
}

Be thorough and accurate. Do not summarize - extract the complete text."""

    try:
        response = openai.chat.completions.create(
            name=f"parse_{document_type}_contract",
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Parse this {document_type} contract document. Extract all text and identify the structure.",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{base64_image}",
                                "detail": "high",
                            },
                        },
                    ],
                },
            ],
            response_format={"type": "json_object"},
            max_completion_tokens=4096,
            metadata={"document_type": document_type, "image_path": image_path},
        )
    except RateLimitError as e:
        raise RuntimeError(f"OpenAI rate limit exceeded. Please wait and retry. Details: {e}")
    except APITimeoutError as e:
        raise RuntimeError(f"OpenAI API timeout. The image may be too large. Details: {e}")
    except APIConnectionError as e:
        raise RuntimeError(f"Failed to connect to OpenAI API. Check your network. Details: {e}")
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
        raise ValueError(f"Failed to parse LLM response as JSON: {e}")
    
    try:
        return DocumentStructure(
            title=parsed.get("title", "Unknown"),
            sections=parsed.get("sections", []) or ["General"],
            full_text=parsed.get("full_text", ""),
            document_type=document_type,
        )
    except ValidationError as e:
        raise ValueError(f"Invalid document structure from LLM: {e}")
