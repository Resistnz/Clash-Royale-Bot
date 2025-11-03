from typing import Protocol, List, TypeVar, runtime_checkable
from .troop import Troop

@runtime_checkable
class GameObserver(Protocol):
    def Update(self, troops: List[Troop]) -> bool:
        ...