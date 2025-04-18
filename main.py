import time
import pygame
import random

from game.game_class import GameLogic
from ui.player.temp_ia import EasyComputer
from ui.ui_manager import UIManager
from utils.graphics import checkForWinners, deploymentPhase, randomizeShipPositions, sortFleet, cGameLogic, pGameLogic, \
    takeTurns, updateGameLogic
from utils.prompt import Prompt, clear


def play_graphical():
    pygame.init()

    ui_manager = UIManager()
    while ui_manager.is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ui_manager.is_running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                match event.button:
                    case 1:
                        if ui_manager.in_deployment == True:
                            for ship in ui_manager.pFleet:
                                if ship.rect.collidepoint(pygame.mouse.get_pos()):
                                    ship.active = True
                                    sortFleet(ship, ui_manager.pFleet)
                                    ship.select_ship_and_move(ui_manager)
                        else:
                            if ui_manager.player1.turn == True:
                                ui_manager.player1.makeAttack(ui_manager.cGameGrid, cGameLogic, ui_manager)
                                if ui_manager.player1.turn == False:
                                    ui_manager.turn_timer = pygame.time.get_ticks()
                        for button in ui_manager.buttons:
                            if button.rect.collidepoint(pygame.mouse.get_pos()):
                                if button.name == 'Deploy' and button.active == True:
                                    ui_manager.in_deployment = deploymentPhase(ui_manager.in_deployment)
                                elif button.name == 'Quit' and button.active == True:
                                    ui_manager.is_running = False
                                elif (
                                        button.name == 'Player vs IA' or button.name == 'IA Vs IA') and button.active == True:
                                    if button.name == 'Player vs IA':
                                        ui_manager.computer = EasyComputer()
                                    elif button.name == 'IA Vs IA':
                                        # ia vs ia a mettre ici
                                        print('not implemented yet')
                                        pass
                                    if ui_manager.state == 'Game Over':
                                        ui_manager.tokens.clear()
                                        for ship in ui_manager.pFleet:
                                            ship.returnToDefaultPosition()
                                        randomizeShipPositions(ui_manager.cFleet, ui_manager.cGameGrid)

                                        updateGameLogic(ui_manager.pGameGrid, ui_manager.pFleet, pGameLogic)
                                        updateGameLogic(ui_manager.cGameGrid, ui_manager.cFleet, cGameLogic)
                                        ui_manager.in_deployment = deploymentPhase(ui_manager.in_deployment)
                                    ui_manager.state = 'Deployment'
                                button.actionOnPress(ui_manager)
                    case 2:
                        print('event button 2')
                        pass
                    case 3:
                        if ui_manager.in_deployment == True:
                            for ship in ui_manager.pFleet:
                                if ship.rect.collidepoint(pygame.mouse.get_pos()) and not ship.checkForRotateCollisions(
                                        ui_manager.pFleet):
                                    ship.rotateShip(True)

        ui_manager.update_game_screen()

        if ui_manager.state == 'Deployment' and not ui_manager.in_deployment:
            player1Wins = checkForWinners(cGameLogic)
            computerWins = checkForWinners(pGameLogic)
            if player1Wins == True or computerWins == True:
                if player1Wins == True:
                    ui_manager.computer.status = ui_manager.computer.computerStatus('Player Win')
                    continue
                elif computerWins == True:
                    ui_manager.computer.status = ui_manager.computer.computerStatus('IA WIN')
                    continue

                pygame.display.flip()
                time.sleep(5)
                ui_manager.state = 'Game Over'
        takeTurns(ui_manager.player1, ui_manager.computer, ui_manager)

    pygame.quit()


def play_terminal():
    clear(0)

    while True:
        print(f'Welcome to Battleship Game !')
        match Prompt.select(
            'Select:',
            choices=['Play a game', 'View statistics', 'Quit'],
        ).element:
            case 'Play a game':
                clear(1)
                game = GameLogic('PvP', 'terminal')
                game.initiate()
                game.play()
                game.end()
            case 'View statistics':
                print('Not Implemented yet')
            case 'Quit':
                print()
                break

    clear(2)
    print('Thanks for playing!')


if __name__ == '__main__':
    match Prompt.select(
        'Select game mode',
        ['terminal', 'graphical']
    ).element:
        case 'terminal':
            play_terminal()
        case 'graphical':
            play_graphical()
