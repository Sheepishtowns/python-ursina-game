from perlin_noise import PerlinNoise
from numpy import floor
from random import randint

noise = PerlinNoise(octaves=2, seed=100)

#VARIABLES
chunkSize = 16
freq = 24

def generate_chunk():
    topblocks = []
    #the top grass layer 
    for i in range(chunkSize**2):
        block = floor(i/chunkSize)*2
        z = floor(i%chunkSize)*2
        y = floor(noise([block/freq, z/freq]) * 5)
        topblocks.append([block, y, z, 0])
    #the dirt layer under the grass
    dirtblocks = []
    for topblock in topblocks:
        thickness = randint(6,9)
        block = topblock[0]
        z = topblock[2]
        for i in range(1, thickness+1):
            dirtblocks.append([block, topblock[1] - i*2, z, 1])

    return topblocks+dirtblocks

def ifblockcanbeseen(coord, blocks):
    neighbour_column_blocks = []
    y_range = (coord[1], coord[1]-2)
    is_top = True
    #check the number of surrounding blocks covering each face
    face_a = 0
    face_b = 0
    face_c = 0
    face_d = 0

    for block in blocks:
        if block[1] == coord[1]+2 and block[2] == coord[2] and block[0] == coord[0]:#the block on top of the target block
            is_top = False
    if is_top:
        return True
    for block in blocks:
        if block[0] == coord[0]+2 and block[2] == coord[2]: #check if the block is surrounded
            if block[1] >= y_range[1] and block[1] <= y_range[0] or block[1]-2 > y_range[1] and block[1]-2 < y_range[0]:
                neighbour_column_blocks.append(block)
        if block[0] == coord[0]-2 and block[2] == coord[2]:
            if block[1] >= y_range[1] and block[1] <= y_range[0] or block[1]-2 > y_range[1] and block[1]-2 < y_range[0]:
                neighbour_column_blocks.append(block)
        if block[0] == coord[0] and block[2] == coord[2]+2:
            if block[1] >= y_range[1] and block[1] <= y_range[0] or block[1]-2 > y_range[1] and block[1]-2 < y_range[0]:
                neighbour_column_blocks.append(block)
        if block[0] == coord[0] and block[2] == coord[2]-2:
            if block[1] >= y_range[1] and block[1] <= y_range[0] or block[1]-2 > y_range[1] and block[1]-2 < y_range[0]:
                neighbour_column_blocks.append(block)
    
    for surrounding in neighbour_column_blocks:
        if surrounding[0] == coord[0]-2:
            face_a += 1
        if surrounding[0] == coord[0]+2:
            face_b += 1
        if surrounding[2] == coord[2]+2:
            face_c += 1
        if surrounding[2] == coord[2]-2:
            face_d += 1
    
    if face_a >= 1 and face_b >= 1 and face_c >= 1 and face_d >= 1:
        return False
    else:
        return True

    