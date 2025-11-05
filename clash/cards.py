from clash.troops import *
import random

class Card():
    cardName = ""

    def __init__(self, troop, cost):
        self.troop = troop
        self.cost = cost

        self.owner = None

    def SetOwner(self, owner):
        self.owner = owner

    def Place(self, x, y) -> bool:
        if self.owner and self.owner.elixir >= self.cost:
            self.owner.game.SpawnTroop(x, y, self.troop, self.owner)

            return True
        
        return False

class KnightCard(Card):
    cardName = "KNIGHT"

    def __init__(self):
        super().__init__(Knight, 3)

class GiantCard(Card):
    cardName = "GIANT"

    def __init__(self):
        super().__init__(Giant, 5)

class MiniPekkaCard(Card):
    cardName = "MINI_PEKKA"

    def __init__(self):
        super().__init__(MiniPekka, 4)

class BabyDragonCard(Card):
    cardName = "BABY_DRAGON"

    def __init__(self):
        super().__init__(BabyDragon, 4)

class FireballCard(Card):
    cardName = "FIREBALL"

    def __init__(self):
        super().__init__(Fireball, 4)


class SkeletonCard(Card):
    cardName = "SKELETON"

    def __init__(self):
        super().__init__(Skeleton, 1)

    def Place(self, x, y) -> bool:
        for i in range(3):
            result = super().Place(x + random.randrange(-10, 10), y + random.randrange(-10, 10))

            if not result: return False

        return True

class SkarmyCard(Card):
    cardName = "SKARMY"

    def __init__(self):
        super().__init__(Skeleton, 3)

    def Place(self, x, y) -> bool:
        for i in range(15):
            result = super().Place(x + random.randrange(-10, 10), y + random.randrange(-10, 10))

            if not result: return False

        return True