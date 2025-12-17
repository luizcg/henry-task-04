"""RabbitMQ consumer adapter."""
import json
import asyncio
from typing import Optional
from datetime import datetime

import aio_pika
from aio_pika import IncomingMessage
from pydantic import BaseModel, Field

from src.services.contract_comparison_service import ContractComparisonService
from src.infrastructure.parsers.factory import ParserFactory
from src.infrastructure.agents.factory import AgentFactory
from src.config.settings import settings


class ContractJobRequest(BaseModel):
    """Request model for RabbitMQ jobs."""
    job_id: str
    contract_id: str
    original_image: str
    amendment_image: str
    metadata: Optional[dict] = None


class ContractJobResponse(BaseModel):
    """Response model for RabbitMQ jobs."""
    job_id: str
    contract_id: str
    status: str
    result: Optional[dict] = None
    error: Optional[str] = None
    processing_time_ms: Optional[int] = None
    trace_id: Optional[str] = None


def get_service() -> ContractComparisonService:
    """Create a new service instance with dependencies."""
    return ContractComparisonService(
        parser=ParserFactory.create(),
        contextualization_agent=AgentFactory.create_contextualization_agent(),
        extraction_agent=AgentFactory.create_extraction_agent(),
    )


async def process_message(message: IncomingMessage):
    """Process a single message from the queue."""
    async with message.process():
        try:
            # Parse request
            body = json.loads(message.body.decode())
            request = ContractJobRequest.model_validate(body)
            
            print(f"[*] Processing job: {request.job_id}")
            
            # Process contract comparison
            service = get_service()
            result = service.compare(
                request.original_image,
                request.amendment_image,
                contract_id=request.contract_id,
                metadata=request.metadata,
            )
            
            # Build response
            response = ContractJobResponse(
                job_id=request.job_id,
                contract_id=request.contract_id,
                status=result.status,
                result=result.result.model_dump() if result.result else None,
                error=result.error,
                processing_time_ms=result.processing_time_ms,
                trace_id=result.trace_id,
            )
            
            # Send response to reply_to queue if specified
            if message.reply_to:
                connection = await aio_pika.connect_robust(settings.rabbitmq_url)
                async with connection:
                    channel = await connection.channel()
                    await channel.default_exchange.publish(
                        aio_pika.Message(
                            body=response.model_dump_json().encode(),
                            correlation_id=message.correlation_id,
                            content_type="application/json",
                        ),
                        routing_key=message.reply_to,
                    )
            
            print(f"[✓] Job {request.job_id} completed: {result.status}")
            
        except Exception as e:
            print(f"[✗] Error processing message: {e}")
            # Could implement retry logic here


async def start_consumer():
    """Start the RabbitMQ consumer."""
    print(f"[*] Connecting to RabbitMQ: {settings.rabbitmq_url}")
    
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    
    async with connection:
        channel = await connection.channel()
        
        # Set prefetch to 1 (process one job at a time)
        await channel.set_qos(prefetch_count=1)
        
        # Declare queue
        queue = await channel.declare_queue(
            settings.queue_name,
            durable=True,
        )
        
        print(f"[*] Waiting for messages on queue: {settings.queue_name}")
        
        # Start consuming
        await queue.consume(process_message)
        
        # Keep running
        await asyncio.Future()


def run_consumer():
    """Run the consumer (blocking)."""
    asyncio.run(start_consumer())
