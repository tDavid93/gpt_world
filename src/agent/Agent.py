
from langchain import LLMMathChain
from langchain.chat_models import ChatOpenAI
from langchain.chat_models import ChatOpenAI

from langchain.chat_models import ChatOpenAI
from langchain.experimental.plan_and_execute import PlanAndExecute, load_agent_executor, load_chat_planner
from langchain import LLMMathChain


from typing import Optional, Type

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

from langchain.tools import BaseTool

from ..entity import Entity

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
            GetKnownPlace(agent_instance=self)
        ]    
        print(f"surrondings: {self.get_surroundings()}")    
        
        self.model = ChatOpenAI(temperature=0)

        self.planner = load_chat_planner(self.model)

        self.executor = load_agent_executor(self.model, self.tools, verbose=True)

        self.langchain_brain = PlanAndExecute(planner=self.planner, executor=self.executor, verbose=True)
        
        #self.langchain_brain = initialize_agent(self.tools, self.llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=True)
    
    def interact(self, entity, items, tool):
        pass
            
    def save_place(self, entity):
        #TODO need for level.get_tile(self.position)
        if self.place_memory.key().__contains__(entity.name):
            self.place_memory[entity.name] = entity.position
            
    
    
    def get_known_place(self):
        """Get all known places in memory from the town. Can be used to retrive all the possible places to go to.

        Returns:
            str: all known places in memory
        """
        #print(f"self.place_memory: {self.place_memory}")
        places = ""
        if self.place_memory:
            for k in self.level.keys():
                places += f"{k} ,"
        return places
    
    
    def move_to_known_place_by_name(self, name:str):
        """Move to known place by name
        
        Returns:
            str: succes or error
        """
        if self.place_memory.keys().__contains__(name):
            self.move_to(self.place_memory[name])
            return "succes"
        return "there is no known place with this name"
    
    
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
        surrondings = {}
        
        distance = 1000
        #print(f"self.leve {self.level}") 
        for enitity in self.level:
            #print(f"enitity: {enitity}")
            if math.hypot(enitity[0] - self.position[0], enitity[1] - self.position[1]) < distance and self.level[enitity].name == "Grass":
                surrondings[self.level[enitity]] = self.level[(enitity)]
        return surrondings
        
    def calculate_health(self):
        self.health -= (self.needs["hunger"] * 0.1) + (self.needs["thirst"] * 0.1) + (self.needs["sleep"] * 0.1) + (self.needs["toilet"] * 0.1) + (self.needs["social"] * 0.1)
        
    def think(self):
        pass
    
    def create_initial_memory(self):
        return f"You playing a text based rpg in a medival age. You are a {self.name} and you are in a town. You have a {self.inventory} in your inventory. Your only goal is to not die. This is your backstory: {self.description}"
    
    
    def start_non_blocking_llm_brain(self):
        self
     
    def update(self):
        print(f"update: {self.name}")
        self.calculate_needs()
        self.calculate_health()
        self.get_surroundings()
                
        
        
        

class GetKnownPlace(BaseTool):
    name = "get_known_place"
    description = "Get every known places from memory"
    agent_memory = ""
    agent: Type[Agent] = None
    
    def __init__(self,agent_instance):
        super().__init__()
        print(f"GetKnownPlace {agent_instance.name}")
        
        self.agent_memory = agent_instance.get_known_place()
        self.agent = agent_instance
    
    
    def _run(self, query:str) -> str:
        """Get all known places in memory from the town. Can be used to retrive all the possible places to go to."""
        
        return self.agent_memory   
        
    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("GetKnownPlace does not support async")
    
