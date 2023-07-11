from langchain.llms import OpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import StructuredTool

from langchain import LLMMathChain, SerpAPIWrapper
from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from langchain.chat_models import ChatOpenAI

from ..entity import Entity
import pygame

import math


class Agent(Entity.Entity):
    def __init__(self, agent_config, groups, level, agents):
        super().__init__( agent_config, groups, level, agents)
        self.needs = {
            "hunger": 1.0,
            "thirst": 1.0,
            "sleep": 1.0,
            "toilet": 1.0,
            "social": 1.0
        }
        self.llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")
        #self.tool = StructuredTool().from_function()
        self.place_memory = {}
        self.time_from_social = 0
        self.time_from_eat = 0
        self.need_modif = 0.1
        self.ll_math = LLMMathChain(llm = self.llm)
        
        
        self.tools = [
            Tool.from_function(
                func=self.get_known_place,
                name="get_known_place",
                description="Get all known places in memory"
            ),
            Tool.from_function(
                func=self.move_to_known_place_by_name,
                name="move_to_known_place_by_name",
                description="Move to known place by name",
                
            ),
            Tool.from_function(
                func=self.get_health,
                name="get_health",
                description="Get health status"
                )
        ]    
        print(f"surrondings: {self.get_surroundings()}")    
        
        self.langchain_brain = initialize_agent(self.tools, self.llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=True)
    
    def interact(self, entity, items, tool):
        pass
            
    def save_place(self, entity):
        #TODO need for level.get_tile(self.position)
        if self.place_memory.key().__contains__(entity.name):
            self.place_memory[entity.name] = entity.position
            
    
    @tool("get_known_place", return_direct=True)
    def get_known_place(self):
        """Get all known places in memory from the town. Can be used to retrive all the possible places to go to.

        Returns:
            str: all known places in memory
        """
        return self.place_memory.keys()
    
    @tool("move_to_known_place_by_name", return_direct=True) 
    def move_to_known_place_by_name(self, str):
        """Move to known place by name
        
        Returns:
            str: succes or error
        """
        if self.place_memory.keys().__contains__(str):
            self.move_to(self.place_memory[str])
            return "succes"
        return "there is no known place with this name"
    
    @tool("get_health", return_direct=True)
    def get_health(self):
        """ Get health status
        
        Returns:
            str: health status
        """
        if self.health < 25:
            return "I'm dying"
        if self.health < 50:
            return "I'm very sick"
        if self.health < 75:
            return "I'm sick"
        if self.health < 100:
            return "I'm ok"
    
    def calculate_needs(self):
        
        self.needs["hunger"] -= self.need_modif
        self.needs["thirst"] -= self.need_modif
        #TODO add day_night cycle
        self.needs["sleep"] -=  self.need_modif
        self.needs["toilet"] -= self.need_modif * (24 / (self.time_from_eat +1))
        self.needs["social"] -= self.need_modif * (24 / (self.time_from_social +1))
        
    def get_surroundings(self):
        surrondings = []
        
        distance = 50
        #print(f"self.leve {self.level}") 
        for enitity in self.level:
            #print(f"enitity: {enitity}")
            if math.hypot(enitity[0] - self.position[0], enitity[1] - self.position[1]) < distance and self.level[enitity].name == "Grass":
                surrondings.append(self.level[enitity])
        return surrondings
        
    def calculate_health(self):
        self.health -= (self.needs["hunger"] * 0.1) + (self.needs["thirst"] * 0.1) + (self.needs["sleep"] * 0.1) + (self.needs["toilet"] * 0.1) + (self.needs["social"] * 0.1)
        
    def think(self):
        pass
    
    def create_initial_memory(self):
        return f"You playing a text based rpg in a medival age. You are a {self.name} and you are in a town. You have a {self.inventory} in your inventory. Your only goal is to not die."
    
     
    def update(self):
        print(f"update: {self.name}")
        self.calculate_needs()
        self.calculate_health()
        self.get_surroundings()
        self.langchain_brain.run(self.create_initial_memory())        
        
        