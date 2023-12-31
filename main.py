import csv
import sys

import pygame

from src import level
from src.settings import *


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        file = open("level/map.csv")
        self.map = list(csv.reader(file))
        self.clock = pygame.time.Clock()
        self.level = level.Level(self.map)
    
    def run(self):
        while True:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.level.run()
            pygame.display.update()
            
if __name__ == "__main__":
    game = Game()
    game.run()
