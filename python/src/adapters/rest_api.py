"""REST API adapter using FastAPI."""
import uuid
import asyncio
from typing import Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from src.services.contract_comparison_service import ContractComparisonService
from src.infrastructure.parsers.factory import ParserFactory
from src.infrastructure.agents.factory import AgentFactory
from src.domain.models import ContractChangeResult

# Thread pool for running blocking operations
executor = ThreadPoolExecutor(max_workers=4)


# Request/Response models
class CompareRequest(BaseModel):
    """Request model for contract comparison."""
    original_image: str = Field(..., description="Path or base64 of original contract")
    amendment_image: str = Field(..., description="Path or base64 of amendment")
    contract_id: Optional[str] = Field(None, description="Optional contract ID")
    async_mode: bool = Field(False, alias="async", description="Run asynchronously")
    callback_url: Optional[str] = Field(None, description="Webhook URL for async results")


class CompareResponse(BaseModel):
    """Response model for contract comparison."""
    job_id: str
    status: str
    result: Optional[ContractChangeResult] = None
    error: Optional[str] = None
    processing_time_ms: Optional[int] = None
    trace_id: Optional[str] = None
    message: Optional[str] = None


class JobStatusResponse(BaseModel):
    """Response model for job status."""
    job_id: str
    status: str
    result: Optional[ContractChangeResult] = None
    error: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ProgressResponse(BaseModel):
    """Response model for job progress."""
    job_id: str
    status: str
    progress: int
    step: str
    message: str
    updated_at: datetime


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    timestamp: datetime
    version: str = "1.0.0"


# In-memory job storage (replace with Redis in production)
jobs_store: dict = {}


# FastAPI app
app = FastAPI(
    title="Contract Comparison API",
    description="API for comparing contract documents and extracting changes",
    version="1.0.0",
)


def get_service() -> ContractComparisonService:
    """Create a new service instance with dependencies."""
    return ContractComparisonService(
        parser=ParserFactory.create(),
        contextualization_agent=AgentFactory.create_contextualization_agent(),
        extraction_agent=AgentFactory.create_extraction_agent(),
    )


def process_comparison_async(job_id: str, original: str, amendment: str):
    """Background task for async processing."""
    service = get_service()
    result = service.compare(original, amendment, contract_id=job_id)
    
    jobs_store[job_id] = {
        "status": result.status,
        "result": result.result,
        "error": result.error,
        "completed_at": datetime.utcnow(),
        "trace_id": result.trace_id,
        "processing_time_ms": result.processing_time_ms,
    }


@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
    )


@app.post("/api/v1/contracts/compare", response_model=CompareResponse)
async def compare_contracts(
    request: CompareRequest,
    background_tasks: BackgroundTasks,
):
    """
    Compare two contract images and extract changes.
    
    - **sync mode** (default): Processes immediately and returns result
    - **async mode**: Queues job and returns job_id for polling
    """
    job_id = request.contract_id or str(uuid.uuid4())
    
    print(f"\n{'='*80}")
    print(f"🚀 NEW JOB RECEIVED - ID: {job_id}")
    print(f"   Mode: {'ASYNC' if request.async_mode else 'SYNC'}")
    print(f"   Original: {request.original_image[:50]}...")
    print(f"   Amendment: {request.amendment_image[:50]}...")
    print(f"{'='*80}\n")
    
    if request.async_mode:
        # Async mode: queue for background processing
        jobs_store[job_id] = {
            "status": "pending",
            "result": None,
            "error": None,
            "created_at": datetime.utcnow(),
            "completed_at": None,
        }
        
        background_tasks.add_task(
            process_comparison_async,
            job_id,
            request.original_image,
            request.amendment_image,
        )
        
        return CompareResponse(
            job_id=job_id,
            status="queued",
            message="Job queued for processing",
        )
    
    # Initialize job in store BEFORE processing starts (for progress polling)
    jobs_store[job_id] = {
        "status": "processing",
        "result": None,
        "error": None,
        "created_at": datetime.utcnow(),
        "completed_at": None,
        "progress": {
            "progress": 0,
            "step": "Starting",
            "message": "Initializing processing",
            "updated_at": datetime.utcnow(),
        }
    }
    
    def progress_callback(progress_data: dict):
        """Update progress in jobs_store."""
        jobs_store[job_id]["progress"] = {
            **progress_data,
            "updated_at": datetime.utcnow(),
        }
    
    # Run the comparison in a thread pool to avoid blocking the event loop
    service = get_service()
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        executor,
        lambda: service.compare(
            request.original_image,
            request.amendment_image,
            contract_id=job_id,
            progress_callback=progress_callback,
        )
    )
    
    # Update final status
    jobs_store[job_id].update({
        "status": result.status,
        "result": result.result,
        "error": result.error,
        "completed_at": datetime.utcnow(),
        "trace_id": result.trace_id,
        "processing_time_ms": result.processing_time_ms,
    })
    
    print(f"✅ Job {job_id} completed - Status: {result.status}")
    if result.error:
        print(f"❌ Error: {result.error}")
    print()
    
    return CompareResponse(
        job_id=job_id,
        status=result.status,
        result=result.result,
        error=result.error,
        processing_time_ms=result.processing_time_ms,
        trace_id=result.trace_id,
    )


@app.get("/api/v1/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get the status of an async job."""
    if job_id not in jobs_store:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs_store[job_id]
    
    return JobStatusResponse(
        job_id=job_id,
        status=job["status"],
        result=job.get("result"),
        error=job.get("error"),
        created_at=job.get("created_at"),
        completed_at=job.get("completed_at"),
    )


@app.get("/api/v1/jobs/{job_id}/progress", response_model=ProgressResponse)
async def get_job_progress(job_id: str):
    """Get the current progress of a job."""
    if job_id not in jobs_store:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs_store[job_id]
    progress_data = job.get("progress", {})
    
    return ProgressResponse(
        job_id=job_id,
        status=job["status"],
        progress=progress_data.get("progress", 0),
        step=progress_data.get("step", "Initializing"),
        message=progress_data.get("message", "Starting processing"),
        updated_at=progress_data.get("updated_at", datetime.utcnow()),
    )
