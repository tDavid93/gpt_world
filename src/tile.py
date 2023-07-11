import pygame


class Tile(pygame.sprite.Sprite):
    def __init__(self, position, groups, image_src):
        super().__init__(groups)
        self.position = position
        self.image = pygame.image.load(image_src)
        
        self.rect = self.image.get_rect(topleft=position)
        self.groups = groups