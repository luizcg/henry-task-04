from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from tools.templates.base import ContractData


def generate_pdf(contract: ContractData, output_path: Path) -> Path:
    """
    Generate a PDF document from contract data.
    
    Args:
        contract: ContractData object with all contract information
        output_path: Path where to save the PDF
    
    Returns:
        Path to the generated PDF
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72,
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'ContractTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=20,
        alignment=1,
        fontName='Helvetica-Bold',
    )
    
    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=12,
        spaceBefore=15,
        spaceAfter=8,
        fontName='Helvetica-Bold',
    )
    
    body_style = ParagraphStyle(
        'ContractBody',
        parent=styles['Normal'],
        fontSize=10,
        spaceBefore=0,
        spaceAfter=10,
        leading=14,
        fontName='Helvetica',
    )
    
    party_style = ParagraphStyle(
        'PartyInfo',
        parent=styles['Normal'],
        fontSize=10,
        leftIndent=20,
        spaceBefore=3,
        spaceAfter=3,
        fontName='Helvetica',
    )
    
    signature_style = ParagraphStyle(
        'Signature',
        parent=styles['Normal'],
        fontSize=10,
        spaceBefore=30,
        spaceAfter=5,
        fontName='Helvetica',
    )
    
    story = []
    
    story.append(Paragraph(contract.title, title_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph(f"<b>Effective Date:</b> {contract.date}", body_style))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("<b>PARTIES</b>", section_title_style))
    for party_name, party_info in contract.parties.items():
        story.append(Paragraph(f"<b>{party_name}:</b> {party_info}", party_style))
    story.append(Spacer(1, 10))
    
    for section in contract.sections:
        story.append(Paragraph(
            f"<b>{section.number}. {section.title}</b>",
            section_title_style
        ))
        story.append(Paragraph(section.content, body_style))
    
    story.append(Spacer(1, 30))
    story.append(Paragraph("<b>SIGNATURES</b>", section_title_style))
    story.append(Spacer(1, 20))
    
    for signature in contract.signatures:
        story.append(Paragraph("_" * 40, signature_style))
        story.append(Paragraph(signature, body_style))
        story.append(Paragraph("Date: _________________", body_style))
        story.append(Spacer(1, 20))
    
    doc.build(story)
    
    return output_path
