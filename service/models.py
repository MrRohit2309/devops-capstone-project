"""Customer account model and in-memory repository."""

from dataclasses import dataclass, field
from threading import Lock
from typing import Dict, List, Optional
from uuid import UUID, uuid4


@dataclass
class Customer:
    """A customer account."""

    first_name: str
    last_name: str
    email: str
    address: str
    id: UUID = field(default_factory=uuid4)

    def to_dict(self) -> dict:
        """Return the public JSON representation."""
        return {
            "id": str(self.id),
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "address": self.address,
        }


class CustomerRepository:
    """Thread-safe in-memory store used by this stateless sample service."""

    def __init__(self) -> None:
        self._customers: Dict[UUID, Customer] = {}
        self._lock = Lock()

    def list(self) -> List[Customer]:
        with self._lock:
            return list(self._customers.values())

    def get(self, customer_id: UUID) -> Optional[Customer]:
        with self._lock:
            return self._customers.get(customer_id)

    def add(self, customer: Customer) -> Customer:
        with self._lock:
            self._customers[customer.id] = customer
        return customer

    def update(self, customer_id: UUID, values: dict) -> Optional[Customer]:
        with self._lock:
            customer = self._customers.get(customer_id)
            if customer is None:
                return None
            for key, value in values.items():
                setattr(customer, key, value)
            return customer

    def delete(self, customer_id: UUID) -> bool:
        with self._lock:
            return self._customers.pop(customer_id, None) is not None

    def clear(self) -> None:
        with self._lock:
            self._customers.clear()
