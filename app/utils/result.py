from dataclasses import dataclass
from typing import Generic, TypeVar, Optional

T = TypeVar("T")
E = TypeVar("E")

@dataclass
class Result(Generic[T, E]):
    value: Optional[T] = None
    error: Optional[E] = None
    is_success: bool = False

    @classmethod
    def ok(cls, value: T):
        return cls(value=value, is_success=True)

    @classmethod
    def fail(cls, error: E):
        return cls(error=error, is_success=False)
