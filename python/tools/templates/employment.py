import random
from datetime import datetime, timedelta
from faker import Faker

from tools.templates.base import ContractData, ContractSection, ContractPair, Amendment

fake = Faker()


def generate(num_amendments: int = 1) -> ContractPair:
    """Generate an Employment Agreement with amendments."""
    
    employer = fake.company()
    employee = fake.name()
    start_date = fake.date_between(start_date="-2y", end_date="-1y")
    
    original_salary = random.randint(50, 150) * 1000
    original_vacation = random.randint(10, 20)
    original_notice = 30
    
    original_sections = [
        ContractSection(
            number="1",
            title="PARTIES",
            content=f"This Employment Agreement is entered into between {employer} "
                    f"(\"Employer\") and {employee} (\"Employee\")."
        ),
        ContractSection(
            number="2",
            title="POSITION AND DUTIES",
            content=f"Employee shall serve as {fake.job()} and shall perform all duties "
                    f"as reasonably assigned by the Employer. Employee shall report to "
                    f"the {fake.job()} and work primarily from {fake.city()}, {fake.state()}."
        ),
        ContractSection(
            number="3",
            title="COMPENSATION",
            content=f"Employee shall receive an annual base salary of ${original_salary:,} USD, "
                    f"payable in bi-weekly installments. Salary reviews shall occur annually "
                    f"on the anniversary of the Start Date."
        ),
        ContractSection(
            number="4",
            title="BENEFITS",
            content=f"Employee shall be entitled to {original_vacation} days of paid vacation "
                    f"per year, plus standard company holidays. Employee shall be eligible for "
                    f"the company health insurance plan after 90 days of employment."
        ),
        ContractSection(
            number="5",
            title="TERMINATION",
            content=f"Either party may terminate this Agreement with {original_notice} days "
                    f"written notice. Employer may terminate immediately for cause, including "
                    f"but not limited to: misconduct, breach of confidentiality, or failure "
                    f"to perform duties."
        ),
        ContractSection(
            number="6",
            title="CONFIDENTIALITY",
            content="Employee agrees to maintain strict confidentiality of all proprietary "
                    "information, trade secrets, and business strategies of the Employer, "
                    "both during and after employment."
        ),
        ContractSection(
            number="7",
            title="NON-COMPETE",
            content="For a period of 12 months following termination, Employee shall not "
                    "engage in any business that directly competes with Employer within "
                    "a 50-mile radius of any Employer office location."
        ),
        ContractSection(
            number="8",
            title="GOVERNING LAW",
            content=f"This Agreement shall be governed by the laws of the State of "
                    f"{fake.state()}, without regard to conflicts of law principles."
        ),
    ]
    
    original = ContractData(
        title="EMPLOYMENT AGREEMENT",
        date=start_date.strftime("%B %d, %Y"),
        parties={
            "Employer": f"{employer}, a corporation organized under the laws of {fake.state()}",
            "Employee": f"{employee}, an individual residing in {fake.city()}, {fake.state()}"
        },
        sections=original_sections,
        signatures=[f"{employer}, by authorized representative", employee],
        metadata={"type": "employment", "version": "original"}
    )
    
    changes = []
    amendment_sections = [ContractSection(s.number, s.title, s.content) for s in original_sections]
    
    change_options = [
        ("salary", "3", "COMPENSATION"),
        ("vacation", "4", "BENEFITS"),
        ("notice", "5", "TERMINATION"),
        ("noncompete", "7", "NON-COMPETE"),
    ]
    
    selected_changes = random.sample(change_options, min(num_amendments + 1, len(change_options)))
    
    for change_type, section_num, section_title in selected_changes:
        section_idx = int(section_num) - 1
        original_content = amendment_sections[section_idx].content
        
        if change_type == "salary":
            new_salary = original_salary + random.randint(10, 30) * 1000
            new_content = (
                f"Employee shall receive an annual base salary of ${new_salary:,} USD, "
                f"payable in bi-weekly installments. Additionally, Employee shall be eligible "
                f"for an annual performance bonus of up to 15% of base salary. "
                f"Salary reviews shall occur annually on the anniversary of the Start Date."
            )
            description = f"Salary increased from ${original_salary:,} to ${new_salary:,} and added 15% performance bonus"
            
        elif change_type == "vacation":
            new_vacation = original_vacation + random.randint(3, 7)
            new_content = (
                f"Employee shall be entitled to {new_vacation} days of paid vacation "
                f"per year, plus standard company holidays. Unused vacation days may be "
                f"carried over to the next year, up to a maximum of 5 days. Employee shall "
                f"be eligible for the company health insurance plan after 60 days of employment."
            )
            description = f"Vacation increased from {original_vacation} to {new_vacation} days, added carryover policy, reduced insurance waiting period"
            
        elif change_type == "notice":
            new_notice = original_notice + 30
            new_content = (
                f"Either party may terminate this Agreement with {new_notice} days "
                f"written notice. Employer may terminate immediately for cause, including "
                f"but not limited to: misconduct, breach of confidentiality, or failure "
                f"to perform duties. Upon termination without cause, Employee shall receive "
                f"severance pay equal to 2 weeks salary for each year of service."
            )
            description = f"Notice period extended from {original_notice} to {new_notice} days and added severance policy"
            
        elif change_type == "noncompete":
            new_content = (
                "For a period of 6 months following termination, Employee shall not "
                "engage in any business that directly competes with Employer within "
                "a 25-mile radius of the Employee's primary work location. This restriction "
                "shall not apply if Employee is terminated without cause."
            )
            description = "Non-compete reduced from 12 to 6 months, radius reduced from 50 to 25 miles, added exception for termination without cause"
        
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
        title="AMENDMENT TO EMPLOYMENT AGREEMENT",
        date=amendment_date.strftime("%B %d, %Y"),
        parties=original.parties,
        sections=amendment_sections,
        signatures=original.signatures,
        metadata={"type": "employment", "version": "amendment1"}
    )
    
    return ContractPair(original=original, amendment=amendment, changes=changes)
