from clash.game import Player
import random

class Agent(Player):
    def __init__(self, game, isFocused):
        super().__init__(game, isFocused)

        self.choice = 0# random.randrange(0, 3)

    # Best ai of all time fr
    def Tick(self, dt):
        #return
        if self.elixir >= self.deck[self.choice].cost:
            xPos, yPos = random.randrange(50, 400), random.randrange(80, 291)

            if self.isFocused:
                yPos = 600 - yPos

            self.PlaceCard(xPos, yPos, self.choice)

            self.choice = random.randrange(0, 3)

class RedAgent(Player):
    def __init__(self, game, isFocused):
        super().__init__(game, isFocused)

    def Tick(self, dt):
        if self.elixir >= self.deck[2].cost:
            self.PlaceCard(100, 200, 2)

class BlueAgent(Player):
    def __init__(self, game, isFocused):
        super().__init__(game, isFocused)

        self.done = False

    def Tick(self, dt):
        if self.elixir >= self.deck[0].cost and not self.done:
            self.PlaceCard(100, 240, 0)

            self.done = True

class NoAgent(Player):
    def __init__(self, game, isFocused):
        super().__init__(game, isFocused)