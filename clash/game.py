from typing import List
from pygame.math import Vector2
from typing import Optional
from clash.troops import *

ELIXIR_PER_SECOND = 1/2.8
PRINCESS_FIRE_RATE = 1/0.8

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
    def __init__(self, x, y, owner, game, active=True):
        self.x = x
        self.y = y

        self.fireTimer = 0

        self.owner = owner
        self.game = game

        self.damage = 99

        self.target: Optional[Troop] = None
        self.active = True

        self.maxHealth = 2786
        self.health = self.maxHealth
        self.dead = False

    def Tick(self, dt: float) -> None:
        if not self.active: return

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

            # Lock on
            if dx*dx + dy*dy <= (radius*radius):
                self.target = troop

    def Die(self):
        self.dead = True
        self.active = False

    def TakeDamage(self, attacker: Optional["Troop"], damage: float) -> bool:
        self.health -= damage

        if self.health <= 0:
            self.Die()
            return True

        return False

class Player():
    def __init__(self, game, isFocused):
        self.isFocused = isFocused
        self.game = game
        
        self.elixir: float = 0

class Game:
    def __init__(self):
        blue, red = Player(self, True), Player(self, False)

        self.players: List[Player] = [blue, red]
        self.troops: List[Troop] = []
        self.projectiles: List[Projectile] = []
        self.towers: List[Tower] = []
        self.observers = []

        self.running = True
        self.lifetime = 0

        self.elixirMultiplier = 1

        self.SpawnTroop(100, 200, Giant, self.players[1])

        self.SpawnTroop(130, 400, Skeleton, self.players[0])
        self.SpawnTroop(120, 410, Skeleton, self.players[0])
        self.SpawnTroop(120, 390, Skeleton, self.players[0])

        # Create towers
        self.towers: List[Tower] = [
            Tower(120, 425, blue, self),
            Tower(330, 425, blue, self),
            Tower(225, 480, blue, self, active=False)
        ]

    def AddObserver(self, observer) -> None:
        self.observers.append(observer)

    def RemoveObserver(self, observer) -> None:
        self.observers.remove(observer)

    def SpawnProjectile(self, x, y, owner, dir, speed, damage, target=None) -> None:
        p = Projectile(x, y, owner, dir, speed, damage, target)

        self.projectiles.append(p)

    def SpawnTroop(self, x, y, troopClass, owner):
        troop = troopClass(x, y, owner)

        self.troops.append(troop)
    
    # TODO: This is ass
    def KillTroop(self, troop):
        self.troops.remove(troop)

    def KillProjectile(self, projectile):
        self.projectiles.remove(projectile)

    def Tick(self, dt: float) -> None:
        if not self.running:
            return
        
        self.lifetime += dt
        
        for p in self.players:
            p.elixir += ELIXIR_PER_SECOND * dt

        for troop in self.troops:
            troop.Tick(dt)

        for p in self.projectiles:
            p.Tick(dt)

        for tower in self.towers:
            tower.Tick(dt)

        # Notify all observers
        for observer in self.observers:
            observer.Tick(dt, self.troops, self.projectiles, self.towers)