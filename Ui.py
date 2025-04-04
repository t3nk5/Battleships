import pygame

class Ui:
    def __init__(self, size_x, size_y, offset_x=50, offset_y=50):
        self.size_x = size_x
        self.size_y = size_y
        self.color_blue = (0, 0, 255)
        self.color_black = (0, 0, 0)
        self.color_white = (255, 255, 255)
        self.size_cell = 40
        self.offset_x = offset_x
        self.offset_y = offset_y


        pygame.init()
        self.screen = pygame.display.set_mode((self.size_x * self.size_cell + self.offset_x,
                                               self.size_y * self.size_cell + self.offset_y))
        pygame.display.set_caption("BattleShip")


        self.font = pygame.font.Font(None, 30)

    def draw(self):

        for i in range(self.size_x):
            for j in range(self.size_y):
                x = i * self.size_cell + self.offset_x
                y = j * self.size_cell + self.offset_y

                pygame.draw.rect(self.screen, self.color_blue, (x, y, self.size_cell, self.size_cell))
                pygame.draw.rect(self.screen, self.color_white, (x, y, self.size_cell, self.size_cell), 2)

        for i in range(self.size_x):
            letter = chr(65 + i)
            text_surface = self.font.render(letter, True, self.color_white)
            text_x = i * self.size_cell + self.offset_x + (self.size_cell // 2) - 10
            text_y = self.offset_y - 30
            self.screen.blit(text_surface, (text_x, text_y))


        for j in range(self.size_y):
            number = str(j + 1)
            text_surface = self.font.render(number, True, self.color_white)
            text_x = self.offset_x - 30  #
            text_y = j * self.size_cell + self.offset_y + (self.size_cell // 2) - 10
            self.screen.blit(text_surface, (text_x, text_y))


        pygame.display.flip()