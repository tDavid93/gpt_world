from langchain.llms import OpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import StructuredTool
from ..entity import Entity
import pygame

import math


class Agent(Entity.Entity):
    def __init__(self, position, name, description, inventory, inventory_limit, image_src, groups, health, speed ):
        self.super().__init__(self, position, name, description, inventory, inventory_limit, image_src, groups, health, speed)
        self.needs = {
            "hunger": 1.0,
            "thirst": 1.0,
            "sleep": 1.0,
            "toilet": 1.0,
            "social": 1.0
        }
        self.llm = OpenAI(temperature=0.9)
        self.tool = StructuredTool().from_function()
        self.place_memory = {}
    
    
    def interact(self, entity, items, tool):
        pass
            
    def save_place(self):
        #TODO need for level.get_tile(self.position)
        if self.place_memory.contains():
            pass
        
    def move_to_coordinates():
        pass
    
    def run(self):
        return 0