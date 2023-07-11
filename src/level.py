import pygame
from src.entity import Entity
from src.agent import Agent
from .settings import *
import pandas as pd


class Level:
    def __init__(self,map: pd.DataFrame):
        self.display_surface = pygame.display.get_surface()
        
        self.visible_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()
        
        self.map = map
        self.entities = [map.shape[0], map.shape[1]] 
        
        self.create_map()
        
    def create_map(self):
        for row_i, row in enumerate(self.map):
            for col_i, col in enumerate(row):
                print(row_i, col_i, col)
                x = col_i * TILESIZE
                y = row_i * TILESIZE
                if col == "w":
                    Entity.Entity(position = (x, y), name = "Wall", description = "A wall", inventory = [], inventory_limit = 0, image_src = "assets/sprites/wall.png", groups = [self.visible_sprites, self.obstacle_sprites])   
                
                
                                
    def run(self):
        
        
        self.visible_sprites.draw(self.display_surface)