import pygame
import random

from utils import COLS, ROWS, CELLSIZE, createGameGrid, createGameLogic, printGameLogic, updateGameLogic, loadImage, loadSpriteSheetImages, increaseAnimationImage, loadAnimationImages, sortFleet, pGameLogic, cGameLogic, randomizeShipPositions, deploymentPhase, pick_random_ship_location, takeTurns, checkForWinners, shipLabelMaker, displayShipNames


pygame.init()


class Ship:
    def __init__(self, name, img, pos, size, numGuns=0, gunPath=None, gunsize=None, gunCoordsOffset=None):
        self.name = name
        self.pos = pos
        #  Load the Vertical image
        self.vImage = loadImage(img, size)
        self.vImageWidth = self.vImage.get_width()
        self.vImageHeight = self.vImage.get_height()
        self.vImageRect = self.vImage.get_rect()
        self.vImageRect.topleft = pos
        #  Load the Horizontal image
        self.hImage = pygame.transform.rotate(self.vImage, -90)
        self.hImageWidth = self.hImage.get_width()
        self.hImageHeight = self.hImage.get_height()
        self.hImageRect = self.hImage.get_rect()
        self.hImageRect.topleft = pos
        #  Image and Rectangle
        self.image = self.vImage
        self.rect = self.vImageRect
        self.rotation = False
        #  Ship is current selection
        self.active = False
        #  Load gun Images
        self.gunslist = []
        if numGuns > 0:
            self.gunCoordsOffset = gunCoordsOffset
            for num in range(numGuns):
                self.gunslist.append(
                    Guns(gunPath,
                         self.rect.center,
                         (size[0] * gunsize[0],
                          size[1] * gunsize[1]),
                         self.gunCoordsOffset[num])
                )


    def selectShipAndMove(self):
        while self.active == True:
            self.rect.center = pygame.mouse.get_pos()
            updateGameScreen(GAMESCREEN, GAMESTATE)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.checkForCollisions(pFleet):
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

            elif self.rect.right > gridCoords[0][-1][0]+50:
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
                        self.rect.topleft = (cell[0] + (CELLSIZE - self.image.get_width())//2, cell[1])
                    else:
                        self.rect.topleft = (cell[0], cell[1] + (CELLSIZE - self.image.get_height())//2)

        self.hImageRect.center = self.vImageRect.center = self.rect.center


    def draw(self, window):
        window.blit(self.image, self.rect)
        for guns in self.gunslist:
            guns.draw(window, self)


class Guns:
    def __init__(self, imgPath, pos, size, offset):
        self.orig_image = loadImage(imgPath, size, True)
        self.image = self.orig_image
        self.offset = offset
        self.rect = self.image.get_rect(center=pos)


    def update(self, ship):
        self.rotateGuns(ship)
        if ship.rotation == False:
            self.rect.center = (ship.rect.centerx, ship.rect.centery + (ship.image.get_height()//2 * self.offset))
        else:
            self.rect.center = (ship.rect.centerx + (ship.image.get_width()//2 * -self.offset), ship.rect.centery)


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


    def draw(self, window, ship):
        self.update(ship)
        window.blit(self.image, self.rect)


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
        message = font.render(msg, 1, (255,255,255))
        return message


    def focusOnButton(self, window):
        if self.active:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                window.blit(self.imageLarger, (self.rect[0] - 5, self.rect[1] - 5, self.rect[2], self.rect[3]))
            else:
                window.blit(self.image, self.rect)


    def actionOnPress(self):
        if self.active:
            if self.name == 'Randomize':
                self.randomizeShipPositions(pFleet, pGameGrid)
                self.randomizeShipPositions(cFleet, cGameGrid)
            elif self.name == 'Deploy':
                self.deploymentPhase()
            elif self.name == 'Quit':
                pass


    def randomizeShipPositions(self, shiplist, gameGrid):
        if DEPLOYMENT == True:
            randomizeShipPositions(shiplist, gameGrid)


    def resetShips(self, shiplist):
        if DEPLOYMENT == True:
            for ship in shiplist:
                ship.returnToDefaultPosition()


    def deploymentPhase(self):
        pass


    def restartTheGame(self):
        TOKENS.clear()
        self.resetShips(pFleet)
        self.randomizeShipPositions(cFleet, cGameGrid)
        updateGameLogic(cGameGrid, cFleet, cGameLogic)
        updateGameLogic(pGameGrid, pFleet, pGameLogic)


    def updateButtons(self, gameStatus):
        if self.name == 'Deploy' and gameStatus == False:
            self.name = ' '
        if self.name == 'Randomize' and gameStatus == False:
            self.name = ' '
        elif self.name == 'Quit' and gameStatus == True:
            self.name = ' '
        self.msg = self.addText(self.name)
        self.msgRect = self.msg.get_rect(center=self.rect.center)


    def draw(self, window):
        self.updateButtons(DEPLOYMENT)
        self.focusOnButton(window)
        window.blit(self.msg, self.msgRect)


class Player:
    def __init__(self):
        self.turn = True

    def makeAttack(self, grid, logicgrid):
        posX, posY = pygame.mouse.get_pos()
        if posX >= grid[0][0][0] and posX <= grid[0][-1][0] + 50 and posY >= grid[0][0][1] and posY <= grid[-1][0][1] + 50:
            for i, rowX in enumerate(grid):
                for j, colX in enumerate(rowX):
                    if posX >= colX[0] and posX < colX[0] + 50 and posY >= colX[1] and posY <= colX[1] + 50:
                        if logicgrid[i][j] != ' ':
                            if logicgrid[i][j] == 'O':
                                TOKENS.append(Tokens(REDTOKEN, grid[i][j], 'Hit', None, None, None))
                                logicgrid[i][j] = 'T'
                                SHOTSOUND.play()
                                HITSOUND.play()
                                self.turn = False
                        else:
                            logicgrid[i][j] = 'X'
                            SHOTSOUND.play()
                            MISSSOUND.play()
                            TOKENS.append(Tokens(GREENTOKEN, grid[i][j], 'Miss', None, None, None))
                            self.turn = False


class EasyComputer:
    def __init__(self):
        self.turn = False
        self.status = self.computerStatus('Thinking')
        self.name = 'Easy Computer'


    def computerStatus(self, msg):
        image = pygame.font.SysFont('Stencil', 22)
        message = image.render(msg, 1, (0, 0, 0))
        return message


    def makeAttack(self, gamelogic):
        COMPTURNTIMER = pygame.time.get_ticks()
        if COMPTURNTIMER - TURNTIMER >= 3000:
            validChoice = False
            while not validChoice:
                rowX = random.randint(0, 9)
                colX = random.randint(0, 9)

                if gamelogic[rowX][colX] == ' ' or gamelogic[rowX][colX] == 'O':
                    validChoice = True

            if gamelogic[rowX][colX] == 'O':
                TOKENS.append(Tokens(REDTOKEN, pGameGrid[rowX][colX], 'Hit', FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST, None))
                gamelogic[rowX][colX] = 'T'
                SHOTSOUND.play()
                HITSOUND.play()
                self.turn = False
            else:
                gamelogic[rowX][colX] = 'X'
                TOKENS.append(Tokens(BLUETOKEN, pGameGrid[rowX][colX], 'Miss', None, None, None))
                SHOTSOUND.play()
                MISSSOUND.play()
                self.turn = False
        return self.turn


    def draw(self, window):
        if self.turn:
            window.blit(self.status, (cGameGrid[0][0][0] - CELLSIZE, cGameGrid[-1][-1][1] + CELLSIZE))


class Tokens:
    def __init__(self, image, pos, action, imageList=None, explosionList=None, soundFile=None):
        self.image = image
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.topleft = self.pos
        self.imageList = imageList
        self.explosionList = explosionList
        self.action = action
        self.soundFile = soundFile
        self.timer = pygame.time.get_ticks()
        self.imageIndex = 0
        self.explosionIndex = 0
        self.explosion = False


    def animate_Explosion(self):
        self.explosionIndex += 1
        if self.explosionIndex < len(self.explosionList):
            return self.explosionList[self.explosionIndex]
        else:
            return self.animate_fire()


    def animate_fire(self):
        if pygame.time.get_ticks() - self.timer >= 100:
            self.timer = pygame.time.get_ticks()
            self.imageIndex += 1
        if self.imageIndex < len(self.imageList):
            return self.imageList[self.imageIndex]
        else:
            self.imageIndex = 0
            return self.imageList[self.imageIndex]


    def draw(self, window):
        if not self.imageList:
            window.blit(self.image, self.rect)
        else:
            self.image = self.animate_Explosion()
            self.rect = self.image.get_rect(topleft=self.pos)
            self.rect[1] = self.pos[1] - 10
            window.blit(self.image, self.rect)

def createFleet():
    fleet = []
    for name in FLEET.keys():
        fleet.append(
            Ship(name,
                 FLEET[name][1],
                 FLEET[name][2],
                 FLEET[name][3],
                 FLEET[name][4],
                 FLEET[name][5],
                 FLEET[name][6],
                 FLEET[name][7])
        )
    return fleet

def mainMenuScreen(window):
    window.fill((0, 0, 0))
    window.blit(MAINMENUIMAGE, (0, 0))

    for button in BUTTONS:
        if button.name in ['Easy Computer', 'Hard Computer']:
            button.active = True
            button.draw(window)
        else:
            button.active = False

def deploymentScreen(window):
    window.fill((0, 0, 0))
    window.blit(BACKGROUND, (0, 0))
    window.blit(PGAMEGRIDIMG, (0, 0))
    window.blit(CGAMEGRIDIMG, (cGameGrid[0][0][0] - 50, cGameGrid[0][0][1] - 50))

    for ship in pFleet:
        ship.draw(window)
        ship.snapToGridEdge(pGameGrid)
        ship.snapToGrid(pGameGrid)

    displayShipNames(window)

    for ship in cFleet:
        ship.snapToGridEdge(cGameGrid)
        ship.snapToGrid(cGameGrid)

    for button in BUTTONS:
        if button.name in ['Randomize', 'Deploy', 'Quit']:
            button.active = True
            button.draw(window)
        else:
            button.active = False

    computer.draw(window)

    
    for token in TOKENS:
        token.draw(window)

    updateGameLogic(pGameGrid, pFleet, pGameLogic)
    updateGameLogic(cGameGrid, cFleet, cGameLogic)

def endScreen(window):
    window.fill((0, 0, 0))
    window.blit(ENDSCREENIMAGE, (0, 0))

    for button in BUTTONS:
        if button.name in ['Easy Computer', 'Hard Computer', 'Quit']:
            button.active = True
            button.draw(window)
        else:
            button.active = False

def updateGameScreen(window, GAMESTATE):
    if GAMESTATE == 'Main Menu':
        mainMenuScreen(window)
    elif GAMESTATE == 'Deployment':
        deploymentScreen(window)
    elif GAMESTATE == 'Game Over':
        endScreen(window)

    pygame.display.update()

SCREENWIDTH = 1260
SCREENHEIGHT = 960

DEPLOYMENT = True
SCANNER = False
INDNUM = 0
BLIPPOSITION = None
TURNTIMER = pygame.time.get_ticks()
GAMESTATE = 'Main Menu'


GAMESCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
pygame.display.set_caption('Battle Ship')

FLEET = {
    'battleship': ['battleship', 'ui/assets/images/ships/battleship/battleship.png', (125, 600), (40, 195),
                   4, 'ui/assets/images/ships/battleship/battleshipgun.png', (0.4, 0.125), [-0.525, -0.34, 0.67, 0.49]],
    'cruiser': ['cruiser', 'ui/assets/images/ships/cruiser/cruiser.png', (200, 600), (40, 195),
                2, 'ui/assets/images/ships/cruiser/cruisergun.png', (0.4, 0.125), [-0.36, 0.64]],
    'destroyer': ['destroyer', 'ui/assets/images/ships/destroyer/destroyer.png', (275, 600), (30, 145),
                  2, 'ui/assets/images/ships/destroyer/destroyergun.png', (0.5, 0.15), [-0.52, 0.71]],
    'patrol boat': ['patrol boat', 'ui/assets/images/ships/patrol boat/patrol boat.png', (425, 600), (20, 95),
                    0, '', None, None],
    'submarine': ['submarine', 'ui/assets/images/ships/submarine/submarine.png', (350, 600), (30, 145),
                  1, 'ui/assets/images/ships/submarine/submarinegun.png', (0.25, 0.125), [-0.45]],
    'carrier': ['carrier', 'ui/assets/images/ships/carrier/carrier.png', (50, 600), (45, 245),
                0, '', None, None],
    'rescue ship': ['rescue ship', 'ui/assets/images/ships/rescue ship/rescue ship.png', (500, 600), (20, 95),
                    0, '', None, None]
}
STAGE = ['Main Menu', 'Deployment', 'Game Over']

pGameGrid = createGameGrid(ROWS, COLS, CELLSIZE, (50, 50))

pFleet = createFleet()

cGameGrid = createGameGrid(ROWS, COLS, CELLSIZE, (SCREENWIDTH - (ROWS * CELLSIZE), 50))

cFleet = createFleet()
randomizeShipPositions(cFleet, cGameGrid)

printGameLogic()

MAINMENUIMAGE = loadImage('ui/assets/images/background/Battleship.jpg', (SCREENWIDTH // 3 * 2, SCREENHEIGHT))
ENDSCREENIMAGE = loadImage('ui/assets/images/background/Carrier.jpg', (SCREENWIDTH, SCREENHEIGHT))
BACKGROUND = loadImage('ui/assets/images/background/gamebg.png', (SCREENWIDTH, SCREENHEIGHT))
PGAMEGRIDIMG = loadImage('ui/assets/images/grids/player_grid.png', ((ROWS + 1) * CELLSIZE, (COLS + 1) * CELLSIZE))
CGAMEGRIDIMG = loadImage('ui/assets/images/grids/comp_grid.png', ((ROWS + 1) * CELLSIZE, (COLS + 1) * CELLSIZE))
BUTTONIMAGE = loadImage('ui/assets/images/buttons/button.png', (150, 50))
BUTTONIMAGE1 = loadImage('ui/assets/images/buttons/button.png', (250, 100))
BUTTONS = [
    Button(BUTTONIMAGE, (150, 50), (25, 900), 'Randomize'),
    Button(BUTTONIMAGE, (150, 50), (375, 900), 'Deploy'),
    Button(BUTTONIMAGE1, (250, 100), (900, SCREENHEIGHT // 2 - 150), 'Easy Computer'),
    Button(BUTTONIMAGE1, (250, 100), (900, SCREENHEIGHT // 2 + 150), 'Hard Computer')
]
REDTOKEN = loadImage('ui/assets/images/tokens/redtoken.png', (CELLSIZE, CELLSIZE))
GREENTOKEN = loadImage('ui/assets/images/tokens/greentoken.png', (CELLSIZE, CELLSIZE))
BLUETOKEN = loadImage('ui/assets/images/tokens/bluetoken.png', (CELLSIZE, CELLSIZE))
FIRETOKENIMAGELIST = loadAnimationImages('ui/assets/images/tokens/fireloop/fire1_ ', 13, (CELLSIZE, CELLSIZE))
EXPLOSIONSPRITESHEET = pygame.image.load('ui/assets/images/tokens/explosion/explosion.png').convert_alpha()
EXPLOSIONIMAGELIST = []
for row in range(8):
    for col in range(8):
        EXPLOSIONIMAGELIST.append(loadSpriteSheetImages(EXPLOSIONSPRITESHEET, col, row, (CELLSIZE, CELLSIZE), (128, 128)))
TOKENS = []
RADARGRIDIMAGES = loadAnimationImages('ui/assets/images/radar_base/radar_anim', 360, (ROWS * CELLSIZE, COLS * CELLSIZE))
RADARBLIPIMAGES = loadAnimationImages('ui/assets/images/radar_blip/Blip_', 11, (50, 50))
RADARGRID = loadImage('ui/assets/images/grids/grid_faint.png', ((ROWS) * CELLSIZE, (COLS) * CELLSIZE))
HITSOUND = pygame.mixer.Sound('ui/assets/sounds/explosion.wav')
HITSOUND.set_volume(0.05)
SHOTSOUND = pygame.mixer.Sound('ui/assets/sounds/gunshot.wav')
SHOTSOUND.set_volume(0.05)
MISSSOUND = pygame.mixer.Sound('ui/assets/sounds/splash.wav')
MISSSOUND.set_volume(0.05)

player1 = Player()
computer = EasyComputer()

RUNGAME = True
if __name__ == '__main__':
    while RUNGAME:


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUNGAME = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if DEPLOYMENT == True:
                        for ship in pFleet:
                            if ship.rect.collidepoint(pygame.mouse.get_pos()):
                                ship.active = True
                                sortFleet(ship, pFleet)
                                ship.selectShipAndMove()

                    else:
                        if player1.turn == True:
                            player1.makeAttack(cGameGrid, cGameLogic)
                            if player1.turn == False:
                                TURNTIMER = pygame.time.get_ticks()

                    for button in BUTTONS:
                        if button.rect.collidepoint(pygame.mouse.get_pos()):
                            if button.name == 'Deploy' and button.active == True:
                                status = deploymentPhase(DEPLOYMENT)
                                DEPLOYMENT = status
                            elif button.name == 'Quit' and button.active == True:
                                RUNGAME = False
                            elif (button.name == 'Easy Computer' or button.name == 'Hard Computer') and button.active == True:
                                if button.name == 'Easy Computer':
                                    computer = EasyComputer()

                                elif button.name == 'Hard Computer':
                                    ##ia vs ia a mettre ici
                                    pass
                                if GAMESTATE == 'Game Over':
                                    TOKENS.clear()
                                    for ship in pFleet:
                                        ship.returnToDefaultPosition()
                                    randomizeShipPositions(cFleet, cGameGrid)
                                    
                                    updateGameLogic(pGameGrid, pFleet, pGameLogic)
                                    updateGameLogic(cGameGrid, cFleet, cGameLogic)
                                    status = deploymentPhase(DEPLOYMENT)
                                    DEPLOYMENT = status
                                GAMESTATE = STAGE[1]
                            button.actionOnPress()

                elif event.button == 2:
                    printGameLogic()


                elif event.button == 3:
                    if DEPLOYMENT == True:
                        for ship in pFleet:
                            if ship.rect.collidepoint(pygame.mouse.get_pos()) and not ship.checkForRotateCollisions(pFleet):
                                ship.rotateShip(True)

        updateGameScreen(GAMESCREEN, GAMESTATE)
        if SCANNER == True:
            INDNUM += 1

        if GAMESTATE == 'Deployment' and DEPLOYMENT != True:
            player1Wins = checkForWinners(cGameLogic)
            computerWins = checkForWinners(pGameLogic)
            if player1Wins == True or computerWins == True:
                GAMESTATE = STAGE[2]

        takeTurns(player1, computer)

    pygame.quit()
