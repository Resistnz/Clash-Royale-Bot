from pygame import time
from clash.game import Game
from clash.gui import GUI
from agent import *

TICKS_PER_SECOND = 60

def main():
    # Create core game instance
    game = Game(BlueAgent, RedAgent)
    
    # Create and attach GUI observer
    gui = GUI()
    game.AddObserver(gui)

    # Main game loop
    clock = time.Clock()
    while game.running:
        dt = clock.tick(TICKS_PER_SECOND) / 1000
        
        game.Tick(dt)

if __name__ == "__main__":
    main()