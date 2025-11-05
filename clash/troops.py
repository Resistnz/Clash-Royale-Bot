from enum import Enum, auto
from typing import Optional
import math

class TroopType(Enum):
    GIANT = auto()
    SKELETON = auto()
    KNIGHT = auto()

class Troop():
    def __init__(self, x: int, y: int, t: TroopType, owner):
        self.x = x
        self.y = y

        self.speed = 10
        self.direction = 90

        self.owner = owner

        if not owner.isFocused:
            self.direction += 180

        self.troopType = t

        self.target: Optional[Troop] = None

        self.maxHealth = 4090
        self.health = self.maxHealth
        
        self.damage = 253
        self.attackTimer = 0
        self.attackSpeed = 1/1.5 # 

        self.initialAttackTimer = 0
        self.initialAttackSpeed = 1/0.5

        self.dead = False
        self.targetBuildings = True

        # How much it gets influenced by other troops pushing
        self.weight = 1

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

                self.initialAttackTimer = min(1, self.initialAttackTimer + self.initialAttackSpeed * dt)

                if self.attackTimer == 1 and self.initialAttackTimer == 1:
                    self.attackTimer = 0

                    self.Attack()

        if moving:
            # Calculate separation force from nearby troops
            separationX, separationY = 0, 0
            nearbyCount = 0
            
            for other in self.owner.game.troops:
                if other == self or other.dead:
                    continue
                    
                dx = self.x - other.x
                dy = self.y - other.y
                distanceSq = dx*dx + dy*dy
                
                # Define minimum desired separation distance
                minDistance = 30
                
                if distanceSq < minDistance * minDistance:
                    # Calculate repulsion strength (stronger when closer)
                    distance = math.sqrt(distanceSq)
                    baseStrength = 1.0 - (distance / minDistance)
                    
                    weightRatio = other.weight / (self.weight + other.weight)
                    #weightRatio = 1
                    pushStrength = baseStrength * weightRatio
                    
                    # Normalize the direction vector
                    if distance > 0:
                        dx = dx / distance
                        dy = dy / distance
                    
                    separationX += dx * pushStrength
                    separationY += dy * pushStrength
                    nearbyCount += 1
            
            # Apply separation force if there are nearby troops
            if nearbyCount > 0:
                separationStrength = 40
                separationX = separationX * separationStrength
                separationY = separationY * separationStrength
            
            # Combine movement direction with separation
            rad = math.radians(self.direction)
            moveX = math.cos(rad) * self.speed
            moveY = -math.sin(rad) * self.speed
            
            # Apply both forces
            self.x += (moveX + separationX) * dt
            self.y += (moveY + separationY) * dt

    def PickTarget(self) -> None:
        if self.target != None:
            if self.target.dead:
                self.target = None
                return

        closest = None
        closestDist = float('inf')

        closestBuilding = None
        closestBuildingDist = float('inf')

        initialTarget = self.target

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

        if self.targetBuildings or not self.target:
            self.target = closestBuilding

        # Update initialAttack timer if changed target
        if initialTarget != self.target:
            self.initialAttackTimer = 0

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

        self.weight = 1

class Knight(Troop):
    def __init__(self, x: int, y: int, owner):
        super().__init__(x, y, TroopType.KNIGHT, owner)

        self.speed = 15

        self.maxHealth = 1766
        self.health = self.maxHealth
        
        self.damage = 202
        self.attackTimer = 0
        self.attackSpeed = 1.2

        self.targetBuildings = False

        self.weight = 20

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

        self.weight = 50

class MiniPekka(Troop):
    def __init__(self, x: int, y: int, owner):
        super().__init__(x, y, TroopType.GIANT, owner)

        self.speed = 10

        self.maxHealth = 4090
        self.health = self.maxHealth
        
        self.damage = 253
        self.attackTimer = 0
        self.attackSpeed = 1/1.5

        self.targetBuildings = True

        self.weight = 50