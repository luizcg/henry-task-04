from enum import Enum
from typing import Callable
import random


class ContractType(str, Enum):
    EMPLOYMENT = "employment"
    NDA = "nda"
    SERVICE = "service"
    LEASE = "lease"
    
    @classmethod
    def random(cls) -> "ContractType":
        return random.choice(list(cls))
    
    @classmethod
    def choices(cls) -> list[str]:
        return [t.value for t in cls]


def get_template(contract_type: ContractType) -> Callable:
    """Get the template generator function for a contract type."""
    from tools.templates import employment, nda, service, lease
    
    templates = {
        ContractType.EMPLOYMENT: employment.generate,
        ContractType.NDA: nda.generate,
        ContractType.SERVICE: service.generate,
        ContractType.LEASE: lease.generate,
    }
    return templates[contract_type]
