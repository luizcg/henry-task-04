import random
from datetime import datetime, timedelta
from faker import Faker

from tools.templates.base import ContractData, ContractSection, ContractPair, Amendment

fake = Faker()


def generate(num_amendments: int = 1) -> ContractPair:
    """Generate a Service Agreement with amendments."""
    
    provider = fake.company()
    client = fake.company()
    start_date = fake.date_between(start_date="-2y", end_date="-1y")
    
    service_type = random.choice(["software development", "consulting", "marketing", "IT support"])
    original_rate = random.randint(100, 300)
    original_hours = random.randint(20, 40)
    original_liability = random.randint(50, 100) * 1000
    
    original_sections = [
        ContractSection(
            number="1",
            title="SERVICES",
            content=f"{provider} (\"Provider\") agrees to provide {service_type} services to "
                    f"{client} (\"Client\") as described in Exhibit A attached hereto. Provider "
                    f"shall perform all services in a professional and workmanlike manner consistent "
                    f"with industry standards."
        ),
        ContractSection(
            number="2",
            title="COMPENSATION",
            content=f"Client shall pay Provider at a rate of ${original_rate} per hour for services "
                    f"rendered. Provider shall submit monthly invoices detailing hours worked and "
                    f"services performed. Payment is due within 30 days of invoice date. Estimated "
                    f"monthly hours: {original_hours} hours."
        ),
        ContractSection(
            number="3",
            title="TERM",
            content="This Agreement shall commence on the Effective Date and continue for a period "
                    "of 12 months, unless earlier terminated as provided herein. Either party may "
                    "terminate with 30 days written notice."
        ),
        ContractSection(
            number="4",
            title="INTELLECTUAL PROPERTY",
            content="All work product created by Provider in the course of performing services "
                    "shall be considered \"work for hire\" and shall be the exclusive property of "
                    "Client. Provider hereby assigns all rights, title, and interest in such work "
                    "product to Client."
        ),
        ContractSection(
            number="5",
            title="CONFIDENTIALITY",
            content="Provider agrees to maintain the confidentiality of all Client information "
                    "obtained during the performance of services. This obligation shall survive "
                    "termination of this Agreement."
        ),
        ContractSection(
            number="6",
            title="LIABILITY",
            content=f"Provider's total liability under this Agreement shall not exceed "
                    f"${original_liability:,}. In no event shall either party be liable for "
                    f"indirect, incidental, special, or consequential damages."
        ),
        ContractSection(
            number="7",
            title="INSURANCE",
            content="Provider shall maintain professional liability insurance with coverage of "
                    "at least $1,000,000 per occurrence and shall provide Client with certificate "
                    "of insurance upon request."
        ),
        ContractSection(
            number="8",
            title="INDEPENDENT CONTRACTOR",
            content="Provider is an independent contractor and not an employee of Client. Provider "
                    "shall be responsible for all taxes and benefits. Nothing in this Agreement "
                    "creates a partnership, joint venture, or agency relationship."
        ),
    ]
    
    original = ContractData(
        title="SERVICE AGREEMENT",
        date=start_date.strftime("%B %d, %Y"),
        parties={
            "Provider": f"{provider}, a {fake.state()} corporation",
            "Client": f"{client}, a {fake.state()} corporation"
        },
        sections=original_sections,
        signatures=[f"{provider}, by authorized representative", 
                   f"{client}, by authorized representative"],
        metadata={"type": "service", "version": "original"}
    )
    
    changes = []
    amendment_sections = [ContractSection(s.number, s.title, s.content) for s in original_sections]
    
    change_options = [
        ("rate", "2", "COMPENSATION"),
        ("term", "3", "TERM"),
        ("ip", "4", "INTELLECTUAL PROPERTY"),
        ("liability", "6", "LIABILITY"),
    ]
    
    selected_changes = random.sample(change_options, min(num_amendments + 1, len(change_options)))
    
    for change_type, section_num, section_title in selected_changes:
        section_idx = int(section_num) - 1
        original_content = amendment_sections[section_idx].content
        
        if change_type == "rate":
            new_rate = original_rate + random.randint(25, 75)
            new_hours = original_hours + random.randint(10, 20)
            new_content = (
                f"Client shall pay Provider at a rate of ${new_rate} per hour for services "
                f"rendered. For work exceeding {new_hours} hours per month, a discounted rate "
                f"of ${new_rate - 25} per hour shall apply. Provider shall submit bi-weekly "
                f"invoices detailing hours worked and services performed. Payment is due within "
                f"15 days of invoice date."
            )
            description = f"Rate increased from ${original_rate} to ${new_rate}/hr; added volume discount; changed to bi-weekly invoicing with 15-day payment terms"
            
        elif change_type == "term":
            new_content = (
                "This Agreement shall commence on the Effective Date and continue for a period "
                "of 24 months, unless earlier terminated as provided herein. Either party may "
                "terminate with 60 days written notice. Upon termination, Provider shall complete "
                "any work in progress and deliver all completed deliverables to Client."
            )
            description = "Extended term from 12 to 24 months; increased notice period from 30 to 60 days; added transition provisions"
            
        elif change_type == "ip":
            new_content = (
                "All work product created by Provider in the course of performing services "
                "shall be considered \"work for hire\" and shall be the exclusive property of "
                "Client upon full payment. Provider hereby assigns all rights, title, and interest "
                "in such work product to Client. Notwithstanding the foregoing, Provider retains "
                "rights to pre-existing materials and general knowledge/skills developed during engagement."
            )
            description = "Added condition that IP transfers only upon full payment; Provider retains pre-existing materials and general skills"
            
        elif change_type == "liability":
            new_liability = original_liability * 2
            new_content = (
                f"Provider's total liability under this Agreement shall not exceed "
                f"${new_liability:,} or the total fees paid under this Agreement in the preceding "
                f"12 months, whichever is greater. In no event shall either party be liable for "
                f"indirect, incidental, special, or consequential damages, except in cases of "
                f"gross negligence or willful misconduct."
            )
            description = f"Liability cap increased from ${original_liability:,} to ${new_liability:,}; added alternative based on fees paid; added exception for gross negligence"
        
        amendment_sections[section_idx] = ContractSection(section_num, section_title, new_content)
        
        changes.append(Amendment(
            section_number=section_num,
            change_type="modified",
            original_content=original_content,
            new_content=new_content,
            description=description
        ))
    
    amendment_date = start_date + timedelta(days=random.randint(180, 365))
    
    amendment = ContractData(
        title="AMENDMENT TO SERVICE AGREEMENT",
        date=amendment_date.strftime("%B %d, %Y"),
        parties=original.parties,
        sections=amendment_sections,
        signatures=original.signatures,
        metadata={"type": "service", "version": "amendment1"}
    )
    
    return ContractPair(original=original, amendment=amendment, changes=changes)
