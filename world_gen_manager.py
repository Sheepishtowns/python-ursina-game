from perlin_noise import PerlinNoise
from numpy import floor, ceil, sign
from random import randint
from utilities import *

#emojis 😀😄😃🤣😎

class WorldGenerator:
    def __init__(self, seed):
        self.initial = True
        self.noise = PerlinNoise(octaves=2, seed=seed)
        self.chunkSize = 16
        self.freq = 24
        self.amp = 5
        self.world_all = {} #stores all the chunks, both loaded and unloaded
        self.loaded_chunks = []
        self.not_loaded_chunks = []
        self.loaded_blocks = []
        self.chunkUnit = self.chunkSize*2
        self.playerpos = (0,0)
    
    def get_player_chunk_new(self):
        x_diff = sign(self.playerpos[0]) * abs(ceil(self.playerspawn[0]) - ceil(self.playerpos[0]))
        z_diff = sign(self.playerpos[1]) * abs(ceil(self.playerspawn[1]) - ceil(self.playerpos[1]))
        x_chunk_diff = x_diff // self.chunkUnit
        z_chunk_diff = z_diff // self.chunkUnit

        return [self.playerspawn[0] + x_chunk_diff*self.chunkUnit, self.playerspawn[1] + z_chunk_diff*self.chunkUnit]

    def trigger(self, playerpos):#playerpos is only x and z here
        unit = self.chunkUnit
        blocks2load = []
        
        if any([not self.playerpos[0] == playerpos[0], not self.playerpos[1] == playerpos[1]]) and not self.initial:
            #calculate where the player is going to generate chunks infront
            x_diff = playerpos[0] - self.playerpos[0]
            z_diff = playerpos[1] - self.playerpos[1]

            self.playerpos = playerpos

            #gets the origin of chunk generation
            #┏───────┐
            #┃       ┃
            #┃       ┃
            #┢───────╀───────┐
            #┃   x   ┃       ┃
            #┃       ┃       ┃
            #┗───────┘───────┘
            
            origin = self.get_player_chunk_new()
            origin = [origin[0]+sign(x_diff)*unit, origin[1]+sign(z_diff)*unit]

            blocks2load = []

            if sign(x_diff) == 0 or sign(z_diff) == 0:
                chunks2load = [[origin[0], origin[1]],[origin[0] + sign(z_diff)*unit, origin[1] + sign(x_diff)*unit],[origin[0] - sign(z_diff)*unit, origin[1] - sign(x_diff)*unit]]
            else:
                chunks2load = [[origin[0],origin[1]],[origin[0], origin[1] + -1*sign(z_diff)*unit], [origin[0] + -1*sign(x_diff)*unit, origin[1]]]

            for item in chunks2load:
                if item not in self.loaded_chunks:
                    blocks2load.append(self.generate_single(item, True))
                    self.loaded_chunks.append(item)
            
            
        if self.initial:#initial load
            self.initial = False
            radius = -1

            self.playerspawn = playerpos

            for x in range(0,radius-1,-1):#generate a 4 by 4 chunk of land
                for z in range(0,radius-1,-1):
                    generated = self.generate_single((playerpos[0] + x*unit,playerpos[1] + z*unit), True)
                    blocks2load.append(generated)
                    self.world_all[str([playerpos[0] + x*unit,playerpos[1] + z*unit])] = generated
                    self.loaded_chunks.append([playerpos[0] + x*unit,playerpos[1] + z*unit])

        if blocks2load:
            self.loaded_blocks += blocks2load
            return blocks2load
        else:
            return None

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