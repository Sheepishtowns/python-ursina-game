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
        self.activeperimeter = 4
        self.chunkUnit = self.chunkSize*2
        self.playerpos = (0,0)
    """
    def get_player_chunk(self):#gets the coords of the chunk the player is in
        for chunk in self.loaded_chunks:
            corner_a = chunk[0]
            corner_b = chunk[1]
            corner_c = chunk[0] + 2*self.chunkSize
            corner_d = chunk[1] + 2*self.chunkSize
            if self.playerpos[0] >= corner_a and self.playerpos[0] <= corner_c and self.playerpos[1] >= corner_b and self.playerpos[1] <= corner_d:
                return chunk

        return None
    """
    def get_player_chunk_new(self):
        x_diff = sign(self.playerpos[0]) * abs(ceil(self.playerspawn[0]) - ceil(self.playerpos[0]))
        z_diff = sign(self.playerpos[1]) * abs(ceil(self.playerspawn[1]) - ceil(self.playerpos[1]))
        x_chunk_diff = x_diff // self.chunkUnit
        z_chunk_diff = z_diff // self.chunkUnit

        return [self.playerspawn[0] + x_chunk_diff*self.chunkUnit, self.playerspawn[1] + z_chunk_diff*self.chunkUnit]

    """
    def get_chunk_pos(self, coord):
        x_diff = sign(coord[0]) * abs(ceil(self.playerspawn[0]) - ceil(coord[0]))
        z_diff = sign(coord[1]) * abs(ceil(self.playerspawn[1]) - ceil(coord[1]))
        x_chunk_diff = x_diff // self.chunkUnit
        z_chunk_diff = z_diff // self.chunkUnit

        return (self.playerspawn[0] + x_chunk_diff*self.chunkUnit, self.playerspawn[1] + z_chunk_diff*self.chunkUnit)
    """
    def trigger(self, playerpos):#playerpos is only x and z here
        unit = self.chunkUnit
        blocks2load = []
        
        if any([not self.playerpos[0] == playerpos[0], not self.playerpos[1] == playerpos[1]]) and not self.initial:
            #calculate where the player is going to generate chunks infront
            x_diff = playerpos[0] - self.playerpos[0]
            z_diff = playerpos[1] - self.playerpos[1]

            self.playerpos = playerpos
        
            #gets the corner of chunks, so the for loop can select a 2 by 2 chunk of land
            corner = self.get_player_chunk_new()
            if x_diff > 0:
                corner = [corner[0]+3*unit, corner[1]+unit]
            if x_diff < 0:
                corner = [corner[0], corner[1]+unit]
            for i in range(0,2):
                corner[0] = corner[0] - unit 
                corner[1] = corner[1] - unit

            blocks2load = []

            for x in range(0,1):
                for z in range(0,2):
                    chunk2check = [corner[0] + x*unit, corner[1] + z*unit]
                    if chunk2check not in self.loaded_chunks:
                        blocks2load.append(self.generate_single(chunk2check, True))
                        self.loaded_chunks.append(chunk2check)
            
        if self.initial:#initial load
            self.initial = False
            radius = -1

            self.playerspawn = playerpos

            for x in range(0,radius-1,-1):#generate a 4 by 4 chunk of land
                for z in range(0,radius-1,-1):
                    generated = self.generate_single((playerpos[0] + x*unit,playerpos[1] + z*unit))
                    blocks2load += generated
                    self.world_all[str([playerpos[0] + x*unit,playerpos[1] + z*unit])] = generated
                    self.loaded_chunks.append([playerpos[0] + x*unit,playerpos[1] + z*unit])

        if blocks2load:
            self.loaded_blocks += blocks2load
            return blocks2load
        else:
            return None
        
    def background_generation_thread(self):  
        while True:
            start_point = self.get_player_chunk()
            
            for f in range(0,self.chunks2preload_radius):
                start_point = [start_point[0]-2*16, start_point[1]+2*16]
        #counter = 0

            #for x in range(0, 2*self.chunks2preload_radius+1):
             #   for z in range(0, 2*self.chunks2preload_radius+1):
              #      coordofchunk = [start_point[0]+x*2*self.chunkSize, start_point[1]-z*2*self.chunkSize]
               #     if coordofchunk not in self.not_loaded_chunks and coordofchunk not in self.loaded_chunks:
                #        chunk = self.generate_single(coordofchunk)
                 #       self.world_all[str(coordofchunk)] = chunk
                  #      self.optimized_not_loaded[str(coordofchunk)] = []
                        #for block in chunk:
                        # print("effw") 
                        #    if ifblockcanbeseen(block, chunk):
                        #        self.optimized_not_loaded[str(coordofchunk)].append(block)
                        #self.not_loaded_chunks.append(coordofchunk)
                        #counter += 1
        
        #print(counter)

    def slice(self, chunk):
        x_axis_slices = {}
        
        for block in chunk:
            if block[0] in x_axis_slices:
                x_axis_slices[block[0]].append(block)
            else:
                x_axis_slices[block[0]] = [block]

        z_axis_slices = {}
        for block in chunk:
            if block[2] in z_axis_slices:
                z_axis_slices[block[2]].append(block)
            else:
                z_axis_slices[block[2]] = [block]

        return [x_axis_slices, z_axis_slices]

    def generate_single(self, startpos = (0,0), getop_layer=False):
        if list(startpos) in self.loaded_chunks:
            return []

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