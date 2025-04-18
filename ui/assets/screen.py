import pygame

SCREENWIDTH = 1260
SCREENHEIGHT = 960

GAMESCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))

CELLSIZE = 50
ROWS = 10
COLS = 10


class Window:
    __instance: 'Window' = None
    __initialized = False

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        if not self.__initialized:
            self.__screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
            self.__initialized = True

    @staticmethod
    def screen():
        return Window().__screen
