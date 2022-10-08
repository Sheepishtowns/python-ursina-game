import time
import pygame

def mouseBlockLocate(pos):
    x_zone = 0
    while True:
        
        if x_zone > 17*40:
            return None
        if pos[0] >= x_zone and pos[0] <= x_zone+40:
            break
        x_zone += 40
    y_zone = 360
    while True:
    
        if y_zone < 0:
            return None
        if pos[1] >= y_zone and pos[1] <= y_zone+40:
            break
        y_zone -= 40
    return (x_zone, y_zone)

def withinBlocks(pos1, pos2, xy):
    if xy == "x":
        block1 = mouseBlockLocate(pos1)[0]
        block2 = mouseBlockLocate(pos2)[0]
        
        if block1 == None or block2 == None:
            return False

        list_ = []
        while True:
            list_.append(block1)
            if block1 == block2:
                break
            block1 += 40  
        
        return list_


def existInMap(gameMap, pos):
    for i in gameMap:
        if i[1] == pos[0] and i[2] == pos[1]:
            return i
    return False

class Counter():
    def __init__(self): self.tasks = []
    def new_task(self, name, miliseconds_before_execution:int):
        if not self.check_task(name):
            self.tasks.append([name,miliseconds_before_execution,time.time()])
        else:
            for task in self.tasks:
                if task[0] == name:
                    task[1] = miliseconds_before_execution
                    task[2] = time.time()
    
    def check_task(self, name):
        for task in self.tasks:
            if task[0] == name:
                diff = round(time.time() - task[2],3)
                if diff >= task[1]:
                    return True
                else:
                    return 2 #time not up
        return False 

class SpriteSheet:

    def __init__(self, filename):
        """Load the sheet."""
        try:
            self.sheet = pygame.image.load(filename).convert()
        except pygame.error as e:
            print(f"Unable to load spritesheet image: {filename}")
            raise SystemExit(e)


    def image_at(self, rectangle, colorkey = None):
        """Load a specific image from a specific rectangle."""
        # Loads image from x, y, x+offset, y+offset.
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image

    def images_at(self, rects, colorkey = None):
        """Load a whole bunch of images and return them as a list."""
        return [self.image_at(rect, colorkey) for rect in rects]

    def load_strip(self, rect, image_count, colorkey = None):
        """Load a whole strip of images, and return them as a list."""
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)