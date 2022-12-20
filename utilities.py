def ifblockcanbeseen(coord, blocks, refresh_around = False):
    
    y_range = (coord[1], coord[1]-2)
    is_top = True
    #check the number of surrounding blocks covering each face
    face_a = []
    face_b = []
    face_c = []
    face_d = []
    
    if not refresh_around:
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

        if refresh_around and block[1] == coord[1]-2 and block[2] == coord[2] and block[0] == coord[0]:#get the block on the bottom
            face_d.append(block)

    if refresh_around:
        target_blocks = face_a + face_b + face_c + face_d
        canbeseen = []
        for target in target_blocks:
            if ifblockcanbeseen(target[:3], blocks):
                canbeseen.append(target)
        return canbeseen

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