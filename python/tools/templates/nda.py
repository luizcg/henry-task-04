import random
from datetime import datetime, timedelta
from faker import Faker

from tools.templates.base import ContractData, ContractSection, ContractPair, Amendment

fake = Faker()


def generate(num_amendments: int = 1) -> ContractPair:
    """Generate a Non-Disclosure Agreement with amendments."""
    
    disclosing_party = fake.company()
    receiving_party = fake.company()
    start_date = fake.date_between(start_date="-2y", end_date="-1y")
    
    original_duration = random.choice([2, 3, 5])
    original_scope = "business strategies, financial data, customer lists, and technical specifications"
    
    original_sections = [
        ContractSection(
            number="1",
            title="DEFINITION OF CONFIDENTIAL INFORMATION",
            content=f"\"Confidential Information\" means any non-public information disclosed by "
                    f"{disclosing_party} (\"Disclosing Party\") to {receiving_party} (\"Receiving Party\"), "
                    f"including but not limited to: {original_scope}. Confidential Information may be "
                    f"disclosed in written, oral, electronic, or visual form."
        ),
        ContractSection(
            number="2",
            title="OBLIGATIONS OF RECEIVING PARTY",
            content="The Receiving Party agrees to: (a) hold all Confidential Information in strict "
                    "confidence; (b) not disclose Confidential Information to any third party without "
                    "prior written consent; (c) use Confidential Information solely for the Purpose "
                    "defined herein; (d) protect Confidential Information using the same degree of "
                    "care used to protect its own confidential information, but no less than reasonable care."
        ),
        ContractSection(
            number="3",
            title="PERMITTED DISCLOSURES",
            content="Receiving Party may disclose Confidential Information to its employees who have "
                    "a need to know and who are bound by confidentiality obligations at least as "
                    "protective as those contained herein. Receiving Party shall be responsible for "
                    "any breach by its employees."
        ),
        ContractSection(
            number="4",
            title="EXCLUSIONS",
            content="Confidential Information does not include information that: (a) is or becomes "
                    "publicly available through no fault of Receiving Party; (b) was rightfully in "
                    "Receiving Party's possession prior to disclosure; (c) is independently developed "
                    "by Receiving Party without use of Confidential Information; (d) is rightfully "
                    "obtained from a third party without restriction."
        ),
        ContractSection(
            number="5",
            title="TERM AND TERMINATION",
            content=f"This Agreement shall remain in effect for {original_duration} years from the "
                    f"Effective Date. The confidentiality obligations shall survive termination and "
                    f"continue for a period of {original_duration} years thereafter."
        ),
        ContractSection(
            number="6",
            title="RETURN OF MATERIALS",
            content="Upon termination or request by Disclosing Party, Receiving Party shall promptly "
                    "return or destroy all Confidential Information and any copies thereof, and shall "
                    "certify in writing that such return or destruction has been completed."
        ),
        ContractSection(
            number="7",
            title="REMEDIES",
            content="Receiving Party acknowledges that any breach may cause irreparable harm to "
                    "Disclosing Party, and that monetary damages may be inadequate. Therefore, "
                    "Disclosing Party shall be entitled to seek equitable relief, including injunction "
                    "and specific performance, in addition to any other available remedies."
        ),
        ContractSection(
            number="8",
            title="GOVERNING LAW",
            content=f"This Agreement shall be governed by the laws of {fake.state()}, without regard "
                    f"to conflicts of law principles. Any disputes shall be resolved in the courts of "
                    f"{fake.city()}, {fake.state()}."
        ),
    ]
    
    original = ContractData(
        title="NON-DISCLOSURE AGREEMENT",
        date=start_date.strftime("%B %d, %Y"),
        parties={
            "Disclosing Party": f"{disclosing_party}, a {fake.state()} corporation",
            "Receiving Party": f"{receiving_party}, a {fake.state()} corporation"
        },
        sections=original_sections,
        signatures=[f"{disclosing_party}, by authorized representative", 
                   f"{receiving_party}, by authorized representative"],
        metadata={"type": "nda", "version": "original"}
    )
    
    changes = []
    amendment_sections = [ContractSection(s.number, s.title, s.content) for s in original_sections]
    
    change_options = [
        ("scope", "1", "DEFINITION OF CONFIDENTIAL INFORMATION"),
        ("permitted", "3", "PERMITTED DISCLOSURES"),
        ("term", "5", "TERM AND TERMINATION"),
        ("return", "6", "RETURN OF MATERIALS"),
    ]
    
    selected_changes = random.sample(change_options, min(num_amendments + 1, len(change_options)))
    
    for change_type, section_num, section_title in selected_changes:
        section_idx = int(section_num) - 1
        original_content = amendment_sections[section_idx].content
        
        if change_type == "scope":
            new_scope = original_scope + ", source code, algorithms, product roadmaps, and merger/acquisition plans"
            new_content = (
                f"\"Confidential Information\" means any non-public information disclosed by "
                f"{disclosing_party} (\"Disclosing Party\") to {receiving_party} (\"Receiving Party\"), "
                f"including but not limited to: {new_scope}. Confidential Information may be "
                f"disclosed in written, oral, electronic, or visual form. Information shall be deemed "
                f"Confidential whether or not marked as such."
            )
            description = "Expanded scope to include source code, algorithms, product roadmaps, and M&A plans; added presumption of confidentiality"
            
        elif change_type == "permitted":
            new_content = (
                "Receiving Party may disclose Confidential Information to its employees and "
                "contractors who have a need to know and who are bound by written confidentiality "
                "obligations at least as protective as those contained herein. Receiving Party may "
                "also disclose to its legal and financial advisors under professional duty of "
                "confidentiality. Receiving Party shall be responsible for any breach by such parties."
            )
            description = "Extended permitted disclosures to include contractors and professional advisors"
            
        elif change_type == "term":
            new_duration = original_duration + 2
            new_content = (
                f"This Agreement shall remain in effect for {new_duration} years from the "
                f"Effective Date. The confidentiality obligations shall survive termination and "
                f"continue indefinitely for trade secrets and for a period of {new_duration} years "
                f"for other Confidential Information."
            )
            description = f"Extended term from {original_duration} to {new_duration} years; added indefinite protection for trade secrets"
            
        elif change_type == "return":
            new_content = (
                "Upon termination or request by Disclosing Party, Receiving Party shall promptly "
                "return or destroy all Confidential Information and any copies thereof, and shall "
                "certify in writing that such return or destruction has been completed. Notwithstanding "
                "the foregoing, Receiving Party may retain one archival copy solely for legal compliance "
                "purposes, subject to continued confidentiality obligations."
            )
            description = "Added exception allowing retention of archival copy for legal compliance"
        
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
        title="AMENDMENT TO NON-DISCLOSURE AGREEMENT",
        date=amendment_date.strftime("%B %d, %Y"),
        parties=original.parties,
        sections=amendment_sections,
        signatures=original.signatures,
        metadata={"type": "nda", "version": "amendment1"}
    )
    
    return ContractPair(original=original, amendment=amendment, changes=changes)
