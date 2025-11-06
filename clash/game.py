from typing import List
from pygame.math import Vector2
from typing import Optional
from clash.troops import *
from clash.cards import *
import random

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

class AOEProjectile(Projectile):
    def __init__(self, x, y, owner, dir, speed, damage, targetPos: Vector2, radius: float):
        super().__init__(x, y, owner, dir, speed, damage)

        self.targetPos = targetPos
        self.radius = radius

    def Tick(self, dt):
        self.x += self.dir.x * dt * self.speed
        self.y += self.dir.y * dt * self.speed

        if Vector2.distance_to(self.targetPos, (self.x, self.y)) <= 5:
            # Damage all troops in the radius
            for troop in list(self.owner.owner.game.troops):
                if troop.owner == self.owner: continue

                if Vector2.distance_to(self.targetPos, (troop.x, troop.y)) <= self.radius:
                    troop.TakeDamage(None, self.damage)

            for tower in list(self.owner.owner.game.towers):
                if tower.owner == self.owner: continue

                if Vector2.distance_to(self.targetPos, (tower.x, tower.y)) <= self.radius:
                    tower.TakeDamage(None, self.damage)

            self.owner.owner.game.KillProjectile(self)

class Tower():
    def __init__(self, x, y, owner, game, active=True, isKing=False):
        self.x = x
        self.y = y

        self.fireTimer = 0

        self.owner = owner
        self.game = game

        self.damage = 99

        self.target: Optional[Troop] = None
        self.active = active

        self.maxHealth = 2786
        self.range = 130
        self.health = self.maxHealth
        self.dead = False

        self.isKing = isKing

        if isKing:
            self.range = 200

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

            # Lock on
            if dx*dx + dy*dy <= (self.range*self.range):
                self.target = troop

    def Activate(self):
        self.active = True
        print("activated")

    def Die(self):
        self.dead = True
        self.active = False

        # Activate king tower
        for tower in self.owner.game.towers:
            if tower.owner == self.owner and tower.isKing:
                tower.Activate()

    def TakeDamage(self, attacker: Optional["Troop"], damage: float) -> bool:
        self.health -= damage

        if self.health <= 0:
            self.Die()
            return True

        return False

class Player():
    def __init__(self, game, isFocused):
        self.isFocused = isFocused
        self.game: "Game" = game
        
        self.elixir: float = 5

        self.deck: List[Card] = [
            FireballCard(),
            BabyDragonCard(),
            KnightCard(),
            GiantCard(),
            SkeletonCard(),
            SkarmyCard(),
            MiniPekkaCard()    
        ]
        
        random.shuffle(self.deck)

        for card in self.deck:
            card.SetOwner(self)

        self.kingTower = None

        self.owner = self

    def PlaceCard(self, x, y, index):
        cardToPlace: Card = self.deck[index]

        if cardToPlace.Place(x, y):
            self.elixir -= cardToPlace.cost

            # Move this guy to the back but keep top 4 in order
            i = self.deck.index(cardToPlace)
            self.deck.remove(cardToPlace)

            card5 = self.deck.pop(3)

            self.deck.insert(i, card5)
            self.deck.append(cardToPlace)

    def Tick(self, dt):
        pass

class Game:
    def __init__(self, blueClass, redClass):
        blue, red = blueClass(self, True), redClass(self, False)

        self.players: List[Player] = [blue, red]
        self.troops: List[Troop] = []
        self.projectiles: List[Projectile] = []
        self.towers: List[Tower] = []
        self.observers = []

        self.running = True
        self.lifetime = 0

        self.elixirMultiplier = 1

        self.placed = False

        # self.SpawnTroop(100, 180, Giant, self.players[1])

        # for i in range(15):
        #     self.SpawnTroop(120 + random.randrange(-10, 10), 380 + random.randrange(-10, 10), Skeleton, self.players[0])

        # self.SpawnTroop(150, 300, Knight, self.players[0])

        # Create towers
        self.towers: List[Tower] = [
            Tower(120, 425, blue, self),
            Tower(330, 425, blue, self),
            Tower(225, 480, blue, self, active=False),

            Tower(120, 130, red, self),
            Tower(330, 130, red, self),
            Tower(225, 70, red, self, active=False)
        ]

        blue.kingTower = self.towers[2]
        red.kingTower = self.towers[5]

    def GetFocusedPlayer(self) -> Player:
        if self.players[0].isFocused: 
            return self.players[0]
        else: 
            return self.players[1]

    def AddObserver(self, observer) -> None:
        self.observers.append(observer)

    def RemoveObserver(self, observer) -> None:
        self.observers.remove(observer)

    def SpawnProjectile(self, x, y, owner, dir, speed, damage, target=None) -> None:
        p = Projectile(x, y, owner, dir, speed, damage, target)

        self.projectiles.append(p)

    def SpawnAOEProjectile(self, x, y, owner, dir, speed, damage, targetPos, radius) -> None:
        p = AOEProjectile(x, y, owner, dir, speed, damage, targetPos, radius)

        self.projectiles.append(p)

    def SpawnTroop(self, x, y, troopClass, owner):
        troop = troopClass(x, y, owner)

        # Don't add any spells
        if troopClass in [Fireball]: return

        self.troops.append(troop)
    
    # TODO: This is ass
    def KillTroop(self, troop):
        if troop in self.troops:
            self.troops.remove(troop)

    def KillProjectile(self, projectile):
        self.projectiles.remove(projectile)

    def Tick(self, dt: float) -> None:
        if not self.running:
            return
        
        self.lifetime += dt
        
        for p in self.players:
            p.elixir = min(10, p.elixir + ELIXIR_PER_SECOND * dt)

        # Sort for z-ordering
        # Remove this if its slow
        self.troops.sort(key=lambda x: x.y)

        for player in self.players:
            player.Tick(dt)

        for troop in self.troops:
            troop.Tick(dt)

        for p in self.projectiles:
            p.Tick(dt)

        for tower in self.towers:
            tower.Tick(dt)

        # Notify all observers
        for observer in self.observers:
            observer.Tick(dt, self)