from clash.game import Player
import random

class Agent(Player):
    def __init__(self, game, isFocused):
        super().__init__(game, isFocused)

    # Best ai of all time fr
    def Tick(self, dt):
        cardIndex = random.randrange(0, 3)

        if self.elixir >= self.deck[cardIndex].cost:
            xPos, yPos = random.randrange(50, 400), random.randrange(80, 291)

            if self.isFocused:
                yPos = 600 - yPos

            self.PlaceCard(xPos, yPos, cardIndex)