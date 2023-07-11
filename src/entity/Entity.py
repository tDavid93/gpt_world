from .interactions import craft
import math
import pygame

class Entity(pygame.sprite.Sprite):
    def __init__(self, position, name, description, inventory, inventory_limit, image_src, groups, health = 100, speed = 0.0):
        super().__init__(groups)
        self.position = position
        self.name = name
        self.description = description
        self.health = health
        self.speed = 0.0
        self.tasklist = {}
        self.inventory = inventory
        self.inventory_limit = inventory_limit
        
        self.image = pygame.image.load(image_src)
        
        self.rect = self.image.get_rect(topleft=position)
        self.groups = groups
        
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
    
    
    
    
    def run(self):
        if self.tasklist != {}:
            if self.tasklist[0].time > 0:
                self.tasklist[0].time -= 1
            else:
                for i in self.tasklist[0].recipe.result:
                    list(self.tasklist[0].keys())[0].inventory.append(i)
                self.tasklist.pop(0)      