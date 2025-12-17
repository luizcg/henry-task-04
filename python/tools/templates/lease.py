import random
from datetime import datetime, timedelta
from faker import Faker

from tools.templates.base import ContractData, ContractSection, ContractPair, Amendment

fake = Faker()


def generate(num_amendments: int = 1) -> ContractPair:
    """Generate a Lease Agreement with amendments."""
    
    landlord = fake.name()
    tenant = fake.name()
    property_address = f"{fake.street_address()}, {fake.city()}, {fake.state()} {fake.zipcode()}"
    start_date = fake.date_between(start_date="-2y", end_date="-1y")
    
    original_rent = random.randint(1500, 4000)
    original_deposit = original_rent * 2
    original_term = random.choice([12, 24])
    
    original_sections = [
        ContractSection(
            number="1",
            title="PREMISES",
            content=f"Landlord agrees to lease to Tenant the property located at {property_address} "
                    f"(\"Premises\"). The Premises shall be used solely for residential purposes."
        ),
        ContractSection(
            number="2",
            title="TERM",
            content=f"The lease term shall be {original_term} months, commencing on the Effective Date. "
                    f"Upon expiration, this lease shall convert to a month-to-month tenancy unless "
                    f"either party provides 30 days written notice of termination."
        ),
        ContractSection(
            number="3",
            title="RENT",
            content=f"Tenant shall pay monthly rent of ${original_rent:,} due on the first day of each "
                    f"month. Rent shall be paid by check or electronic transfer to Landlord. A late "
                    f"fee of $50 shall apply to payments received after the 5th of the month."
        ),
        ContractSection(
            number="4",
            title="SECURITY DEPOSIT",
            content=f"Tenant shall pay a security deposit of ${original_deposit:,} upon execution of "
                    f"this lease. The deposit shall be returned within 30 days of lease termination, "
                    f"less any deductions for damages beyond normal wear and tear."
        ),
        ContractSection(
            number="5",
            title="UTILITIES",
            content="Tenant shall be responsible for all utilities including electricity, gas, water, "
                    "sewer, trash, internet, and cable. Landlord shall be responsible for property taxes "
                    "and building insurance."
        ),
        ContractSection(
            number="6",
            title="MAINTENANCE",
            content="Landlord shall maintain the structural elements, roof, and major systems (HVAC, "
                    "plumbing, electrical) in good working order. Tenant shall maintain the interior "
                    "and promptly report any maintenance issues to Landlord."
        ),
        ContractSection(
            number="7",
            title="PETS",
            content="No pets are allowed on the Premises without prior written consent of Landlord. "
                    "Violation of this provision shall be grounds for immediate termination."
        ),
        ContractSection(
            number="8",
            title="ALTERATIONS",
            content="Tenant shall not make any alterations, additions, or improvements to the Premises "
                    "without prior written consent of Landlord. Any approved alterations shall become "
                    "property of Landlord upon termination."
        ),
    ]
    
    original = ContractData(
        title="RESIDENTIAL LEASE AGREEMENT",
        date=start_date.strftime("%B %d, %Y"),
        parties={
            "Landlord": f"{landlord}, an individual",
            "Tenant": f"{tenant}, an individual"
        },
        sections=original_sections,
        signatures=[landlord, tenant],
        metadata={"type": "lease", "version": "original"}
    )
    
    changes = []
    amendment_sections = [ContractSection(s.number, s.title, s.content) for s in original_sections]
    
    change_options = [
        ("rent", "3", "RENT"),
        ("deposit", "4", "SECURITY DEPOSIT"),
        ("pets", "7", "PETS"),
        ("utilities", "5", "UTILITIES"),
    ]
    
    selected_changes = random.sample(change_options, min(num_amendments + 1, len(change_options)))
    
    for change_type, section_num, section_title in selected_changes:
        section_idx = int(section_num) - 1
        original_content = amendment_sections[section_idx].content
        
        if change_type == "rent":
            new_rent = original_rent + random.randint(100, 300)
            new_content = (
                f"Tenant shall pay monthly rent of ${new_rent:,} due on the first day of each "
                f"month. Rent shall be paid by check, electronic transfer, or through the online "
                f"portal at landlordpay.example.com. A late fee of $75 shall apply to payments "
                f"received after the 5th of the month. Rent may be increased annually with 60 days notice."
            )
            description = f"Rent increased from ${original_rent:,} to ${new_rent:,}; added online payment option; late fee increased to $75; added annual increase provision"
            
        elif change_type == "deposit":
            new_deposit = int(original_deposit * 0.75)
            new_content = (
                f"Tenant shall pay a security deposit of ${new_deposit:,} upon execution of "
                f"this lease. The deposit shall be held in an interest-bearing account and returned "
                f"within 21 days of lease termination, less any deductions for damages beyond normal "
                f"wear and tear. Landlord shall provide itemized statement of any deductions."
            )
            description = f"Deposit reduced from ${original_deposit:,} to ${new_deposit:,}; added interest-bearing requirement; shortened return period to 21 days; added itemization requirement"
            
        elif change_type == "pets":
            pet_deposit = 500
            new_content = (
                f"Pets are allowed on the Premises subject to the following conditions: (a) maximum "
                f"of 2 pets; (b) dogs must be under 50 pounds; (c) Tenant shall pay a non-refundable "
                f"pet fee of ${pet_deposit}; (d) Tenant shall maintain renter's insurance covering "
                f"pet liability. Prohibited breeds and exotic animals are not permitted."
            )
            description = f"Changed from no pets to allowing up to 2 pets with restrictions; added ${pet_deposit} pet fee and insurance requirement"
            
        elif change_type == "utilities":
            new_content = (
                "Tenant shall be responsible for electricity, gas, internet, and cable. Landlord "
                "shall be responsible for water, sewer, and trash collection. Landlord shall also "
                "be responsible for property taxes and building insurance. If utility costs exceed "
                "historical averages by more than 20%, parties shall discuss cost sharing."
            )
            description = "Changed utility split: Landlord now covers water/sewer/trash; added provision for unusual utility cost sharing"
        
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
        title="AMENDMENT TO RESIDENTIAL LEASE AGREEMENT",
        date=amendment_date.strftime("%B %d, %Y"),
        parties=original.parties,
        sections=amendment_sections,
        signatures=original.signatures,
        metadata={"type": "lease", "version": "amendment1"}
    )
    
    return ContractPair(original=original, amendment=amendment, changes=changes)
