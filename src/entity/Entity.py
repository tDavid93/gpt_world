from .interactions import craft
import math
import pygame

class Entity(pygame.sprite.Sprite):
    def __init__(self, entity_config, groups, level, agents):
        super().__init__(groups)
        self.position = entity_config["position"]
        self.level = level
        self.name = entity_config["name"] 
        self.description = entity_config["description"]
        self.health = entity_config["health"]
        self.speed = entity_config["speed"]
        self.tasklist = {}
        self.inventory = entity_config["inventory"]
        self.inventory_limit = entity_config["inventory_limit"]
        
        self.image = pygame.image.load(entity_config["image_src"])
        
        self.rect = self.image.get_rect(topleft=self.position)
        self.groups = groups
        self.agents = agents
        self.entity_config = entity_config
        
        
        
    def get_distance(self, entity):
        return math.hypot(self.positi.x-entity.position.x, self.position.y-entity.position.y)
    
    
    def interact(self,type, entity, ingredients, tool, recipe):
        if self.get_distance(self,entity) < 5:
            if type == "craft":
                succ, task = craft(recipe, ingredients, tool, self)
                if succ:
                    self.tasklist.append(entity, task)
                    return "You have started crafting " + recipe.name + "."
            else:
                return f"You cant {type} with {self.name}."    
            
            
        else:
            return f"You cant use {self.name} from here. You need to move closer to interact with it."
        
        
        pass
    
    
    def get_description(self):
        return f"Name:{self.name};\n Description: {self.description}"
    
    
    
    
    def run_tasklist(self):
        if self.tasklist != {}:
            if self.tasklist[0].time > 0:
                self.tasklist[0].time -= 1
            else:
                for i in self.tasklist[0].recipe.result:
                    list(self.tasklist[0].keys())[0].inventory.append(i)
                self.tasklist.pop(0)     
                
    def update(self):
        self.run_tasklist()
        self.rect = self.image.get_rect(topleft=self.position) 