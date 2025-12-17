import json
import uuid
import sys
from pathlib import Path

import typer
from pydantic import ValidationError
from dotenv import load_dotenv

from src.image_parser import parse_contract_image
from src.agents.contextualization_agent import run_contextualization_agent
from src.agents.extraction_agent import run_extraction_agent
from src.models import ProcessingResult, ContractChangeResult
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
    
    # Create hierarchical trace with metadata
    with create_trace(
        name="contract_comparison",
        session_id=contract_id,
        contract_pair_id=contract_id,
        metadata={
            "original_image": original_image_path,
            "amendment_image": amendment_image_path,
        },
    ) as trace:
        try:
            # Step 1: Parse original contract
            typer.echo(f"[1/5] Parsing original contract: {original_image_path}")
            with trace.span("parse_original_contract", input_data={"path": original_image_path}) as span:
                original_doc = parse_contract_image(
                    original_image_path,
                    document_type="original",
                    trace=trace,
                )
                span.update(output={"title": original_doc.title, "sections_count": len(original_doc.sections)})
            
            # Step 2: Parse amendment
            typer.echo(f"[2/5] Parsing amendment: {amendment_image_path}")
            with trace.span("parse_amendment_contract", input_data={"path": amendment_image_path}) as span:
                amendment_doc = parse_contract_image(
                    amendment_image_path,
                    document_type="amendment",
                    trace=trace,
                )
                span.update(output={"title": amendment_doc.title, "sections_count": len(amendment_doc.sections)})
            
            # Step 3: Agent 1 - Contextualization
            typer.echo("[3/5] Agent 1: Contextualizing documents...")
            with trace.span("agent1_contextualization", input_data={
                "original_title": original_doc.title,
                "amendment_title": amendment_doc.title,
            }) as span:
                contextualization = run_contextualization_agent(
                    original_doc,
                    amendment_doc,
                    trace=trace,
                )
                span.update(output={
                    "corresponding_sections_count": len(contextualization.corresponding_sections),
                    "analysis_notes_length": len(contextualization.analysis_notes),
                })
            
            # Step 4: Agent 2 - Extraction
            typer.echo("[4/5] Agent 2: Extracting changes...")
            with trace.span("agent2_extraction", input_data={
                "sections_to_analyze": len(contextualization.corresponding_sections),
            }) as span:
                changes = run_extraction_agent(
                    contextualization,
                    trace=trace,
                )
                span.update(output={
                    "sections_changed": changes.sections_changed,
                    "topics_touched": changes.topics_touched,
                })
            
            # Step 5: Pydantic Validation
            typer.echo("[5/5] Validating output...")
            with trace.span("pydantic_validation", input_data={
                "sections_changed": changes.sections_changed,
                "topics_touched": changes.topics_touched,
            }) as span:
                # Re-validate to ensure output is correct
                validated_changes = ContractChangeResult.model_validate(changes.model_dump())
                span.update(output={"validation": "success", "fields_validated": 3})
            
            result = ProcessingResult(
                contract_id=contract_id,
                status="success",
                result=validated_changes,
                error=None,
                trace_id=trace.trace_id,
            )
            
            typer.echo(f"\n✓ Processing complete. Contract ID: {contract_id}")
            typer.echo(f"View trace at: {trace.get_trace_url()}")
            
        except ValidationError as e:
            result = ProcessingResult(
                contract_id=contract_id,
                status="error",
                result=None,
                error=f"Validation error: {e}",
                trace_id=trace.trace_id,
            )
            typer.echo(f"\n✗ Validation Error: {e}", err=True)
            
        except Exception as e:
            result = ProcessingResult(
                contract_id=contract_id,
                status="error",
                result=None,
                error=str(e),
                trace_id=trace.trace_id,
            )
            typer.echo(f"\n✗ Error: {e}", err=True)
    
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
