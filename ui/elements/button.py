from __future__ import annotations

import pygame

from ui.assets.screen import Window
# from ui.ui_manager import UIManager
from utils.graphics import randomizeShipPositions, updateGameLogic, pGameLogic, cGameLogic


class Button:
    def __init__(self, image, size, pos, msg):
        self.name = msg
        self.image = image
        self.imageLarger = self.image
        self.imageLarger = pygame.transform.scale(self.imageLarger, (size[0] + 10, size[1] + 10))
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.active = False

        self.msg = self.addText(msg)
        self.msgRect = self.msg.get_rect(center=self.rect.center)

    def addText(self, msg):
        font = pygame.font.SysFont('Stencil', 22)
        message = font.render(msg, 1, (255, 255, 255))
        return message

    def focusOnButton(self):
        if self.active:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                Window.screen().blit(self.imageLarger, (self.rect[0] - 5, self.rect[1] - 5, self.rect[2], self.rect[3]))
            else:
                Window.screen().blit(self.image, self.rect)

    def actionOnPress(self, ui: UIManager):
        if self.active:
            if self.name == 'Randomize':
                self.randomizeShipPositions(ui.pFleet, ui.pGameGrid, ui)
                self.randomizeShipPositions(ui.cFleet, ui.cGameGrid, ui)
            elif self.name == 'Deploy':
                self.deploymentPhase()
            elif self.name == 'Quit':
                pass

    def randomizeShipPositions(self, shiplist, gameGrid, ui: UIManager):
        if ui.in_deployment == True:
            randomizeShipPositions(shiplist, gameGrid)

    def resetShips(self, shiplist, ui: UIManager):
        if ui.in_deployment == True:
            for ship in shiplist:
                ship.returnToDefaultPosition()

    def deploymentPhase(self):
        pass

    def restartTheGame(self, ui: UIManager):
        ui.tokens.clear()
        self.resetShips(ui.pFleet)
        self.randomizeShipPositions(ui.cFleet, ui.cGameGrid)
        updateGameLogic(ui.cGameGrid, ui.cFleet, cGameLogic)
        updateGameLogic(ui.pGameGrid, ui.pFleet, pGameLogic)

    def updateButtons(self, gameStatus):
        if self.name == 'Deploy' and gameStatus == False:
            self.name = 'Deploy'
        elif self.name == 'Randomize' and gameStatus == False:
            self.name = 'Quit'

        self.msg = self.addText(self.name)
        self.msgRect = self.msg.get_rect(center=self.rect.center)

    def draw(self, ui: UIManager):
        self.updateButtons(ui.in_deployment)
        self.focusOnButton()
        Window.screen().blit(self.msg, self.msgRect)
