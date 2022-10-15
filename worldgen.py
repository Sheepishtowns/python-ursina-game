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
        x = floor(i/chunkSize*2)
        z = floor(i%chunkSize*2)
        y = floor(noise([x/freq, z/freq]) * 5)
        topblocks.append([x, y, z])
    #the dirt layer under the grass
    dirtblocks = []
    for topblock in topblocks:
        thickness = randint(6,9)
        x = topblock[0]
        z = topblock[2]
        for i in range(1, thickness+1):
            dirtblocks.append([x, topblock[1] - i*2, z])
    print(topblocks+dirtblocks)

    return topblocks

def getunseenblocks(blocks):
    hidden = []
    for block in blocks:
        neighbors = [[block[0]+2,block[1],block[2]], [block[0]-2,block[1],block[2]], [block[0],block[1],block[2]+2], [block[0],block[1],block[2]-2], [block[0],block[1]+2,block[2]]]
        visible = False
        for neighbor in neighbors:
            if not neighbor in blocks:
                visible = True
        if not visible:
            hidden.append(block)
    return hidden