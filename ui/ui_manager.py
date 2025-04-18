from typing import Literal

import pygame

from ui.assets.images import BACKGROUND, BUTTONIMAGE, BUTTONIMAGE1, CGAMEGRIDIMG, ENDSCREENIMAGE, MAINMENUIMAGE, \
    PGAMEGRIDIMG
from ui.assets.screen import CELLSIZE, COLS, ROWS, SCREENHEIGHT, SCREENWIDTH, Window
from ui.elements.button import Button
from ui.elements.ship_ui import SHIP_TYPES_NAMES, ShipUI
from ui.elements.token import Token
from ui.game_ui import GameUI
from ui.player.player_ui import PlayerUI
from ui.player.temp_ia import EasyComputer
from ui.player.temp_player import Player
from utils.graphics import createGameGrid, updateGameLogic, pGameLogic, cGameLogic


class UIManager():
    def __init__(self):
        self.is_running: bool = True
        self.state: Literal['Main Menu', 'Deployment', 'Game Over'] = 'Main Menu'
        self.game: GameUI | None = None
        self.turn_timer = pygame.time.get_ticks()
        self.buttons = [
            Button(BUTTONIMAGE, (150, 50), (25, 900), 'Randomize'),
            Button(BUTTONIMAGE, (150, 50), (375, 900), 'Deploy'),
            Button(BUTTONIMAGE1, (250, 100), (900, SCREENHEIGHT // 2 - 150), 'Player vs IA'),
            Button(BUTTONIMAGE1, (250, 100), (900, SCREENHEIGHT // 2 + 150), 'IA Vs IA')
        ]
        self.tokens: list[Token] = []

        self.in_deployment = True
        self.pGameGrid = createGameGrid(ROWS, COLS, CELLSIZE, (50, 50))
        self.pFleet = ShipUI.createFleet()
        self.cGameGrid = createGameGrid(ROWS, COLS, CELLSIZE, (SCREENWIDTH - (ROWS * CELLSIZE), 50))
        self.cFleet = ShipUI.createFleet()
        self.player1 = Player()
        self.computer = EasyComputer()

    @staticmethod
    def display_game_message(msg: str):
        image = pygame.font.SysFont('Stencil', 22)
        message = image.render(msg, 1, (0, 0, 0))
        return message

    @staticmethod
    def ship_label_maker(msg: str):
        text = pygame.font.SysFont('Stencil', 22).render(msg, 1, (0, 17, 167))
        text = pygame.transform.rotate(text, 90)
        return text

    def display_ship_names(self):
        ship_labels = [self.ship_label_maker(ship_type_name) for ship_type_name in SHIP_TYPES_NAMES]

        startPos = 25
        for item in ship_labels:
            Window.screen().blit(item, (startPos, 600))
            startPos += 75

    def update_game_screen(self):
        match self.state:
            case 'Main Menu':
                self.__main_menu_screen()
            case 'Deployment':
                self.__deployment_screen()
            case 'Game Over':
                self.__end_screen()
        pygame.display.update()

    def __main_menu_screen(self):
        Window.screen().fill((0, 0, 0))
        Window.screen().blit(MAINMENUIMAGE, (0, 0))

        for button in self.buttons:
            if button.name in ['Player vs IA', 'IA Vs IA']:
                button.active = True
                button.draw(self)
            else:
                button.active = False

    def __deployment_screen(self):
        Window.screen().fill((0, 0, 0))
        Window.screen().blit(BACKGROUND, (0, 0))
        Window.screen().blit(PGAMEGRIDIMG, (0, 0))
        Window.screen().blit(CGAMEGRIDIMG, (self.cGameGrid[0][0][0] - 50, self.cGameGrid[0][0][1] - 50))

        for ship in self.pFleet:
            ship.draw()
            ship.snapToGridEdge(self.pGameGrid)
            ship.snapToGrid(self.pGameGrid)

        self.display_ship_names()

        for ship in self.cFleet:
            ship.snapToGridEdge(self.cGameGrid)
            ship.snapToGrid(self.cGameGrid)

        for button in self.buttons:
            if button.name in ['Randomize', 'Deploy', 'Quit']:
                button.active = True
                button.draw(self)
            else:
                button.active = False

        self.computer.draw(self)

        for token in self.tokens:
            token.draw()

        updateGameLogic(self.pGameGrid, self.pFleet, pGameLogic)
        updateGameLogic(self.cGameGrid, self.cFleet, cGameLogic)

    def __end_screen(self):
        Window.screen().fill((0, 0, 0))
        Window.screen().blit(ENDSCREENIMAGE, (0, 0))

        for button in self.buttons:
            if button.name in ['Player vs IA', 'IA Vs IA', 'Quit']:
                button.active = True
                button.draw(self)
            else:
                button.active = False

    def play_turn(self):
        if isinstance(self.game.current_player, PlayerUI):
            self.turn_timer = pygame.time.get_ticks()
        self.game.turn()

        if self.game.next_player.defensive_grid.alive: self.__next_turn()

    def __next_turn(self):
        self.game._player_index = self.game._next_index

    # @property
    # def in_deployment(self):
    #     return self.game is not None and not self.game.in_deployment

    def quit(self):
        self.is_running = False

    def check_buttons(self):
        for button in self.buttons:
            if not button.rect.collidepoint(pygame.mouse.get_pos()) or not button.active: continue

            match button.name:
                case 'Deploy':
                    self.in_deployment = not self.in_deployment
                case 'Quit':
                    self.is_running = False
                case 'Player vs IA' | 'IA Vs IA':
                    if button.name == 'Player vs IA':
                        self.game = GameUI('PvIA')
                    elif button.name == 'IA Vs IA':
                        self.game = GameUI('PvIA')

                    if self.state == 'Game Over':
                        self.tokens.clear()
                        self.game = None
                        self.in_deployment = not self.in_deployment
                    self.state = 'Deployment'
            button.actionOnPress(self)
