import json
import random
from pathlib import Path
from typing import Optional, List

import typer
from rich.console import Console
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.panel import Panel
from rich.table import Table

from tools.templates import ContractType, get_template
from tools.templates.base import ContractPair
from tools.effects import VisualEffect
from tools.pdf_generator import generate_pdf
from tools.image_converter import pdf_to_images

app = typer.Typer(help="Generate fictional contract pairs for testing")
console = Console()

DEFAULT_OUTPUT_DIR = Path("data/contracts")


def select_contract_type() -> ContractType:
    """Interactive selection of contract type."""
    console.print("\n[bold cyan]🔹 Select contract type:[/bold cyan]")
    
    table = Table(show_header=False, box=None)
    table.add_column("Option", style="cyan")
    table.add_column("Type")
    
    for i, ct in enumerate(ContractType, 1):
        table.add_row(f"[{i}]", ct.value.replace("_", " ").title())
    table.add_row(f"[{len(ContractType) + 1}]", "Random (default)")
    
    console.print(table)
    
    choice = Prompt.ask(
        "Choice",
        default=str(len(ContractType) + 1),
    )
    
    try:
        idx = int(choice)
        if idx == len(ContractType) + 1:
            selected = ContractType.random()
            console.print(f"  → Randomly selected: [green]{selected.value}[/green]")
            return selected
        elif 1 <= idx <= len(ContractType):
            return list(ContractType)[idx - 1]
    except ValueError:
        pass
    
    return ContractType.random()


def select_quantity() -> int:
    """Interactive selection of number of contract pairs."""
    console.print("\n[bold cyan]🔹 How many contract pairs?[/bold cyan]")
    
    quantity = IntPrompt.ask("Quantity", default=1)
    return max(1, min(quantity, 10))


def select_output_format() -> tuple[bool, bool]:
    """Interactive selection of output format."""
    console.print("\n[bold cyan]🔹 Output format:[/bold cyan]")
    
    table = Table(show_header=False, box=None)
    table.add_column("Option", style="cyan")
    table.add_column("Format")
    
    table.add_row("[1]", "PDF only")
    table.add_row("[2]", "Image only")
    table.add_row("[3]", "Both (default)")
    
    console.print(table)
    
    choice = Prompt.ask("Choice", default="3")
    
    if choice == "1":
        return True, False
    elif choice == "2":
        return False, True
    else:
        return True, True


def select_visual_effects() -> List[VisualEffect]:
    """Interactive selection of visual effects for images."""
    console.print("\n[bold cyan]🔹 Visual variations for images:[/bold cyan]")
    
    table = Table(show_header=False, box=None)
    table.add_column("Option", style="cyan")
    table.add_column("Effect")
    table.add_column("Description", style="dim")
    
    table.add_row("[1]", "Clean", "Digital, high quality")
    table.add_row("[2]", "Scanned", "Noise, slight rotation, borders")
    table.add_row("[3]", "Photographed", "Perspective, shadows, lighting")
    table.add_row("[4]", "Low-res", "Low resolution, JPEG artifacts")
    table.add_row("[5]", "All variations")
    
    console.print(table)
    
    choice = Prompt.ask("Choice", default="1")
    
    if choice == "5":
        return VisualEffect.all()
    elif choice in ["1", "2", "3", "4"]:
        return [list(VisualEffect)[int(choice) - 1]]
    else:
        return [VisualEffect.CLEAN]


def generate_contract_pair(
    contract_type: ContractType,
    output_dir: Path,
    contract_num: int,
    generate_pdf_flag: bool,
    generate_images: bool,
    effects: List[VisualEffect],
) -> Path:
    """Generate a single contract pair with all outputs."""
    
    contract_dir = output_dir / f"contract_{contract_num:03d}"
    contract_dir.mkdir(parents=True, exist_ok=True)
    
    template_func = get_template(contract_type)
    pair: ContractPair = template_func(num_amendments=random.randint(1, 3))
    
    original_pdf = None
    amendment_pdf = None
    
    if generate_pdf_flag:
        original_pdf = generate_pdf(pair.original, contract_dir / "contract_original.pdf")
        amendment_pdf = generate_pdf(pair.amendment, contract_dir / "contract_amendment1.pdf")
        console.print(f"    📄 PDFs generated")
    
    if generate_images:
        if original_pdf is None:
            original_pdf = generate_pdf(pair.original, contract_dir / ".temp_original.pdf")
            amendment_pdf = generate_pdf(pair.amendment, contract_dir / ".temp_amendment.pdf")
        
        try:
            pdf_to_images(original_pdf, contract_dir, "contract_original", effects)
            pdf_to_images(amendment_pdf, contract_dir, "contract_amendment1", effects)
            console.print(f"    🖼️  Images generated ({len(effects)} variation(s))")
            
            if not generate_pdf_flag:
                original_pdf.unlink(missing_ok=True)
                amendment_pdf.unlink(missing_ok=True)
        except ImportError as e:
            console.print(f"    [yellow]⚠️  Images not generated: {e}[/yellow]")
    
    metadata = {
        "contract_type": contract_type.value,
        "original": {
            "title": pair.original.title,
            "date": pair.original.date,
            "sections": [s.number for s in pair.original.sections],
        },
        "amendment": {
            "title": pair.amendment.title,
            "date": pair.amendment.date,
            "sections": [s.number for s in pair.amendment.sections],
        },
        "changes": [
            {
                "section": c.section_number,
                "type": c.change_type,
                "description": c.description,
            }
            for c in pair.changes
        ],
    }
    (contract_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))
    
    return contract_dir


@app.command()
def generate(
    contract_type: Optional[str] = typer.Option(
        None, "--type", "-t",
        help=f"Contract type: {', '.join(ContractType.choices())} or 'random'"
    ),
    quantity: Optional[int] = typer.Option(
        None, "--quantity", "-n",
        help="Number of contract pairs to generate (1-10)"
    ),
    output_format: Optional[str] = typer.Option(
        None, "--format", "-f",
        help="Output format: pdf, image, or both"
    ),
    effects: Optional[str] = typer.Option(
        None, "--effects", "-e",
        help=f"Visual effects: {', '.join(VisualEffect.choices())} or 'all'"
    ),
    output_dir: Path = typer.Option(
        DEFAULT_OUTPUT_DIR, "--output", "-o",
        help="Output directory"
    ),
    interactive: bool = typer.Option(
        True, "--interactive/--no-interactive", "-i/-I",
        help="Interactive mode (prompts for options)"
    ),
):
    """
    Generate fictional contract pairs for testing the contract comparison agent.
    
    Run without arguments for interactive mode, or use flags for automation.
    
    Examples:
        generate-contracts
        generate-contracts -t employment -n 2 -f both -e scanned -I
    """
    console.print(Panel.fit(
        "[bold]Contract Generator[/bold]\n"
        "Fictional contract generator for testing",
        border_style="cyan"
    ))
    
    if interactive and contract_type is None:
        selected_type = select_contract_type()
    else:
        if contract_type == "random" or contract_type is None:
            selected_type = ContractType.random()
        else:
            try:
                selected_type = ContractType(contract_type)
            except ValueError:
                console.print(f"[red]Invalid type: {contract_type}[/red]")
                raise typer.Exit(1)
    
    if interactive and quantity is None:
        selected_quantity = select_quantity()
    else:
        selected_quantity = max(1, min(quantity or 1, 10))
    
    if interactive and output_format is None:
        gen_pdf, gen_images = select_output_format()
    else:
        fmt = output_format or "both"
        gen_pdf = fmt in ["pdf", "both"]
        gen_images = fmt in ["image", "images", "both"]
    
    if gen_images:
        if interactive and effects is None:
            selected_effects = select_visual_effects()
        else:
            if effects == "all":
                selected_effects = VisualEffect.all()
            elif effects:
                try:
                    selected_effects = [VisualEffect(effects)]
                except ValueError:
                    selected_effects = [VisualEffect.CLEAN]
            else:
                selected_effects = [VisualEffect.CLEAN]
    else:
        selected_effects = []
    
    console.print(f"\n[bold green]✓ Generating {selected_quantity} contract pair(s)...[/bold green]\n")
    
    output_dir = Path(output_dir)
    generated = []
    
    for i in range(1, selected_quantity + 1):
        console.print(f"  [cyan]Contract {i}/{selected_quantity}:[/cyan] {selected_type.value}")
        
        try:
            contract_dir = generate_contract_pair(
                contract_type=selected_type if selected_quantity == 1 else ContractType.random(),
                output_dir=output_dir,
                contract_num=_get_next_contract_num(output_dir),
                generate_pdf_flag=gen_pdf,
                generate_images=gen_images,
                effects=selected_effects,
            )
            generated.append(contract_dir)
            console.print(f"    ✓ Created: [green]{contract_dir}[/green]")
        except Exception as e:
            console.print(f"    [red]✗ Error: {e}[/red]")
    
    console.print(f"\n[bold green]✓ {len(generated)} contract(s) generated in {output_dir}[/bold green]")


def _get_next_contract_num(output_dir: Path) -> int:
    """Get the next available contract number."""
    if not output_dir.exists():
        return 1
    
    existing = list(output_dir.glob("contract_*"))
    if not existing:
        return 1
    
    numbers = []
    for d in existing:
        try:
            num = int(d.name.split("_")[1])
            numbers.append(num)
        except (IndexError, ValueError):
            pass
    
    return max(numbers, default=0) + 1


@app.command()
def list_types():
    """List all available contract types."""
    console.print("\n[bold]Available contract types:[/bold]\n")
    
    table = Table()
    table.add_column("Type", style="cyan")
    table.add_column("Description")
    
    descriptions = {
        ContractType.EMPLOYMENT: "Employment contract with salary, benefits, termination",
        ContractType.NDA: "Non-disclosure agreement between companies",
        ContractType.SERVICE: "Service agreement with rates, term, IP",
        ContractType.LEASE: "Residential lease agreement",
    }
    
    for ct in ContractType:
        table.add_row(ct.value, descriptions.get(ct, ""))
    
    console.print(table)


@app.command()
def list_effects():
    """List all available visual effects."""
    console.print("\n[bold]Available visual effects:[/bold]\n")
    
    table = Table()
    table.add_column("Effect", style="cyan")
    table.add_column("Description")
    
    descriptions = {
        VisualEffect.CLEAN: "Clean digital image, high quality",
        VisualEffect.SCANNED: "Simulates scanned document (noise, rotation, dark borders)",
        VisualEffect.PHOTOGRAPHED: "Simulates phone photo (perspective, shadows, lighting)",
        VisualEffect.LOWRES: "Low resolution with JPEG compression artifacts",
    }
    
    for effect in VisualEffect:
        table.add_row(effect.value, descriptions.get(effect, ""))
    
    console.print(table)


if __name__ == "__main__":
    app()
