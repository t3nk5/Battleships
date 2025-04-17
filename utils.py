import random
import pygame




def createGameGrid(rows, cols, cellsize, pos):
    startX = pos[0]
    startY = pos[1]
    coordGrid = []
    for row in range(rows):
        rowX = []
        for col in range(cols):
            rowX.append((startX, startY))
            startX += cellsize
        coordGrid.append(rowX)
        startX = pos[0]
        startY += cellsize
    return coordGrid

def createGameLogic(rows, cols):
    gamelogic = []
    for row in range(rows):
        rowX = []
        for col in range(cols):
            rowX.append(' ')
        gamelogic.append(rowX)
    return gamelogic

def updateGameLogic(coordGrid, shiplist, gamelogic):
    for i, rowX in enumerate(coordGrid):
        for j, colX in enumerate(rowX):
            if gamelogic[i][j] == 'T' or gamelogic[i][j] == 'X':
                continue
            else:
                gamelogic[i][j] = ' '
                for ship in shiplist:
                    if pygame.rect.Rect(colX[0], colX[1], CELLSIZE, CELLSIZE).colliderect(ship.rect):
                        gamelogic[i][j] = 'O'

def showGridOnScreen(window, cellsize, playerGrid, computerGrid):
    gamegrids = [playerGrid, computerGrid]
    for grid in gamegrids:
        for row in grid:
            for col in row:
                pygame.draw.rect(window, (255, 255, 255), (col[0], col[1], cellsize, cellsize), 1)

def printGameLogic():
    print('Player Grid'.center(50, '#'))
    for _ in pGameLogic:
        print(_)
    print('Computer Grid'.center(50, '#'))
    for _ in cGameLogic:
        print(_)

def loadImage(path, size, rotate=False):
    img = pygame.image.load(path).convert_alpha()
    img = pygame.transform.scale(img, size)
    if rotate == True:
        img = pygame.transform.rotate(img, -90)
    return img

def loadAnimationImages(path, aniNum,  size):
    imageList = []
    for num in range(aniNum):
        if num < 10:
            imageList.append(loadImage(f'{path}00{num}.png', size))
        elif num < 100:
            imageList.append(loadImage(f'{path}0{num}.png', size))
        else:
            imageList.append(loadImage(f'{path}{num}.png', size))
    return imageList

def loadSpriteSheetImages(spriteSheet, rows, cols, newSize, size):
    image = pygame.Surface((128, 128))
    image.blit(spriteSheet, (0, 0), (rows * size[0], cols * size[1], size[0], size[1]))
    image = pygame.transform.scale(image, (newSize[0], newSize[1]))
    image.set_colorkey((0, 0, 0))
    return image

def increaseAnimationImage(imageList, ind):
    return imageList[ind]



def sortFleet(ship, shiplist):
    shiplist.remove(ship)
    shiplist.append(ship)

def randomizeShipPositions(shiplist, gamegrid):
    placedShips = []
    for i, ship in enumerate(shiplist):
        validPosition = False
        while validPosition == False:
            ship.returnToDefaultPosition()
            rotateShip = random.choice([True, False])
            if rotateShip == True:
                yAxis = random.randint(0, 9)
                xAxis = random.randint(0, 9 - (ship.hImage.get_width()//50))
                ship.rotateShip(True)
                ship.rect.topleft = gamegrid[yAxis][xAxis]
            else:
                yAxis = random.randint(0, 9 - (ship.vImage.get_height()//50))
                xAxis = random.randint(0, 9)
                ship.rect.topleft = gamegrid[yAxis][xAxis]
            if len(placedShips) > 0:
                for item in placedShips:
                    if ship.rect.colliderect(item.rect):
                        validPosition = False
                        break
                    else:
                        validPosition = True
            else:
                validPosition = True
        placedShips.append(ship)

def deploymentPhase(deployment):
    if deployment == True:
        return False
    else:
        return True

def pick_random_ship_location(gameLogic):
    validChoice = False
    while not validChoice:
        posX = random.randint(0, 9)
        posY = random.randint(0, 9)
        if gameLogic[posX][posY] == 'O':
            validChoice = True

    return (posX, posY)


def displayRadarScanner(imagelist, indnum, SCANNER):
    if SCANNER == True and indnum <= 359:
        image = increaseAnimationImage(imagelist, indnum)
        return image
    else:
        return False








CELLSIZE = 50
ROWS = 10
COLS = 10


pGameLogic = createGameLogic(ROWS, COLS)

cGameLogic = createGameLogic(ROWS, COLS)

