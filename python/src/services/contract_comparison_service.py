"""Contract comparison service - core business logic."""
import uuid
from typing import Optional, Any, Callable
from datetime import datetime

from src.domain.models import (
    DocumentStructure,
    ContextualizationResult,
    ContractChangeResult,
    ProcessingResult,
)
from src.domain.interfaces import (
    ImageParserStrategy,
    ContextualizationAgent,
    ExtractionAgent,
)
from src.tracing import TracingContext, create_trace


class ContractComparisonService:
    """
    Service layer for contract comparison.
    
    This service encapsulates all business logic for comparing contracts,
    independent of the transport layer (REST API, RabbitMQ, CLI).
    """
    
    def __init__(
        self,
        parser: ImageParserStrategy,
        contextualization_agent: ContextualizationAgent,
        extraction_agent: ExtractionAgent,
    ):
        """
        Initialize the service with required dependencies.
        
        Args:
            parser: Image parser strategy implementation
            contextualization_agent: Agent for document contextualization
            extraction_agent: Agent for change extraction
        """
        self.parser = parser
        self.contextualization_agent = contextualization_agent
        self.extraction_agent = extraction_agent
    
    def compare(
        self,
        original_image_path: str,
        amendment_image_path: str,
        contract_id: Optional[str] = None,
        metadata: Optional[dict] = None,
        progress_callback: Optional[Callable[[dict], None]] = None,
    ) -> ProcessingResult:
        """
        Compare two contract images and extract changes.
        
        Args:
            original_image_path: Path to the original contract image
            amendment_image_path: Path to the amendment image
            contract_id: Optional ID for tracking
            metadata: Optional metadata for tracing
            progress_callback: Optional callback function for progress updates
        
        Returns:
            ProcessingResult with extracted changes or error
        """
        contract_id = contract_id or str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        def report_progress(step: str, progress: int, message: str):
            """Helper to report progress."""
            if progress_callback:
                progress_callback({
                    "step": step,
                    "progress": progress,
                    "message": message,
                    "status": "processing",
                })
        
        with create_trace(
            name="contract_comparison",
            session_id=contract_id,
            contract_pair_id=contract_id,
            metadata={
                "original_image": original_image_path,
                "amendment_image": amendment_image_path,
                **(metadata or {}),
            },
        ) as trace:
            try:
                # Step 1: Parse original contract
                report_progress("Step 1/5", 10, "Parsing original contract...")
                with trace.span("parse_original_contract", input_data={"path": original_image_path}) as span:
                    original_doc = self.parser.parse(
                        original_image_path,
                        document_type="original",
                        trace=trace,
                    )
                    span.update(output={
                        "title": original_doc.title,
                        "sections_count": len(original_doc.sections),
                    })
                report_progress("Step 1/5", 20, "Original contract parsed successfully")
                
                # Step 2: Parse amendment
                report_progress("Step 2/5", 30, "Parsing amendment contract...")
                with trace.span("parse_amendment_contract", input_data={"path": amendment_image_path}) as span:
                    amendment_doc = self.parser.parse(
                        amendment_image_path,
                        document_type="amendment",
                        trace=trace,
                    )
                    span.update(output={
                        "title": amendment_doc.title,
                        "sections_count": len(amendment_doc.sections),
                    })
                report_progress("Step 2/5", 40, "Amendment contract parsed successfully")
                
                # Step 3: Contextualization
                report_progress("Step 3/5", 50, "Contextualizing documents with AI...")
                with trace.span("agent1_contextualization", input_data={
                    "original_title": original_doc.title,
                    "amendment_title": amendment_doc.title,
                }) as span:
                    contextualization = self.contextualization_agent.run(
                        original_doc,
                        amendment_doc,
                        trace=trace,
                    )
                    span.update(output={
                        "corresponding_sections_count": len(contextualization.corresponding_sections),
                        "analysis_notes_length": len(contextualization.analysis_notes),
                    })
                report_progress("Step 3/5", 60, "Contextualization complete")
                
                # Step 4: Extraction
                report_progress("Step 4/5", 70, "Extracting changes with AI...")
                with trace.span("agent2_extraction", input_data={
                    "sections_to_analyze": len(contextualization.corresponding_sections),
                }) as span:
                    changes = self.extraction_agent.run(
                        contextualization,
                        trace=trace,
                    )
                    span.update(output={
                        "sections_changed": changes.sections_changed,
                        "topics_touched": changes.topics_touched,
                    })
                report_progress("Step 4/5", 85, "Change extraction complete")
                
                # Step 5: Validation
                report_progress("Step 5/5", 90, "Validating results...")
                with trace.span("pydantic_validation", input_data={
                    "sections_changed": changes.sections_changed,
                    "topics_touched": changes.topics_touched,
                }) as span:
                    validated_changes = ContractChangeResult.model_validate(changes.model_dump())
                    span.update(output={"validation": "success", "fields_validated": 3})
                
                processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                
                report_progress("Completed", 100, "Processing complete!")
                
                return ProcessingResult(
                    contract_id=contract_id,
                    status="success",
                    result=validated_changes,
                    error=None,
                    trace_id=trace.trace_id,
                    processing_time_ms=processing_time_ms,
                )
                
            except Exception as e:
                processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                
                return ProcessingResult(
                    contract_id=contract_id,
                    status="error",
                    result=None,
                    error=str(e),
                    trace_id=trace.trace_id,
                    processing_time_ms=processing_time_ms,
                )
