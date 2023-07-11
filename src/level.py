import json
import os

import pandas as pd
import pygame

from src.agent import Agent
from src.entity import Entity

from .settings import *
from . import klogger as kl
import numpy as np



class Level:
    def __init__(self, map: pd.DataFrame):
        self.display_surface = pygame.display.get_surface()
        
        self.visible_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()

        self.map = map
        self.entities = {}

        self.agents_config = self.entity_config_loader("assets/agents")
        self.agents = []
        
        

        self.entity_configs = self.entity_config_loader("assets/enitities")
        
        self.pathfinder_map = self.generate_pathfinder_map()
        
        self.create_map()
        

    def create_map(self):
        for row_i, row in enumerate(self.map):
            for col_i, col in enumerate(row):
                # print(row_i, col_i, col)
                x = col_i * TILESIZE
                y = row_i * TILESIZE
                if self.entity_configs.keys().__contains__(col[0]):
                    # print(f"config : {self.entity_configs}")
                    l_config = self.entity_configs[col[0]]
                    l_config["r_position"] = (row_i, col_i)
                    l_config["position"] = (x, y)

                    self.entities[x, y] = Entity.Entity(l_config,
                                                        agents=self.agents,
                                                        groups=[
                                                                self.visible_sprites,
                                                                self.obstacle_sprites
                                                                ], 
                                                        level=self.entities)

        for agent in self.agents_config:
            l_config = self.agents_config[agent]
            
            l_config["r_position"] = (
                                    l_config["pos_x"],
                                    l_config["pos_y"]
                                    )
             
            l_config["position"] = (
                                    l_config["pos_x"] * TILESIZE,
                                    l_config["pos_y"] * TILESIZE
                                    )
            
            
            self.agents.append(Agent.Agent(
                                        l_config,
                                        level=self.entities,
                                        map=self.pathfinder_map,
                                        agents=self.agents,
                                        groups=[self.visible_sprites]
                ))
            
    def generate_pathfinder_map(self):
        kl.klog("level", "generate_pathfinder_map", f"map: {self.map}", level="DEBUG")
        size_x = len(self.map)
        size_y = len(self.map[0])
        maze = np.empty((size_x, size_y), dtype=int)
        for row_i, row in enumerate(self.map):
            for col_i, col in enumerate(row):
                # print(row_i, col_i, col)
                if self.entity_configs.keys().__contains__(col[0]):
                    # print(f"config : {self.entity_configs}")
                    l_config = self.entity_configs[col[0]]
                    
                    kl.klog("level", "generate_pathfinder_map", f"l_config: {l_config}, x: {row_i}, y: {col_i}", level="DEBUG")
                    
                    if l_config["walkable"] == "false":
                        maze[row_i][col_i] = 1
                    else:
                        maze[row_i][col_i] = 0
        return maze

    def entity_config_loader(self, folder):
        # load configs from folder
        configs = {}
        for _, __, files in os.walk(folder):
            for file in files:
                if file.endswith(".json"):
                    with open(folder + "/" + file) as f:
                        data = json.load(f)
                        # print(f"data: {data}")
                        try:
                            configs[data["sign"]] = data

                        except KeyError:
                            configs[data["name"]] = data

        return configs

    def update(self):
        self.visible_sprites.update()
        self.obstacle_sprites.update()

    def run(self):
        self.update()

        self.visible_sprites.draw(self.display_surface)
