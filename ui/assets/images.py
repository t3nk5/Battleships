import pygame

from ui.assets.screen import CELLSIZE, COLS, ROWS, SCREENHEIGHT, SCREENWIDTH


def loadImage(path, size, rotate=False):
    img = pygame.image.load(path).convert_alpha()
    img = pygame.transform.scale(img, size)
    if rotate == True:
        img = pygame.transform.rotate(img, -90)
    return img


def loadAnimationImages(path, aniNum, size):
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


#

MAINMENUIMAGE = loadImage('ui/assets/images/background/Battleship.jpg', (SCREENWIDTH // 3 * 2, SCREENHEIGHT))
ENDSCREENIMAGE = loadImage('ui/assets/images/background/Carrier.jpg', (SCREENWIDTH, SCREENHEIGHT))
BACKGROUND = loadImage('ui/assets/images/background/gamebg.png', (SCREENWIDTH, SCREENHEIGHT))
PGAMEGRIDIMG = loadImage('ui/assets/images/grids/player_grid.png', ((ROWS + 1) * CELLSIZE, (COLS + 1) * CELLSIZE))
CGAMEGRIDIMG = loadImage('ui/assets/images/grids/comp_grid.png', ((ROWS + 1) * CELLSIZE, (COLS + 1) * CELLSIZE))
BUTTONIMAGE = loadImage('ui/assets/images/buttons/button.png', (150, 50))
BUTTONIMAGE1 = loadImage('ui/assets/images/buttons/button.png', (250, 100))
REDTOKEN = loadImage('ui/assets/images/tokens/redtoken.png', (CELLSIZE, CELLSIZE))
GREENTOKEN = loadImage('ui/assets/images/tokens/greentoken.png', (CELLSIZE, CELLSIZE))
BLUETOKEN = loadImage('ui/assets/images/tokens/bluetoken.png', (CELLSIZE, CELLSIZE))
FIRETOKENIMAGELIST = loadAnimationImages('ui/assets/images/tokens/fireloop/fire1_ ', 13, (CELLSIZE, CELLSIZE))
FIRETOKENIMAGELIST = loadAnimationImages('ui/assets/images/tokens/fireloop/fire1_ ', 13, (CELLSIZE, CELLSIZE))
EXPLOSIONSPRITESHEET = pygame.image.load('ui/assets/images/tokens/explosion/explosion.png').convert_alpha()
EXPLOSIONIMAGELIST = [loadSpriteSheetImages(EXPLOSIONSPRITESHEET, col, row, (CELLSIZE, CELLSIZE), (128, 128)) for row in
                      range(8) for col in range(8)]
RADARGRID = loadImage('ui/assets/images/grids/grid_faint.png', ((ROWS) * CELLSIZE, (COLS) * CELLSIZE))
