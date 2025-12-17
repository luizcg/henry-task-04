"""OpenAI Vision parser implementation."""
import os
import json
from typing import Optional, Any

from openai import OpenAI
from openai import APIError, APIConnectionError, RateLimitError, APITimeoutError
from pydantic import ValidationError

from src.domain.interfaces import ImageParserStrategy
from src.domain.models import DocumentStructure
from src.infrastructure.parsers.base import encode_image_base64, get_image_media_type
from src.config.settings import settings


class OpenAIVisionParser(ImageParserStrategy):
    """Image parser using OpenAI GPT Vision models."""
    
    def __init__(self, model: Optional[str] = None):
        """
        Initialize the parser.
        
        Args:
            model: Model name (defaults to settings.model_name)
        """
        self.model = model or settings.model_name
        self.client = OpenAI(api_key=settings.openai_api_key)
    
    def parse(
        self,
        image_path: str,
        document_type: str,
        trace: Optional[Any] = None,
    ) -> DocumentStructure:
        """Parse a contract image using OpenAI Vision."""
        
        # Create generation span for LLM call if trace is available
        generation = None
        if trace:
            generation = trace.generation(
                name=f"parse_{document_type}_llm_call",
                model=self.model,
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
            response = self.client.chat.completions.create(
                model=self.model,
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
