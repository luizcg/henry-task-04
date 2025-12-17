import os
from datetime import datetime
from typing import Optional, Any
from contextlib import contextmanager

from dotenv import load_dotenv
from langfuse import get_client, propagate_attributes

load_dotenv()


class TracingContext:
    """Context manager for hierarchical tracing with Langfuse."""
    
    def __init__(
        self,
        name: str,
        session_id: Optional[str] = None,
        contract_pair_id: Optional[str] = None,
        metadata: Optional[dict] = None,
    ):
        self.langfuse = get_client()
        self.name = name
        self.session_id = session_id
        self.contract_pair_id = contract_pair_id
        self.timestamp = datetime.utcnow().isoformat()
        self.metadata = metadata or {}
        self.root_span = None
        self._trace_id = None
    
    def __enter__(self):
        """Create the parent trace/span."""
        # Create root span with all metadata
        self.root_span = self.langfuse.start_as_current_observation(
            as_type="span",
            name=self.name,
            input={
                "contract_pair_id": self.contract_pair_id,
                "timestamp": self.timestamp,
                **self.metadata,
            },
        )
        # Enter the context manager
        self._span_context = self.root_span.__enter__()
        
        # Propagate session attributes
        self._attr_context = propagate_attributes(
            session_id=self.session_id,
            user_id=self.contract_pair_id,
            tags=["contract_comparison"],
            metadata={
                "contract_pair_id": self.contract_pair_id,
                "timestamp": self.timestamp,
            },
        )
        self._attr_context.__enter__()
        
        # Get trace ID
        self._trace_id = self.langfuse.get_current_trace_id()
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End trace and flush."""
        # Update root span with final output if no error
        if exc_type is None:
            self._span_context.update(output={"status": "success"})
        else:
            self._span_context.update(output={"status": "error", "error": str(exc_val)})
        
        # Exit contexts
        self._attr_context.__exit__(exc_type, exc_val, exc_tb)
        self.root_span.__exit__(exc_type, exc_val, exc_tb)
        
        # Flush traces
        self.langfuse.flush()
        return False
    
    @contextmanager
    def span(self, name: str, input_data: Optional[Any] = None):
        """Create a child span within the trace."""
        with self.langfuse.start_as_current_observation(
            as_type="span",
            name=name,
            input=input_data,
        ) as span:
            yield span
    
    def generation(
        self,
        name: str,
        model: str,
        input_data: Optional[Any] = None,
        metadata: Optional[dict] = None,
    ):
        """Create a generation span for LLM calls."""
        return self.langfuse.start_generation(
            name=name,
            model=model,
            input=input_data,
            metadata=metadata or {},
        )
    
    @property
    def trace_id(self) -> str:
        """Get the trace ID."""
        return self._trace_id
    
    def get_trace_url(self) -> str:
        """Get the URL to view this trace in Langfuse."""
        host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        return f"{host}/trace/{self._trace_id}" if self._trace_id else None


def create_trace(
    name: str,
    session_id: Optional[str] = None,
    contract_pair_id: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> TracingContext:
    """
    Create a new tracing context with hierarchical spans.
    
    Args:
        name: Name of the trace (e.g., "contract_comparison")
        session_id: Session ID for grouping traces
        contract_pair_id: ID of the contract pair being processed
        metadata: Additional metadata to attach to the trace
    
    Returns:
        TracingContext that can be used as a context manager
    """
    return TracingContext(
        name=name,
        session_id=session_id,
        contract_pair_id=contract_pair_id,
        metadata=metadata,
    )


def flush_traces():
    """Flush all pending traces to Langfuse."""
    langfuse = get_client()
    langfuse.flush()
