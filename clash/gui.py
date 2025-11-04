import os
import pygame
from pygame import gfxdraw

#SHOW_FPS = True

pygame.init()

class GUI:
    def __init__(self) -> None:   
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = 450, 720

        pygame.display.init()

        # Get the directory where main.py is located (project root)
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.IMG_PATH = os.path.join(root_dir, "images/")

        self.win = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.NOFRAME, pygame.SRCALPHA)
        self.surfaceHD = pygame.Surface((self.SCREEN_WIDTH*4, self.SCREEN_HEIGHT*4), pygame.SRCALPHA)

        self.bgImage = pygame.transform.smoothscale_by(pygame.image.load(self.IMG_PATH + "bg.jpg"), 0.5)
        self.shadowImage = pygame.transform.smoothscale_by(pygame.image.load(self.IMG_PATH + "shadow.png"), (0.4, 0.28))
        self.shadowImage.set_alpha(128)

        self.healthbarImage = pygame.transform.smoothscale_by(pygame.image.load(self.IMG_PATH + "healthbar-blue.png"), 1.6)

        self.imagesByTroop = {
            "GIANT": pygame.transform.smoothscale_by(pygame.image.load(self.IMG_PATH + "giant-walk.png"), 0.6)
        }

        self.fpsHistory = []

    # Return False if UI has terminated this frame
    def Tick(self, dt, troops, projectiles) -> bool:
        self.win.blit(self.bgImage, (-415, 0))

        # Fill with transparent
        self.surfaceHD.fill((0, 0, 0, 0))

        for t in troops:
            self.DrawTroop(t)

        for p in projectiles:
            self.DrawProjectile(p)

        scaledHD = pygame.transform.smoothscale_by(self.surfaceHD, 0.25)
        self.win.blit(scaledHD, (0, 0))

        if SHOW_FPS:
            fps = str(int(1 / dt)) if dt > 0 else "N/A"
            font = pygame.font.SysFont('Arial', 30)
            
            self.fpsHistory.append(1 / dt if dt > 0 else 0)
            if len(self.fpsHistory) > 10:
                self.fpsHistory.pop(0)

            avgFPS = sum(self.fpsHistory) / len(self.fpsHistory)
            fps = str(int(avgFPS))

            fpsSurface = font.render(fps, True, (255, 255, 255))
            self.win.blit(fpsSurface, (10, 10))

        # Handle closing the window
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                quit()
                return False

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    quit()
                    return False
                
            if e.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                print(f"Mouse clicked at: ({x}, {y})")
        
        pygame.display.flip()

        return True

    def DrawTroop(self, troop) -> None:
        troopImg = self.imagesByTroop[troop.troopType.name]

        if troop.direction == -1:
            troopImg = pygame.transform.flip(troopImg, False, True)

        width = troopImg.get_width()
        height = troopImg.get_height()

        drawX = troop.x * 4 - width // 2
        drawY = troop.y * 4 - height // 2

        self.surfaceHD.blit(self.shadowImage, (drawX, drawY + 60))
        self.surfaceHD.blit(troopImg, (drawX, drawY))

        self.surfaceHD.blit(self.healthbarImage, (drawX + 20, drawY - 30))

        maxWidth = 100

        barW = int(maxWidth * (troop.health / troop.maxHealth))
        barX = drawX + 80
        barY = drawY

        pygame.draw.rect(self.surfaceHD, (50, 50, 60), (barX, barY, maxWidth, 16), border_radius=3)
        pygame.draw.rect(self.surfaceHD, (52, 146, 235), (barX, barY, barW, 16), border_radius=3)

    def DrawProjectile(self, projectile) -> None:
        pygame.draw.rect(self.surfaceHD, (6, 6, 6), (projectile.x*4, projectile.y*4, 24, 48), border_radius=2)