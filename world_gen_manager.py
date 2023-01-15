from perlin_noise import PerlinNoise
from numpy import floor, ceil, sign
from random import randint
from utilities import *
from ursina.entity import Entity
from ursina import Text
from ursina import destroy
import os

#this is where all the spaghetti code and conpressed one-lined sh*t are located, don't try to understand unless necessary🤣

class WorldGenerator:
    def __init__(self, seed, blockdata):
        self.initial = True
        self.blockdata = blockdata
        self.noise = PerlinNoise(octaves=2, seed=seed)
        self.chunkSize = 16
        self.freq = 24
        self.amp = 5
        self.world_all = {} #stores all the blocks with chunk coordinates, both loaded and unloaded
        self.all_block_entities = {} #stores entity objects with chunk coordinates
        self.loaded_chunks = [] #only stores coordinates
        self.all_nolabel = [] #stores all the blocks, but not the chunk coordinates
        self.chunkUnit = self.chunkSize*2
        self.playerpos = (0,0)
        #
        self.blocks2load_queued = []#having queues to prevent the sudden lag when creating and destroying a lot of entities
        self.blocks2unload_queued = []

    def equal_split_list(self, lst, n):
        lists = []
        for i in range(0, len(lst), n):
            lists.append(lst[i:i + n])
        return lists

    def get_player_chunk_new(self):
        x_diff = sign(self.playerpos[0]) * abs(ceil(self.playerspawn[0]) - ceil(self.playerpos[0]))
        z_diff = sign(self.playerpos[1]) * abs(ceil(self.playerspawn[1]) - ceil(self.playerpos[1]))
        x_chunk_diff = x_diff // self.chunkUnit
        z_chunk_diff = z_diff // self.chunkUnit

        return [self.playerspawn[0] + x_chunk_diff*self.chunkUnit, self.playerspawn[1] + z_chunk_diff*self.chunkUnit]

    def locate_chunk_by_coordinate(self, coords):
        x_diff = sign(coords[0]) * abs(ceil(self.playerspawn[0]) - ceil(coords[0]))
        z_diff = sign(coords[1]) * abs(ceil(self.playerspawn[1]) - ceil(coords[1]))
        x_chunk_diff = x_diff // self.chunkUnit
        z_chunk_diff = z_diff // self.chunkUnit

        return [self.playerspawn[0] + x_chunk_diff*self.chunkUnit, self.playerspawn[1] + z_chunk_diff*self.chunkUnit]

    def trigger(self, playerpos):#playerpos is only x and z here
        unit = self.chunkUnit
        blockdata = self.blockdata
        blocks2load = []
        blocks2unload = []

        #process the queued everytime
        if self.blocks2load_queued:
            chunk = self.blocks2load_queued[0]

            items = chunk[1]
            if not len(chunk[1]) < 1:
                if not items:
                    self.blocks2load_queued.pop(0)
                blocks = items[0]
            
                if not blocks:
                    self.blocks2load_queued[0][1].pop(0)
                
                for block in blocks:
                    block_ = Entity(model = os.path.join("model/", blockdata["fullblocks"][str(block[3])]["model"]), texture = os.path.join("texture/", blockdata["fullblocks"][str(block[3])]["texture"]), rotation = (-90,0,0), collider="box")
                    block_.x = block[0]
                    block_.z = block[2]
                    block_.y = block[1]
                    if not str(list(map(int, chunk[0]))) in self.all_block_entities:
                        self.all_block_entities[str(list(map(int, chunk[0])))] = [block_]
                    else:
                        self.all_block_entities[str(list(map(int, chunk[0])))].append(block_)
                self.blocks2load_queued[0][1].pop(0)
            else:
                self.blocks2load_queued.pop(0)
        
        if self.blocks2unload_queued:
            for blockentity in self.blocks2unload_queued[0]:
                #print(blockentity)
                destroy(blockentity)
            self.blocks2unload_queued.pop(0)
        
        if any([not self.playerpos[0] == playerpos[0], not self.playerpos[1] == playerpos[1]]) and not self.initial:
            #calculate where the player is going to generate chunks infront
            x_diff = playerpos[0] - self.playerpos[0]
            z_diff = playerpos[1] - self.playerpos[1]

            prev_chunk = self.get_player_chunk_new()

            self.playerpos = playerpos

            current_chunk = self.get_player_chunk_new()

            #gets the origin of chunk generation
            #┏───────┐
            #┃       ┃
            #┃       ┃
            #┢───────╀───────┐
            #┃   x   ┃       ┃
            #┃       ┃       ┃
            #┗───────┘───────┘

            #load chunks
            origin = self.get_player_chunk_new()
            origin = [origin[0]+sign(x_diff)*unit, origin[1]+sign(z_diff)*unit]

            if sign(x_diff) == 0 or sign(z_diff) == 0:
                chunks2load = [[origin[0], origin[1]],[origin[0] + sign(z_diff)*unit, origin[1] + sign(x_diff)*unit],[origin[0] - sign(z_diff)*unit, origin[1] - sign(x_diff)*unit]]
            else:
                chunks2load = [[origin[0],origin[1]],[origin[0], origin[1] + -1*sign(z_diff)*unit], [origin[0] + -1*sign(x_diff)*unit, origin[1]]]

            for item in chunks2load:
                if item not in self.loaded_chunks:
                    generated = self.generate_single(item, True)
                    self.all_nolabel += generated[1]
                    partials = self.equal_split_list(generated[0], 8) 
                    self.blocks2load_queued.append([item, partials[1:]])
                    for block in partials[0]:
                        block_ = Entity(model = os.path.join("model/", blockdata["fullblocks"][str(block[3])]["model"]), texture = os.path.join("texture/", blockdata["fullblocks"][str(block[3])]["texture"]), rotation = (-90,0,0), collider="box")
                        block_.x = block[0]
                        block_.z = block[2]
                        block_.y = block[1]
                        if not str(list(map(int, item))) in self.all_block_entities:
                            self.all_block_entities[str(list(map(int, item)))] = [block_]#using map to convert float numbers in the array to int
                        else:
                            self.all_block_entities[str(list(map(int, item)))].append(block_)
                        
                    blocks2load += generated[0]
                    self.loaded_chunks.append(item)
                    #label = Text(str(item), parent=scene, scale=(25,25,25), position=(item[0], 6, item[1]))
                    self.world_all[str(list(map(int, item)))] = generated[1]


            #checks for unload
            if not prev_chunk == current_chunk:
                for item in self.loaded_chunks[:]:
                    #print("currently checking:"+str(item))
                    x_dist = abs(item[0]-current_chunk[0])
                    z_dist = abs(item[1]-current_chunk[1])
                    #print(x_dist, z_dist)
                    if x_dist > 32 or z_dist > 32:
                        blocks2unload += self.world_all[str(list(map(int,item)))]
                        partials = self.equal_split_list(self.all_block_entities[str(list(map(int,item)))], 8)
                        self.blocks2unload_queued.extend(partials)
                        self.all_block_entities[str(list(map(int,item)))] = []
                        self.loaded_chunks.remove(item)
            
        if self.initial:#initial load
            self.initial = False
            radius = -1

            self.playerspawn = playerpos

            for x in range(0,radius-1,-1):#generate a 4 by 4 chunk of land
                for z in range(0,radius-1,-1):
                    generated = self.generate_single((playerpos[0] + x*unit,playerpos[1] + z*unit), True)
                    #label = Text(str((playerpos[0] + x*unit,playerpos[1] + z*unit)), parent=scene, scale=(25,25,25), position=(playerpos[0] + x*unit,6,playerpos[1] + z*unit))
                    self.all_nolabel += generated[1]
                    for block_ in generated[0]:
                        blocks2load.append(block_)
                        block = Entity(model = os.path.join("model/", blockdata["fullblocks"][str(block_[3])]["model"]), texture = os.path.join("texture/", blockdata["fullblocks"][str(block_[3])]["texture"]), rotation = (-90,0,0), collider="box")
                        block.x = block_[0]
                        block.z = block_[2]
                        block.y = block_[1]
                        
                        if not str([playerpos[0] + x*unit,playerpos[1] + z*unit]) in self.all_block_entities:
                            self.all_block_entities[str([playerpos[0] + x*unit,playerpos[1] + z*unit])] = [block]
                        else:
                            self.all_block_entities[str([playerpos[0] + x*unit,playerpos[1] + z*unit])].append(block)
                
                    self.world_all[str([playerpos[0] + x*unit,playerpos[1] + z*unit])] = generated[1]
                    self.loaded_chunks.append([playerpos[0] + x*unit,playerpos[1] + z*unit])

        return blocks2load,blocks2unload
        
    def block_update(self, block, entity, action):
        #"block" needs to include coordinate and texture [x,y,z,texture]
        if action == "create":
            chunk_location = self.locate_chunk_by_coordinate([block[0], block[2]])
            self.world_all[str(list(map(int, chunk_location)))].append(block)
            self.all_nolabel.append(block)
            self.all_block_entities[str(list(map(int, chunk_location)))].append(entity)
        elif action == "destroy":
            chunk_location = self.locate_chunk_by_coordinate([entity.position[0], entity.position[2]])
            for item in self.world_all[str(list(map(int, chunk_location)))]:
                if list(entity.position) == item[:3]:
                    texture = item[3]
                    self.world_all[str(list(map(int, chunk_location)))].remove(item)
            self.all_nolabel.remove(list(entity.position)+[texture])
            self.all_block_entities[str(list(map(int, chunk_location)))].remove(entity)
            return list(entity.position)+[texture]
        elif action == "newentity":
            chunk_location = self.locate_chunk_by_coordinate([entity.position[0], entity.position[2]])
            self.all_block_entities[str(list(map(int, chunk_location)))].append(entity)

    def generate_single(self, startpos = (0,0), getop_layer=False):
        topblocks = []
        #the top grass layer
        for i in range(self.chunkSize**2):
            x = floor(i/self.chunkSize)*2+startpos[0]
            z = floor(i%self.chunkSize)*2+startpos[1]
            y = floor(self.noise([x/self.freq, z/self.freq]) * self.amp)
            topblocks.append([x, y, z, 0])
        #the dirt layer under the grass
        dirtblocks = []
        for topblock in topblocks:
            thickness = randint(3,5)
            x = topblock[0]
            z = topblock[2]
            for i in range(1, thickness+1):
                dirtblocks.append([x, topblock[1] - i*2, z, 1])
        #the stone layer
        stoneblocks = []
        bottomdirtblocks = []
        for dirtblock in dirtblocks:
            if [dirtblock[0], dirtblock[1] - 2, dirtblock[2], 1] not in dirtblocks:
                bottomdirtblocks.append(dirtblock)
        for bottomdirtblock in bottomdirtblocks:
            thickness = randint(4,7)
            x = bottomdirtblock[0]
            z = bottomdirtblock[2]
            
            for i in range(1, thickness+1):
                stoneblocks.append([x, bottomdirtblock[1] - i*2, z, 2])

        if getop_layer:
            return [topblocks, topblocks+dirtblocks+stoneblocks]
        return topblocks+dirtblocks+stoneblocks

# ▣ 