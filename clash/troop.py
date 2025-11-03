from .types import TroopType

class Troop():
    def __init__(self, t: TroopType):
        self.x = 300
        self.y = 300

        self.speed = 10

        self.troopType = t

    def Update(self, deltaTime: float) -> None:
        self.y -= self.speed * deltaTime
