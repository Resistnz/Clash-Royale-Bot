from typing import List
from .troop import Troop
from .types import TroopType
from .interfaces import GameObserver

class Game:
    def __init__(self):
        self.troops: List[Troop] = []
        self.observers: List[GameObserver] = []

        self.running = True

        self.troops.append(Troop(TroopType.GIANT))

    def AddObserver(self, observer: GameObserver) -> None:
        self.observers.append(observer)

    def RemoveObserver(self, observer: GameObserver) -> None:
        self.observers.remove(observer)

    def Tick(self, dt: float) -> None:
        if not self.running:
            return

        for troop in self.troops:
            troop.Update(dt)

        # Notify all observers
        for observer in self.observers:
            observer.Update(self.troops)