import json
import uuid
import sys
from pathlib import Path

import typer
from pydantic import ValidationError
from dotenv import load_dotenv

from src.services.contract_comparison_service import ContractComparisonService
from src.infrastructure.parsers.factory import ParserFactory
from src.infrastructure.agents.factory import AgentFactory
from src.domain.models import ProcessingResult, ContractChangeResult
from src.tracing import create_trace, flush_traces

load_dotenv()

app = typer.Typer(help="Contract Comparison and Change Extraction Agent")


def process_contracts(
    original_image_path: str,
    amendment_image_path: str,
    contract_id: str | None = None,
) -> ProcessingResult:
    """
    Process two contract images and extract changes.
    
    Uses hierarchical tracing with Langfuse for full observability.
    
    Args:
        original_image_path: Path to the original contract image
        amendment_image_path: Path to the amendment image
        contract_id: Optional ID for tracking
    
    Returns:
        ProcessingResult with extracted changes or error
    """
    contract_id = contract_id or str(uuid.uuid4())
    
    # Initialize service with factories
    parser = ParserFactory.create()
    contextualization_agent = AgentFactory.create_contextualization_agent()
    extraction_agent = AgentFactory.create_extraction_agent()
    
    service = ContractComparisonService(
        parser=parser,
        contextualization_agent=contextualization_agent,
        extraction_agent=extraction_agent,
    )
    
    # Process with service
    typer.echo(f"Processing contracts...")
    typer.echo(f"  Original: {original_image_path}")
    typer.echo(f"  Amendment: {amendment_image_path}")
    
    result = service.compare(
        original_image_path=original_image_path,
        amendment_image_path=amendment_image_path,
        contract_id=contract_id,
    )
    
    if result.status == "success":
        typer.echo(f"\n✓ Processing complete. Contract ID: {contract_id}")
        if result.trace_id:
            typer.echo(f"Trace ID: {result.trace_id}")
    else:
        typer.echo(f"\n✗ Error: {result.error}", err=True)
    
    return result


@app.command()
def compare(
    original: str = typer.Argument(..., help="Path to original contract image"),
    amendment: str = typer.Argument(..., help="Path to amendment image"),
    contract_id: str = typer.Option(None, "--id", help="Contract ID for tracking"),
    output: str = typer.Option(None, "--output", "-o", help="Output file path (JSON)"),
    pretty: bool = typer.Option(True, "--pretty/--compact", help="Pretty print JSON"),
):
    """
    Compare an original contract with its amendment and extract changes.
    
    Example:
        python -m src.main compare data/original.png data/amendment.png
    """
    original_path = Path(original)
    amendment_path = Path(amendment)
    
    if not original_path.exists():
        typer.echo(f"Error: Original contract not found: {original}", err=True)
        raise typer.Exit(1)
    
    if not amendment_path.exists():
        typer.echo(f"Error: Amendment not found: {amendment}", err=True)
        raise typer.Exit(1)
    
    result = process_contracts(
        str(original_path),
        str(amendment_path),
        contract_id,
    )
    
    indent = 2 if pretty else None
    json_output = result.model_dump_json(indent=indent)
    
    if output:
        Path(output).write_text(json_output)
        typer.echo(f"Output saved to: {output}")
    else:
        typer.echo("\n--- Result ---")
        typer.echo(json_output)
    
    if result.status == "error":
        raise typer.Exit(1)


@app.command()
def validate(
    json_file: str = typer.Argument(..., help="Path to JSON file to validate"),
):
    """
    Validate a JSON file against the ContractChangeResult schema.
    """
    path = Path(json_file)
    
    if not path.exists():
        typer.echo(f"Error: File not found: {json_file}", err=True)
        raise typer.Exit(1)
    
    try:
        data = json.loads(path.read_text())
        result = ContractChangeResult.model_validate(data)
        typer.echo("✓ Valid ContractChangeResult")
        typer.echo(result.model_dump_json(indent=2))
    except Exception as e:
        typer.echo(f"✗ Validation error: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
