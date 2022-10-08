from funcs import *
from PIL import Image, ImageEnhance
import os

pygame.init()

os.chdir(os.path.dirname(__file__))

screen = pygame.display.set_mode((680,400))
pygame.display.set_caption('game')
counter = Counter()
block_breaking_spritesheet = SpriteSheet("breaking_animation.png")

breaking_animation1 = block_breaking_spritesheet.image_at((80, 68, 30, 55))


special_block = (0,0)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = breaking_animation1#pygame.transform.scale(breaking_animation1,(37,79)) #pygame.image.load("player.png")
        self.rect = self.image.get_rect()
        self.rect.x = 40
        self.rect.y = 240
        self.movex = 0
        self.movey = 0
        self.speed = 0.005#smaller faster
        self.is_jumping = False
        self.init_jump_energy = 10
        self.jump_energy = 0
        self.top_left = (self.rect.x, self.rect.y)
        self.top_right = (self.rect.x + self.rect.width, self.rect.y)
        self.bottom_left = (self.rect.x, self.rect.y + self.rect.height)
        self.bottom_right = (self.rect.x + self.rect.width, self.rect.y + self.rect.height)
    def collision_detection(self, direction):
        global special_block
        self.top_left = (self.rect.x, self.rect.y)
        self.top_right = (self.rect.x + self.rect.width, self.rect.y)
        ht = (self.rect.x + self.rect.width, self.rect.y)
        self.bottom_left = (self.rect.x, self.rect.y + self.rect.height)
        self.bottom_right = (self.rect.x + self.rect.width, self.rect.y + self.rect.height)
        if direction == "d":
            onBlocksX = withinBlocks(self.bottom_left, self.bottom_right, "x")
            onBlockY = mouseBlockLocate([self.bottom_left[0] ,self.bottom_left[1]+1])[1]
    
            for onBlockX in onBlocksX:
                #onBlockY = onBlockY-1
                if existInMap(gameMap, [onBlockX, onBlockY]):
                    return True
            
            special_block = (self.bottom_right[0],self.bottom_right[1] + 40)
            
            return False
        if direction == "l":
            headBlock = mouseBlockLocate(self.top_left)
            bottom_block = mouseBlockLocate(self.bottom_left)
            #x = headBlock[0]
            #if existInMap(gameMap, (headBlock[0]-40, headBlock[1])):
            #    print("distance between left block:"+str(self.top_left[0]-headBlock[0]))
            if existInMap(gameMap, headBlock):
                return True
            if existInMap(gameMap, (bottom_block[0], bottom_block[1])):
                return True
            
            return False
        if direction == "r":
            headBlock = mouseBlockLocate(self.top_right)
            bottom_block = mouseBlockLocate(self.bottom_right)
            #x = headBlock[0]
            if existInMap(gameMap, headBlock):
                return True            
            if existInMap(gameMap, (bottom_block[0], bottom_block[1])):
                return True
            
            return False
             
                    
    def update(self):
        #fall detection
        if not self.collision_detection("d") and self.jump_energy < 1:
            if counter.check_task("playerFall") == True or counter.check_task("playerFall") == False:
                self.movey = 1
                counter.new_task("playerFall",self.speed*0.8)
            self.movex = 0
            
        if self.collision_detection("l"):
            if self.movex < 0:
                self.movex = 0
        if self.collision_detection("r"):
            if self.movex > 0:
                self.movex = 0
                

        if self.jump_energy > 0:
            if counter.check_task("playerJump") == True or counter.check_task("playerJump") == False:
                self.movey -= self.jump_energy
                self.jump_energy -= 1
                counter.new_task("playerJump",self.speed*7)

        self.rect.x += self.movex 
        self.rect.y += self.movey 
        """
        if existInMap(gameMap,mouseBlockLocate(self.bottom_left)) or existInMap(gameMap,mouseBlockLocate(self.bottom_right)):#anti no-clip
            if self.movex > 0:
                self.rect.x -= self.movex 
            else:
                self.rect.y -= self.movey """
        self.movex = 0
        self.movey = 0
        
    def move(self, direction):
        if counter.check_task("playerMove") == True or counter.check_task("playerMove") == False:
            if direction == "l":
                self.movex = -1
            elif direction == "r":
                self.movex = 1
            counter.new_task("playerMove",self.speed)

    def jump(self):
        if self.collision_detection("d"):
            self.jump_energy = self.init_jump_energy
                
        
class Tile(pygame.sprite.Sprite):
    def __init__(self, id, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.id_block = {"111":"dirt.png","112":"plain_dirt.png"}
        self.id = id
        self.image = pygame.transform.scale(pygame.image.load(self.id_block[id]),(40,40))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.highlight = False #for performance
    def destroy(self,x,y):
        for i in all_blocks_list:
            if x == i.rect.x and y == i.rect.y:
                all_blocks_list.remove(i)
                
    def update(self):
        global special_block
        #print(pygame.mouse.get_pos())
        #block highlight
        x,y = pygame.mouse.get_pos()
        if self.highlight:
            self.image = pygame.transform.scale(pygame.image.load(self.id_block[self.id]),(40,40))
            self.highlight = False
        if x > self.rect.x and x < self.rect.x+40:
            if y > self.rect.y and y < self.rect.y+40:
                self.highlight = True
                im = Image.open(self.id_block[self.id])
                enhancer = ImageEnhance.Brightness(im)
                im = enhancer.enhance(1.5)
                im = pygame.image.fromstring(im.tobytes(), im.size, im.mode)
                self.image = pygame.transform.scale(im,(40,40))
           
        
def generate_terrain():
    terrain = []
    #start from bottom left
    for i in range(0,17):
        terrain.append(["112",i,0])
    for i in range(0,17):
        terrain.append(["111",i,1])
    return terrain

    
all_blocks_list = pygame.sprite.Group()
all_entities_list = pygame.sprite.Group()

gameMap = [] #store all block and entity data

terrain = generate_terrain()
for i in terrain:   
    block = Tile(i[0], i[1]*40, 360 - 40*i[2])
    all_blocks_list.add(block)
    gameMap.append([i[0], i[1]*40, 360 - 40*i[2]])


player = Player()
all_entities_list.add(player)

while True:
    key_list = pygame.key.get_pressed()
    if key_list[pygame.K_LEFT]:
        player.move("l")
    elif key_list[pygame.K_RIGHT]:
        player.move("r")
    elif key_list[pygame.K_UP]:
        player.jump()

    pygame.display.flip()
    screen.fill((0,0,0))
    all_blocks_list.update()
    all_blocks_list.draw(screen)
    all_entities_list.update()
    all_entities_list.draw(screen)

    for event in pygame.event.get():
        #block break
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                coords = mouseBlockLocate(pygame.mouse.get_pos())
                
                block.destroy(coords[0], coords[1])
                if existInMap(gameMap, [coords[0], coords[1]]):
                    gameMap.remove(existInMap(gameMap, [coords[0], coords[1]]))
            elif event.button == 3:
                coords = mouseBlockLocate(pygame.mouse.get_pos())
                if coords:
                    repeated = False
                    if existInMap(gameMap, [coords[0], coords[1]]):
                        repeated = True
                        #break
                    if not repeated:
                        block = Tile("112", coords[0], coords[1])
                        all_blocks_list.add(block)
                        gameMap.append([i[0], coords[0], coords[1]])
        if event.type == pygame.QUIT:
            pygame.quit()
            break        