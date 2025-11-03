from __future__ import annotations
from typing import List, TYPE_CHECKING
import os
import pygame
from pygame import gfxdraw
from .types import TroopType

if TYPE_CHECKING:
    from .troop import Troop

class GUI:
    def __init__(self) -> None:   
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = 450, 720
        # Get the directory where main.py is located (project root)
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.IMG_PATH = os.path.join(root_dir, "images/")

        pygame.init()

        self.win = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.NOFRAME, pygame.SRCALPHA)

        self.bgImage = pygame.transform.smoothscale_by(pygame.image.load(self.IMG_PATH + "bg.jpg"), 0.5)
        self.shadowImage = pygame.transform.smoothscale_by(pygame.image.load(self.IMG_PATH + "shadow.png"), (0.1, 0.07))
        self.shadowImage.set_alpha(128)

        self.imagesByTroop = {
            TroopType.GIANT: pygame.transform.smoothscale_by(pygame.image.load(self.IMG_PATH + "giant-walk.png"), 0.15)
        }

    # Return False if UI has terminated this frame
    def Update(self, troops: list[Troop]) -> bool:
        self.win.blit(self.bgImage, (-415, 0))

        for t in troops:
            self.DrawTroop(t)

        # Handle closing the window
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                quit()
                return False

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    quit()
                    return False
        
        pygame.display.flip()

        return True

    def DrawTroop(self, troop) -> None:
        self.win.blit(self.shadowImage, (troop.x, troop.y + 15))
        self.win.blit(self.imagesByTroop[troop.troopType], (troop.x, troop.y))