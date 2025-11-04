from enum import Enum, auto
from typing import Optional
import math

class TroopType(Enum):
    GIANT = auto()
    SKELETON = auto()

class Troop():
    def __init__(self, x: int, y: int, t: TroopType, owner):
        self.x = x
        self.y = y

        self.speed = 10
        self.direction = 90 # angle from 0 to 360 degrees

        self.owner = owner

        if not owner.isFocused:
            self.direction += 180

        self.troopType = t

        self.target: Optional[Troop] = None

        self.maxHealth = 4090
        self.health = self.maxHealth
        
        self.damage = 253
        self.attackTimer = 0
        self.attackSpeed = 1/1.5

        self.dead = False
        self.targetBuildings = True

    def Tick(self, dt: float) -> None:
        if self.dead: 
            return    

        self.PickTarget()

        self.attackTimer = min(1, self.attackTimer + self.attackSpeed * dt)

        moving = True

        if self.target:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            self.direction = math.degrees(math.atan2(-dy, dx))

            # Attacks
            attackRadius = 32

            # In range
            if dx*dx + dy*dy < attackRadius*attackRadius:
                moving = False

                if self.attackTimer == 1:
                    self.attackTimer = 0

                    self.Attack()

        if moving:
            rad = math.radians(self.direction)
            self.x += math.cos(rad) * self.speed * dt
            self.y -= math.sin(rad) * self.speed * dt

    # Only pick a new target once the old one is dead
    def PickTarget(self) -> None:
        if self.target != None:
            if self.target.dead:
                self.target = None

            return

        closest = None
        closestDist = float('inf')

        closestBuilding = None
        closestBuildingDist = float('inf')

        for troop in self.owner.game.troops:
            if troop.owner == self.owner: continue
            if troop.dead: continue

            dx = troop.x - self.x
            dy = troop.y - self.y

            dist = dx*dx + dy*dy

            if not closest or dist < closestDist:
                closest = troop
                closestDist = dist

        # Also check towers
        for tower in self.owner.game.towers:
            if tower.owner == self.owner: continue
            if tower.dead: continue

            dx = tower.x - self.x
            dy = tower.y - self.y

            dist = dx*dx + dy*dy

            if not closestBuilding or dist < closestBuildingDist:
                closestBuildingDist = dist
                closestBuilding = tower

        radius = 100
        if closestDist <= radius*radius:
            self.target = closest

        if self.targetBuildings:
            self.target = closestBuilding

    # Returns True if died
    def TakeDamage(self, attacker: Optional["Troop"], damage: float) -> bool:
        self.health -= damage

        if self.health <= 0:
            self.Die()
            return True

        return False
    
    def Die(self) -> None:
        self.owner.game.KillTroop(self)

        self.dead = True

    def Attack(self):
        if not self.target: return

        self.target.TakeDamage(self, self.damage)

class Skeleton(Troop):
    def __init__(self, x: int, y: int, owner):
        super().__init__(x, y, TroopType.SKELETON, owner)

        self.speed = 25

        self.maxHealth = 81
        self.health = self.maxHealth
        
        self.damage = 81
        self.attackTimer = 0
        self.attackSpeed = 1

        self.targetBuildings = False

class Giant(Troop):
    def __init__(self, x: int, y: int, owner):
        super().__init__(x, y, TroopType.GIANT, owner)

        self.speed = 10

        self.maxHealth = 4090
        self.health = self.maxHealth
        
        self.damage = 253
        self.attackTimer = 0
        self.attackSpeed = 1/1.5

        self.targetBuildings = True