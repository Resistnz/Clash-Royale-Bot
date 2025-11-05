import os
import pygame
from pygame import gfxdraw

SHOW_FPS = False

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
        self.shadowLayer = pygame.Surface((self.SCREEN_WIDTH*4, self.SCREEN_HEIGHT*4), pygame.SRCALPHA)

        self.bgImage = pygame.transform.smoothscale_by(pygame.image.load(self.IMG_PATH + "bg.jpg"), 0.5)
        self.shadowImage = pygame.transform.smoothscale_by(pygame.image.load(self.IMG_PATH + "shadow.png"), (0.4, 0.28))
        self.shadowImage.set_alpha(128)

        self.healthbarBlue = pygame.transform.smoothscale_by(pygame.image.load(self.IMG_PATH + "healthbar-blue.png"), 1.6)
        self.healthbarRed = pygame.transform.smoothscale_by(pygame.image.load(self.IMG_PATH + "healthbar-red.png"), (1.75, 1.61))

        self.destroyedTower = pygame.transform.smoothscale_by(pygame.image.load(self.IMG_PATH + "destroyed.png"), 2.3)

        self.imagesByTroop = {
            "GIANT": pygame.transform.smoothscale_by(pygame.image.load(self.IMG_PATH + "giant-walk.png"), 0.6),
            "SKELETON": pygame.transform.smoothscale_by(pygame.image.load(self.IMG_PATH + "skeleton.png"), 1.5),
            "KNIGHT":  pygame.transform.smoothscale_by(pygame.image.load(self.IMG_PATH + "knight.png"), 1.5)
        }

        self.fpsHistory = []

    # Return False if UI has terminated this frame
    def Tick(self, dt, troops, projectiles, towers) -> bool:
        self.win.blit(self.bgImage, (-415, 0))

        # Fill with transparent
        self.surfaceHD.fill((0, 0, 0, 0))
        self.shadowLayer.fill((0, 0, 0, 0))

        for tower in towers:
            if tower.dead:
                self.surfaceHD.blit(self.destroyedTower, (tower.x * 4 - 130, tower.y * 4 - 60))
                continue

            if not tower.active: continue

            drawY = tower.y * 4 + 90

            if not tower.owner.isFocused:
                drawY -= 170

            self.DrawHealthBar(tower.x * 4 - 120, drawY, tower)

        for t in troops:
            self.DrawTroop(t)

        for p in projectiles:
            self.DrawProjectile(p)

        scaledHD = pygame.transform.smoothscale_by(self.surfaceHD, 0.25)
        scaledShadow = pygame.transform.smoothscale_by(self.shadowLayer, 0.25)

        self.win.blit(scaledShadow, (0, 0))
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
    
    def DrawHealthBar(self, drawX, drawY, owner) -> None:
        maxWidth = 100

        barW = int(maxWidth * (owner.health / owner.maxHealth))
        barX = drawX + 80
        barY = drawY

        colour = (52, 146, 235) # Blue
        drawImg = self.healthbarBlue

        if not owner.owner.isFocused:
            barY -= 8
            barX += 4

            colour = (217, 33, 51) # Red
            drawImg = self.healthbarRed

        # Only draw level if not damaged
        if owner.health == owner.maxHealth:
            # Don't even draw level on towers
            if not hasattr(owner, "active"):
                self.surfaceHD.blit(drawImg, (drawX + 20, drawY - 30), (0, 0, 60, 100))
        else:
            self.surfaceHD.blit(drawImg, (drawX + 20, drawY - 30))

            pygame.draw.rect(self.surfaceHD, (50, 50, 60), (barX, barY, maxWidth, 16), border_radius=3)
            pygame.draw.rect(self.surfaceHD, colour, (barX, barY, barW, 16), border_radius=3)

    def DrawTroop(self, troop) -> None:
        troopImg = self.imagesByTroop[troop.troopType.name]

        troopImg = pygame.transform.rotate(troopImg, troop.direction - 90)

        width = troopImg.get_width()
        height = troopImg.get_height()

        drawX = troop.x * 4 - width // 2
        drawY = troop.y * 4 - height // 2

        scaledShadow = pygame.transform.smoothscale_by(self.shadowImage, width/270)

        self.shadowLayer.blit(scaledShadow, (drawX, drawY + 60))
        self.surfaceHD.blit(troopImg, (drawX, drawY))

        self.DrawHealthBar(drawX, drawY, troop)

    def DrawProjectile(self, projectile) -> None:
        projectileSurface = pygame.Surface((48, 16), pygame.SRCALPHA)
        pygame.draw.rect(projectileSurface, (30, 30, 32), (0, 0, 48, 16), border_radius=2)
        
        rotatedSurface = pygame.transform.rotate(projectileSurface, -projectile.dir.as_polar()[1])
        
        rect = rotatedSurface.get_rect(center=(projectile.x*4, projectile.y*4))
        
        self.surfaceHD.blit(rotatedSurface, rect)