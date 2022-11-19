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

    return topblocks+dirtblocks+stoneblocks

def ifblockcanbeseen(coord, blocks):
    
    y_range = (coord[1], coord[1]-2)
    is_top = True
    #check the number of surrounding blocks covering each face
    face_a = []
    face_b = []
    face_c = []
    face_d = []

    for block in blocks:
        if block[1] == coord[1]+2 and block[2] == coord[2] and block[0] == coord[0]:#the block on top of the target block
            is_top = False
    if is_top:
        return True
    for block in blocks:
        if block[0] == coord[0]+2 and block[2] == coord[2]: #check if the block is surrounded
            if block[1] >= y_range[1] and block[1] <= y_range[0] or block[1]-2 > y_range[1] and block[1]-2 < y_range[0]:
                face_a.append(block)
        if block[0] == coord[0]-2 and block[2] == coord[2]:
            if block[1] >= y_range[1] and block[1] <= y_range[0] or block[1]-2 > y_range[1] and block[1]-2 < y_range[0]:
                face_b.append(block)
        if block[0] == coord[0] and block[2] == coord[2]+2:
            if block[1] >= y_range[1] and block[1] <= y_range[0] or block[1]-2 > y_range[1] and block[1]-2 < y_range[0]:
                face_c.append(block)
        if block[0] == coord[0] and block[2] == coord[2]-2:
            if block[1] >= y_range[1] and block[1] <= y_range[0] or block[1]-2 > y_range[1] and block[1]-2 < y_range[0]:
                face_d.append(block)
    
    face_a_y = [axis[1] for axis in face_a]
    face_b_y = [axis[1] for axis in face_b]
    face_c_y = [axis[1] for axis in face_c]
    face_d_y = [axis[1] for axis in face_d]

    try:
        if not max(face_a_y) >= y_range[0] or not min(face_a_y)-2 <= y_range[1]:
            return True
    except ValueError:
        pass
    try:
        if not max(face_b_y) >= y_range[0] or not min(face_b_y)-2 <= y_range[1]:
            return True
    except ValueError:
        pass
    try:
        if not max(face_c_y) >= y_range[0] or not min(face_c_y)-2 <= y_range[1]:
            return True
    except ValueError:
        pass
    try:
        if not max(face_d_y) >= y_range[0] or not min(face_d_y)-2 <= y_range[1]:
            return True
    except ValueError:
        pass
    
    return False
    

"""
def partial_refresh(chunk, visible, center, radius = 3):
    #generate coords of blocks that gets checked
    detection_zone = []
    refresh_zone = []
    corner_anchor = [center[0]-2*radius,center[1]+2*radius,center[2]-2*radius]
    for z in range(1, (radius+1)*2):
        layer_corner_anchor = [corner_anchor[0]+2,corner_anchor[1], corner_anchor[2]]
        for x in range(1, (radius+1)*2):
            for y in range(1,(radius+1)*2):
                refresh_zone.append([x*2,y*2,z*2])

    #do the checking
"""
def get_difference(set1, set2):
    set1_ = set1.copy()
    set2_ = set2.copy()#make copy local copy to prevent edits to global vars 
    sames = []
    for item in set1_:
        for item_ in set2_:
            if item[:3] == item_[:3]:
                sames.append(item)
    for item in sames:
        set1_.remove(item)
        set2_.remove(item)
    removes = []
    for item in set1_:
        if item not in set2_:
            removes.append(item)

    return [removes, set2_]
    
    

    