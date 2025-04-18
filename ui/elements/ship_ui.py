from __future__ import annotations

from dataclasses import dataclass

import pygame
from game.board.battleships import Battleship, Carrier, Destroyer, PatrolBoat, Ship, Submarine
from ui.assets.images import loadImage
from ui.assets.screen import CELLSIZE, Window
from ui.elements.gun import Gun


# from ui.ui_manager import UIManager


@dataclass
class ShipUIValues:
    related_class: type[Ship]
    image: str
    initial_position: tuple[int, int]
    img_size: tuple[int, int]
    num_guns: int
    gun_img_path: str | None = None
    gun_img_size: tuple[float, float] | None = None
    guns_coords_offset: list[float] | None = None


FLEET: dict[str, 'ShipUIValues'] = {
    'battleship': ShipUIValues(
        related_class=Battleship,
        image='ui/assets/images/ships/battleship/battleship.png',
        initial_position=(125, 600),
        img_size=(40, 195),
        num_guns=4,
        gun_img_path='ui/assets/images/ships/battleship/battleshipgun.png',
        gun_img_size=(0.4, 0.125),
        guns_coords_offset=[-0.525, -0.34, 0.67, 0.49],
    ),
    'cruiser': ShipUIValues(
        related_class=Ship,  # change ship type
        image='ui/assets/images/ships/cruiser/cruiser.png',
        initial_position=(200, 600),
        img_size=(40, 195),
        num_guns=2,
        gun_img_path='ui/assets/images/ships/cruiser/cruisergun.png',
        gun_img_size=(0.4, 0.125),
        guns_coords_offset=[-0.36, 0.64],
    ),
    'destroyer': ShipUIValues(
        related_class=Destroyer,
        image='ui/assets/images/ships/destroyer/destroyer.png',
        initial_position=(275, 600),
        img_size=(30, 145),
        num_guns=2,
        gun_img_path='ui/assets/images/ships/destroyer/destroyergun.png',
        gun_img_size=(0.5, 0.15),
        guns_coords_offset=[-0.52, 0.71],
    ),
    'patrol boat': ShipUIValues(
        related_class=PatrolBoat,
        image='ui/assets/images/ships/patrol boat/patrol boat.png',
        initial_position=(425, 600),
        img_size=(20, 95),
        num_guns=0,
    ),
    'submarine': ShipUIValues(
        related_class=Submarine,
        image='ui/assets/images/ships/submarine/submarine.png',
        initial_position=(350, 600),
        img_size=(30, 145),
        num_guns=1,
        gun_img_path='ui/assets/images/ships/submarine/submarinegun.png',
        gun_img_size=(0.25, 0.125),
        guns_coords_offset=[-0.45],
    ),
    'carrier': ShipUIValues(
        related_class=Carrier,
        image='ui/assets/images/ships/carrier/carrier.png',
        initial_position=(50, 600),
        img_size=(45, 245),
        num_guns=0,
    ),
    'rescue ship': ShipUIValues(
        related_class=Ship,  # change ship type
        image='ui/assets/images/ships/rescue ship/rescue ship.png',
        initial_position=(500, 600),
        img_size=(20, 95),
        num_guns=0,
    ),
}
SHIP_TYPES_NAMES = list(FLEET.keys())


class ShipUI:
    @staticmethod
    def createFleet():
        return [ShipUI(values) for _, values in FLEET.items()]

    def __init__(self, values: ShipUIValues):
        self.related_class = values.related_class
        self.pos = values.initial_position
        #  Load the Vertical image
        self.vImage = loadImage(values.image, values.img_size)
        self.vImageWidth = self.vImage.get_width()
        self.vImageHeight = self.vImage.get_height()
        self.vImageRect = self.vImage.get_rect()
        self.vImageRect.topleft = values.initial_position
        #  Load the Horizontal image
        self.hImage = pygame.transform.rotate(self.vImage, -90)
        self.hImageWidth = self.hImage.get_width()
        self.hImageHeight = self.hImage.get_height()
        self.hImageRect = self.hImage.get_rect()
        self.hImageRect.topleft = values.initial_position
        #  Image and Rectangle
        self.image = self.vImage
        self.rect = self.vImageRect
        self.rotation = False
        #  Ship is current selection
        self.active = False
        #  Load gun Images
        self.gunCoordsOffset = values.guns_coords_offset
        self.gunslist: list[Gun] = [
            Gun(
                values.gun_img_path,
                self.rect.center,
                (values.img_size[0] * values.gun_img_size[0],
                 values.img_size[1] * values.gun_img_size[1]),
                self.gunCoordsOffset[num]
            )
            for num in range(values.num_guns)
        ] if values.num_guns > 0 else []

    def select_ship_and_move(self, ui: UIManager):
        while self.active == True:
            self.rect.center = pygame.mouse.get_pos()
            ui.update_game_screen()
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.checkForCollisions(ui.pFleet):
                        if event.button == 1:
                            self.hImageRect.center = self.vImageRect.center = self.rect.center
                            self.active = False
                    if event.button == 3:
                        self.rotateShip()

    def rotateShip(self, doRotation=False):
        if self.active or doRotation == True:
            if self.rotation == False:
                self.rotation = True
            else:
                self.rotation = False
            self.switchImageAndRect()

    def switchImageAndRect(self):
        if self.rotation == True:
            self.image = self.hImage
            self.rect = self.hImageRect
        else:
            self.image = self.vImage
            self.rect = self.vImageRect
        self.hImageRect.center = self.vImageRect.center = self.rect.center

    def checkForCollisions(self, shiplist):
        slist = shiplist.copy()
        slist.remove(self)
        for item in slist:
            if self.rect.colliderect(item.rect):
                return True
        return False

    def checkForRotateCollisions(self, shiplist):
        slist = shiplist.copy()
        slist.remove(self)
        for ship in slist:
            if self.rotation == True:
                if self.vImageRect.colliderect(ship.rect):
                    return True
            else:
                if self.hImageRect.colliderect(ship.rect):
                    return True
        return False

    def returnToDefaultPosition(self):
        if self.rotation == True:
            self.rotateShip(True)

        self.rect.topleft = self.pos
        self.hImageRect.center = self.vImageRect.center = self.rect.center

    def snapToGridEdge(self, gridCoords):
        if self.rect.topleft != self.pos:

            if self.rect.left > gridCoords[0][-1][0] + 50 or \
                    self.rect.right < gridCoords[0][0][0] or \
                    self.rect.top > gridCoords[-1][0][1] + 50 or \
                    self.rect.bottom < gridCoords[0][0][1]:
                self.returnToDefaultPosition()

            elif self.rect.right > gridCoords[0][-1][0] + 50:
                self.rect.right = gridCoords[0][-1][0] + 50
            elif self.rect.left < gridCoords[0][0][0]:
                self.rect.left = gridCoords[0][0][0]
            elif self.rect.top < gridCoords[0][0][1]:
                self.rect.top = gridCoords[0][0][1]
            elif self.rect.bottom > gridCoords[-1][0][1] + 50:
                self.rect.bottom = gridCoords[-1][0][1] + 50
            self.vImageRect.center = self.hImageRect.center = self.rect.center

    def snapToGrid(self, gridCoords):
        for rowX in gridCoords:
            for cell in rowX:
                if self.rect.left >= cell[0] and self.rect.left < cell[0] + CELLSIZE \
                        and self.rect.top >= cell[1] and self.rect.top < cell[1] + CELLSIZE:
                    if self.rotation == False:
                        self.rect.topleft = (cell[0] + (CELLSIZE - self.image.get_width()) // 2, cell[1])
                    else:
                        self.rect.topleft = (cell[0], cell[1] + (CELLSIZE - self.image.get_height()) // 2)

        self.hImageRect.center = self.vImageRect.center = self.rect.center

    def draw(self):
        Window.screen().blit(self.image, self.rect)
        for guns in self.gunslist:
            guns.draw(self)
