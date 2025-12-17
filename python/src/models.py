from pydantic import BaseModel, Field
from typing import List


class DocumentStructure(BaseModel):
    """Structure extracted from a contract document by the vision model."""
    
    title: str = Field(..., min_length=1, description="Document title")
    sections: List[str] = Field(..., min_length=1, description="List of section titles/headers")
    full_text: str = Field(..., min_length=10, description="Full extracted text from the document")
    document_type: str = Field(..., description="Type: 'original' or 'amendment'")


class ContextualizationResult(BaseModel):
    """Output from Agent 1 - Contextualization Agent."""
    
    original_structure: DocumentStructure = Field(..., description="Structure of the original contract")
    amendment_structure: DocumentStructure = Field(..., description="Structure of the amendment")
    corresponding_sections: List[dict] = Field(
        ..., 
        description="Mapping of sections between original and amendment"
    )
    analysis_notes: str = Field(..., description="Agent's analysis notes about the documents")


class ContractChangeResult(BaseModel):
    """Final output - validated result of contract comparison."""
    
    sections_changed: List[str] = Field(
        ..., 
        min_length=1,
        description="List of section names/numbers that were modified"
    )
    topics_touched: List[str] = Field(
        ..., 
        min_length=1,
        description="List of topics/subjects affected by the changes"
    )
    summary_of_the_change: str = Field(
        ..., 
        min_length=50,
        description="Detailed summary of what changed between the contracts"
    )


class ProcessingResult(BaseModel):
    """Complete processing result including metadata."""
    
    contract_id: str = Field(..., description="Unique identifier for this processing job")
    status: str = Field(..., pattern="^(success|error)$", description="Processing status")
    result: ContractChangeResult | None = Field(None, description="The extracted changes")
    error: str | None = Field(None, description="Error message if status is error")
    trace_id: str | None = Field(None, description="Langfuse trace ID for debugging")
