from pygame import time
from clash.game import Game
from clash.gui import GUI
from agent import *
import time as t

FIXED_DT = 1/60
TIMESCALE = 1

RENDER_GAME = False

def main():
    startTime = t.perf_counter_ns()

    # Create core game instance
    game = Game(Agent, Agent)
    
    # Create and attach GUI observer
    if RENDER_GAME:
        gui = GUI()
        game.AddObserver(gui)

    # Main game loop
    clock = time.Clock()
    while game.running:
        dt = FIXED_DT

        if RENDER_GAME:
            dt = clock.tick(60) / 1000 * TIMESCALE

            for observer in game.observers:
                observer.Tick(dt, game)

        game.Tick(dt)

    endTime = t.perf_counter_ns()

    print(f"Simulating 1 game took {round((endTime - startTime)/1e6, 2)}ms.")

if __name__ == "__main__":
    main()