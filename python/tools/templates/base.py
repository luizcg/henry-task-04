from dataclasses import dataclass, field
from typing import List
from faker import Faker

fake = Faker()


@dataclass
class ContractSection:
    """Represents a section in a contract."""
    number: str
    title: str
    content: str


@dataclass
class ContractData:
    """Complete contract data structure."""
    title: str
    date: str
    parties: dict
    sections: List[ContractSection]
    signatures: List[str]
    metadata: dict = field(default_factory=dict)
    
    def get_full_text(self) -> str:
        """Get the complete contract text."""
        lines = [
            self.title,
            "",
            f"Date: {self.date}",
            "",
            "PARTIES:",
        ]
        for party_name, party_info in self.parties.items():
            lines.append(f"  {party_name}: {party_info}")
        lines.append("")
        
        for section in self.sections:
            lines.append(f"{section.number}. {section.title}")
            lines.append(section.content)
            lines.append("")
        
        lines.append("SIGNATURES:")
        for sig in self.signatures:
            lines.append(f"  ________________________")
            lines.append(f"  {sig}")
            lines.append("")
        
        return "\n".join(lines)


@dataclass
class Amendment:
    """Describes changes made in an amendment."""
    section_number: str
    change_type: str  # 'modified', 'added', 'removed'
    original_content: str
    new_content: str
    description: str


@dataclass
class ContractPair:
    """Original contract and its amendment."""
    original: ContractData
    amendment: ContractData
    changes: List[Amendment]
    
    def get_changes_summary(self) -> str:
        """Get a human-readable summary of changes."""
        lines = ["# Changes Summary", ""]
        for i, change in enumerate(self.changes, 1):
            lines.append(f"## Change {i}: Section {change.section_number}")
            lines.append(f"**Type:** {change.change_type}")
            lines.append(f"**Description:** {change.description}")
            lines.append("")
            if change.original_content:
                lines.append("**Original:**")
                lines.append(f"```\n{change.original_content}\n```")
            if change.new_content:
                lines.append("**New:**")
                lines.append(f"```\n{change.new_content}\n```")
            lines.append("")
        return "\n".join(lines)
