import pygame
from src.entity import Entity
from src.agent import Agent
from .settings import *
import pandas as pd
import os
import json


class Level:
    def __init__(self,map: pd.DataFrame):
        self.display_surface = pygame.display.get_surface()
        
        self.visible_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()
        
        self.map = map
        self.entities = {} 
        
        self.agents_config = []
        self.agents = [
            
        ]
        
        self.entity_configs = self.entity_config_loader("assets/enitities")
        
        self.create_map()
            
    def create_map(self):
        for row_i, row in enumerate(self.map):
            for col_i, col in enumerate(row):
                #print(row_i, col_i, col)
                x = col_i * TILESIZE
                y = row_i * TILESIZE
                if self.entity_configs.keys().__contains__(col[0]):
                    #print(f"config : {self.entity_configs}")
                    l_config = self.entity_configs[col[0]]
                    l_config["position"] = (x,y)
                    self.entities[x,y] = Entity.Entity(l_config , groups = [self.visible_sprites, self.obstacle_sprites])
                
            
    def entity_config_loader(self, folder):
        #load all the agents in the folder
        configs = {}
        for _,__, files in os.walk(folder):
            for file in files:
                if file.endswith(".json"):
                    with open(folder + "/" + file) as f:
                        data = json.load(f)
                        print(f"data: {data}")
                        configs[data["sign"]] = data
        #print(configs)
        return configs
                                
    def run(self):
        
        
        self.visible_sprites.draw(self.display_surface)