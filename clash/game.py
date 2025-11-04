from typing import List
from enum import Enum, auto
from pygame.math import Vector2
from typing import Optional

ELIXIR_PER_SECOND = 1/2.8
PRINCESS_FIRE_RATE = 1/0.8

class TroopType(Enum):
    GIANT = auto()

class Troop():
    def __init__(self, x: int, y: int, t: TroopType, owner):
        self.x = x
        self.y = y

        self.speed = 10
        self.direction = 1 # -1 for moving down

        self.owner = owner

        if not owner.isFocused:
            self.direction = -1

        self.troopType = t

        self.target: Optional[Troop] = None

        self.health = 4090
        self.maxHealth = 4090
        self.damage = 253
        self.attackTimer = 0
        self.attackSpeed = 1.5

        self.dead = False

    def Tick(self, dt: float) -> None:
        if self.dead: 
            return

        self.attackTimer = min(1, self.attackTimer + self.attackSpeed * dt)

        self.y -= self.speed * dt * self.direction

        if self.target and self.attackSpeed == self.attackTimer:
            self.attackTimer = 0

            self.Attack()

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

class Projectile():
    def __init__(self, x, y, owner, dir: Vector2, speed: float, damage: float, target: Optional[Troop] = None):
        self.x = x
        self.y = y

        self.owner = owner

        self.dir = dir
        self.speed = speed

        self.target = target
        self.damage = damage

    def Tick(self, dt):
        self.x += self.dir.x * dt * self.speed
        self.y += self.dir.y * dt * self.speed

        if self.target:
            # Check if dist to target is close
            dx = self.target.x - self.x
            dy = self.target.y - self.y

            radius = 16

            if dx * dx + dy * dy <= (radius*radius):
                self.target.TakeDamage(None, self.damage)
                
                self.owner.game.KillProjectile(self)

class Tower():
    def __init__(self, x, y, owner, game):
        self.x = x
        self.y = y

        self.fireTimer = 0

        self.owner = owner
        self.game = game

        self.damage = 1000

        self.target: Optional[Troop] = None

    def Tick(self, dt: float) -> None:
        self.PickTarget()

        self.fireTimer = min(1, self.fireTimer + PRINCESS_FIRE_RATE * dt)

        if self.target and self.fireTimer == 1:
            self.fireTimer = 0

            dx, dy = self.target.x - self.x, self.target.y - self.y

            self.game.SpawnProjectile(self.x, self.y, self, Vector2(dx, dy).normalize(), 300, self.damage, self.target)

    def PickTarget(self) -> None:
        if self.target != None:
            if self.target.dead:
                self.target = None

            return

        for troop in self.game.troops:
            if troop.owner == self.owner: continue
            if troop.dead: continue

            dx = troop.x - self.x
            dy = troop.y - self.y

            radius = 100

            if dx*dx + dy*dy <= (radius*radius):
                self.target = troop

                print(f"Locked onto {self.target.troopType.name}")

class Player():
    def __init__(self, game, isFocused):
        self.isFocused = isFocused
        self.game = game

        if isFocused:
            self.towers: List[Tower] = [
                Tower(120, 425, self, self.game),
                Tower(330, 425, self, self.game),
                Tower(225, 480, self, self.game)
            ]
        else:
            self.towers: List[Tower] = []
        
        self.elixir: float = 0

class Game:
    def __init__(self):
        self.players: List[Player] = [Player(self, True), Player(self, False)]
        self.troops: List[Troop] = []
        self.projectiles: List[Projectile] = []
        self.observers = []

        self.running = True

        self.elixirMultiplier = 1

        self.SpawnTroop(100, 300, TroopType.GIANT, self.players[1])

    def AddObserver(self, observer) -> None:
        self.observers.append(observer)

    def RemoveObserver(self, observer) -> None:
        self.observers.remove(observer)

    def SpawnProjectile(self, x, y, owner, dir, speed, damage, target=None) -> None:
        p = Projectile(x, y, owner, dir, speed, damage, target)

        self.projectiles.append(p)

    def SpawnTroop(self, x, y, troopType, owner):
        troop = Troop(x, y, troopType, owner)

        self.troops.append(troop)

    # TODO: This is ass
    def KillTroop(self, troop):
        self.troops.remove(troop)

    def KillProjectile(self, projectile):
        self.projectiles.remove(projectile)

    def Tick(self, dt: float) -> None:
        if not self.running:
            return
        
        for p in self.players:
            p.elixir += ELIXIR_PER_SECOND * dt

        for troop in self.troops:
            troop.Tick(dt)

        for p in self.projectiles:
            p.Tick(dt)

        for player in self.players:
            for tower in player.towers:
                tower.Tick(dt)

        # Notify all observers
        for observer in self.observers:
            observer.Tick(dt, self.troops, self.projectiles)