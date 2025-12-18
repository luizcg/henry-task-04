"""OpenAI Vision parser implementation using LangChain."""
from typing import Optional, Any, List

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field, ValidationError

from src.domain.interfaces import ImageParserStrategy
from src.domain.models import DocumentStructure
from src.infrastructure.parsers.base import encode_image_base64, get_image_media_type
from src.config.settings import settings


class DocumentParserOutput(BaseModel):
    """Schema for the document parser output."""
    title: str = Field(description="Document title")
    sections: List[str] = Field(description="List of section headers/titles")
    full_text: str = Field(description="Complete extracted text with preserved structure")


SYSTEM_PROMPT = """You are a legal document parser. Extract the complete text and structure from the provided contract image.

Your task:
1. Extract ALL text from the document, preserving the hierarchy and structure
2. Identify all section headers/titles
3. Identify the document title
4. Maintain the original formatting as much as possible

Be thorough and accurate. Do not summarize - extract the complete text."""


class LangChainVisionParser(ImageParserStrategy):
    """Image parser using LangChain with OpenAI GPT Vision models."""
    
    def __init__(self, model: Optional[str] = None):
        """Initialize the parser with LangChain components."""
        self.model_name = model or settings.model_name
        self.llm = ChatOpenAI(
            model=self.model_name,
            api_key=settings.openai_api_key,
            temperature=0,
            max_tokens=4096,
        )
        self.parser = JsonOutputParser(pydantic_object=DocumentParserOutput)
    
    def parse(
        self,
        image_path: str,
        document_type: str,
        trace: Optional[Any] = None,
    ) -> DocumentStructure:
        """Parse a contract image using LangChain with OpenAI Vision."""
        
        # Build callbacks list for Langfuse tracing
        callbacks = []
        if trace and hasattr(trace, 'get_langchain_handler'):
            callbacks.append(trace.get_langchain_handler())
        
        config = {"callbacks": callbacks} if callbacks else {}
        
        base64_image = encode_image_base64(image_path)
        media_type = get_image_media_type(image_path)
        
        # Build messages with image content
        system_message = SystemMessage(
            content=SYSTEM_PROMPT + "\n\n" + self.parser.get_format_instructions()
        )
        
        human_message = HumanMessage(
            content=[
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
            ]
        )
        
        try:
            response = self.llm.invoke(
                [system_message, human_message],
                config=config,
            )
            result = self.parser.parse(response.content)
        except Exception as e:
            raise RuntimeError(f"LangChain Vision parser error: {e}")
        
        try:
            return DocumentStructure(
                title=result.get("title", "Unknown"),
                sections=result.get("sections", []) or ["General"],
                full_text=result.get("full_text", ""),
                document_type=document_type,
            )
        except ValidationError as e:
            raise ValueError(f"Invalid document structure from LLM: {e}")


# Alias for backward compatibility
OpenAIVisionParser = LangChainVisionParser
