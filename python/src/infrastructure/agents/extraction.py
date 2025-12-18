"""Extraction agent implementation using LangChain."""
import json
from typing import Optional, Any, List

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field, ValidationError

from src.domain.interfaces import ExtractionAgent
from src.domain.models import ContextualizationResult, ContractChangeResult
from src.config.settings import settings


class ExtractionOutput(BaseModel):
    """Schema for the extraction agent output."""
    sections_changed: List[str] = Field(
        description="List of section names/identifiers that were modified"
    )
    topics_touched: List[str] = Field(
        description="List of business/legal topics affected by the changes"
    )
    summary_of_the_change: str = Field(
        description="Detailed description of what changed and its implications"
    )


SYSTEM_PROMPT = """You are Agent 2: Contract Change Extraction Specialist.

You receive the output from Agent 1 (contextualization) and must extract specific changes between the original contract and amendment.

Your output MUST contain exactly these three fields:
1. sections_changed: List of section names/identifiers that were modified
2. topics_touched: List of business/legal topics affected by the changes
3. summary_of_the_change: Detailed description of what changed and its implications

Be specific and thorough in your analysis."""


class LangChainExtractionAgent(ExtractionAgent):
    """Extraction agent using LangChain."""
    
    def __init__(self, model: Optional[str] = None):
        """Initialize the agent with LangChain components."""
        self.model_name = model or settings.model_name
        self.llm = ChatOpenAI(
            model=self.model_name,
            api_key=settings.openai_api_key,
            temperature=0,
            max_tokens=4096,
        )
        self.parser = JsonOutputParser(pydantic_object=ExtractionOutput)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT + "\n\n{format_instructions}"),
            ("human", """Using Agent 1's contextual analysis, extract the specific changes between these contracts.

## AGENT 1's SECTION MAPPING
{sections_analysis}

## AGENT 1's ANALYSIS NOTES
{analysis_notes}

## ORIGINAL CONTRACT SUMMARY
Title: {original_title}
Sections: {original_sections}

## AMENDMENT SUMMARY
Title: {amendment_title}
Sections: {amendment_sections}

---

Based on Agent 1's analysis, extract:
1. Which sections were changed
2. What topics/areas were affected
3. A detailed summary of the changes and their business/legal implications"""),
        ])
        
        self.chain = self.prompt | self.llm | self.parser
    
    def run(
        self,
        contextualization: ContextualizationResult,
        trace: Optional[Any] = None,
    ) -> ContractChangeResult:
        """Extract specific changes using Agent 1's contextualization."""
        
        # Build callbacks list for Langfuse tracing
        callbacks = []
        if trace and hasattr(trace, 'get_langchain_handler'):
            callbacks.append(trace.get_langchain_handler())
        
        config = {"callbacks": callbacks} if callbacks else {}
        
        sections_analysis = json.dumps(contextualization.corresponding_sections, indent=2)
        
        try:
            result = self.chain.invoke(
                {
                    "sections_analysis": sections_analysis,
                    "analysis_notes": contextualization.analysis_notes,
                    "original_title": contextualization.original_structure.title,
                    "original_sections": ', '.join(contextualization.original_structure.sections),
                    "amendment_title": contextualization.amendment_structure.title,
                    "amendment_sections": ', '.join(contextualization.amendment_structure.sections),
                    "format_instructions": self.parser.get_format_instructions(),
                },
                config=config,
            )
        except Exception as e:
            raise RuntimeError(f"LangChain agent error: {e}")
        
        try:
            return ContractChangeResult(
                sections_changed=result.get("sections_changed", []) or ["General"],
                topics_touched=result.get("topics_touched", []) or ["Contract Terms"],
                summary_of_the_change=result.get("summary_of_the_change", "Changes detected between contracts."),
            )
        except ValidationError as e:
            raise ValueError(f"Invalid extraction result: {e}")


# Alias for backward compatibility
OpenAIExtractionAgent = LangChainExtractionAgent
