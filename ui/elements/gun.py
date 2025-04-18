import pygame
from ui.assets.images import loadImage
from ui.assets.screen import Window


class Gun:
    def __init__(self, imgPath: str, pos: tuple[int, int], size: tuple[float, float], offset: float):
        self.orig_image = loadImage(imgPath, size, True)
        self.image = self.orig_image
        self.offset = offset
        self.rect = self.image.get_rect(center=pos)

    def update(self, ship):
        self.rotateGuns(ship)
        if ship.rotation == False:
            self.rect.center = (ship.rect.centerx, ship.rect.centery + (ship.image.get_height() // 2 * self.offset))
        else:
            self.rect.center = (ship.rect.centerx + (ship.image.get_width() // 2 * -self.offset), ship.rect.centery)

    def _update_image(self, angle):
        self.image = pygame.transform.rotate(self.orig_image, -angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def rotateGuns(self, ship):
        direction = pygame.math.Vector2(pygame.mouse.get_pos()) - pygame.math.Vector2(self.rect.center)
        radius, angle = direction.as_polar()
        if not ship.rotation:
            if self.rect.centery <= ship.vImageRect.centery and angle <= 0:
                self._update_image(angle)
            if self.rect.centery >= ship.vImageRect.centery and angle > 0:
                self._update_image(angle)
        else:
            if self.rect.centerx <= ship.hImageRect.centerx and (angle <= -90 or angle >= 90):
                self._update_image(angle)
            if self.rect.centerx >= ship.hImageRect.centerx and (angle >= -90 and angle <= 90):
                self._update_image(angle)

    def draw(self, ship):
        self.update(ship)
        Window.screen().blit(self.image, self.rect)
