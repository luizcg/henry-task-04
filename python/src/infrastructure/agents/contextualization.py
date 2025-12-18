"""Contextualization agent implementation using LangChain."""
from typing import Optional, Any, List

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field, ValidationError

from src.domain.interfaces import ContextualizationAgent
from src.domain.models import DocumentStructure, ContextualizationResult
from src.config.settings import settings


class SectionMapping(BaseModel):
    """Schema for a single section mapping."""
    original_section: str = Field(description="Section name in the original contract")
    amendment_section: str = Field(description="Corresponding section in the amendment")
    status: str = Field(description="Status: modified, added, removed, or unchanged")


class ContextualizationOutput(BaseModel):
    """Schema for the contextualization agent output."""
    corresponding_sections: List[SectionMapping] = Field(
        description="List of section mappings between original and amendment"
    )
    analysis_notes: str = Field(
        description="Detailed notes about the document structure and changes"
    )


SYSTEM_PROMPT = """You are Agent 1: Contract Contextualization Specialist.

Your role is to analyze two contract documents (original and amendment) and create a comprehensive mapping between them.

Tasks:
1. Identify the structure of both documents
2. Map corresponding sections between original and amendment
3. Note any new sections added or sections removed
4. Provide analysis notes about the relationship between documents

Be thorough and precise. Your analysis will be used by Agent 2 to extract specific changes."""


class LangChainContextualizationAgent(ContextualizationAgent):
    """Contextualization agent using LangChain."""
    
    def __init__(self, model: Optional[str] = None):
        """Initialize the agent with LangChain components."""
        self.model_name = model or settings.model_name
        self.llm = ChatOpenAI(
            model=self.model_name,
            api_key=settings.openai_api_key,
            temperature=0,
            max_tokens=4096,
        )
        self.parser = JsonOutputParser(pydantic_object=ContextualizationOutput)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT + "\n\n{format_instructions}"),
            ("human", """Analyze these two contract documents:

## ORIGINAL CONTRACT
Title: {original_title}
Sections: {original_sections}

Full Text:
{original_text}

---

## AMENDMENT
Title: {amendment_title}
Sections: {amendment_sections}

Full Text:
{amendment_text}

---

Please analyze the structure of both documents and identify corresponding sections."""),
        ])
        
        self.chain = self.prompt | self.llm | self.parser
    
    def run(
        self,
        original_doc: DocumentStructure,
        amendment_doc: DocumentStructure,
        trace: Optional[Any] = None,
    ) -> ContextualizationResult:
        """Contextualize both documents and identify corresponding sections."""
        
        # Build callbacks list for Langfuse tracing
        callbacks = []
        if trace and hasattr(trace, 'get_langchain_handler'):
            callbacks.append(trace.get_langchain_handler())
        
        config = {"callbacks": callbacks} if callbacks else {}
        
        try:
            result = self.chain.invoke(
                {
                    "original_title": original_doc.title,
                    "original_sections": ', '.join(original_doc.sections),
                    "original_text": original_doc.full_text,
                    "amendment_title": amendment_doc.title,
                    "amendment_sections": ', '.join(amendment_doc.sections),
                    "amendment_text": amendment_doc.full_text,
                    "format_instructions": self.parser.get_format_instructions(),
                },
                config=config,
            )
        except Exception as e:
            raise RuntimeError(f"LangChain agent error: {e}")
        
        # Convert to list of dicts for compatibility
        corresponding_sections = [
            {
                "original_section": s.get("original_section", "") if isinstance(s, dict) else s.original_section,
                "amendment_section": s.get("amendment_section", "") if isinstance(s, dict) else s.amendment_section,
                "status": s.get("status", "modified") if isinstance(s, dict) else s.status,
            }
            for s in result.get("corresponding_sections", [])
        ]
        
        try:
            return ContextualizationResult(
                original_structure=original_doc,
                amendment_structure=amendment_doc,
                corresponding_sections=corresponding_sections,
                analysis_notes=result.get("analysis_notes", ""),
            )
        except ValidationError as e:
            raise ValueError(f"Invalid contextualization result: {e}")


# Alias for backward compatibility
OpenAIContextualizationAgent = LangChainContextualizationAgent
