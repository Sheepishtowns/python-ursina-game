from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import json
import os
import utilities
from world_gen_manager import *
from world_event_handle import *
import time

#run with python 3.8 or above

def equal_split_list(lst, n):
    lists = []
    for i in range(0, len(lst), n):
        lists.append(lst[i:i + n])
    return lists

app = Ursina(borderless=False)

box = Entity(parent=camera.ui, model=Quad(radius=0), scale=(1.5,0.7))
text1 = Text(text="Loading world...")
text1.size = 0.05
text1.color = color.blue
text1.x = -0.12
text1.y = 0

#step three times to show the load screen
app.step()
app.step()
app.step()

#load all the blocks from a json file
blockdata = json.loads(open("data/blocks.json","r").read())
world = WorldGenerator(100, blockdata)
playerspawn = (0,0)
#chunk = []
visible_chunk = world.trigger(playerspawn)[0]
visible_chunk_entities = []#store all the entity objects for easy access


#get rid of load screen after world has initially loaded
destroy(box)
destroy(text1)

class Player(FirstPersonController):
    def __init__(self):
        super().__init__()
        self.model = "model\player.obj"
        self.texture = "texture\player.png"
        self.scale = (0.5,0.7,0.5)
        self.speed = 4
        self.height = 3
    def getxz(self):
        return (self.position[0], self.position[2])
    def switch(self):
        mouse.locked = not mouse.locked
        self.cursor.enabled = not self.cursor.enabled

ec = EditorCamera(enabled=0)

player = Player()
player.position = Vec3(playerspawn[0], 8, playerspawn[1])

event_master = EventsMaster(blockdata, visible_chunk)
indicator = None

def update():
    blocks2load, blocks2unload = world.trigger(player.getxz())
    
    global indicator
    destroy(indicator)

    global chunk, visible_chunk
    
    if blocks2load:
        for item in blocks2load:
            visible_chunk.append(item)
    if blocks2unload:
        visible_chunk = [block for block in visible_chunk if block not in blocks2unload]
                
    actions = event_master.trigger(mouse)
    if "breaking" in actions:#apply the breaking animation on blocks
        indicator = Entity(name = "break-indicate", model = os.path.join("model/", blockdata["specialblocks"]["break-indicate"]["model"]), texture = os.path.join("texture/", blockdata["specialblocks"]["break-indicate"]["animation"], "/breaking-"+str(actions["breaking"][1])+".png"), rotation = (-90,0,0), position = actions["breaking"][0], scale = blockdata["specialblocks"]["break-indicate"]["scale"])

    if "destroy" in actions:
        block_rep = world.block_update("", actions["destroy"], "destroy")
        for block in utilities.ifblockcanbeseen(actions["destroy"].position, world.all_nolabel, True):
            if not block in visible_chunk:
                block_ = Entity(model = os.path.join("model/", blockdata["fullblocks"][str(block[3])]["model"]), texture = os.path.join("texture/", blockdata["fullblocks"][str(block[3])]["texture"]), rotation = (-90,0,0), collider="box")
                block_.x = block[0]
                block_.z = block[2]
                block_.y = block[1]
                #print(block)
                world.block_update("", block_, "newentity")
                visible_chunk.append(block)
        
        visible_chunk.remove(block_rep)
        event_master.chunkdata = visible_chunk
        destroy(actions["destroy"])
    
    if "place" in actions:
        block = Entity(model = os.path.join("model/", blockdata["fullblocks"][str(actions["place"][1])]["model"]), texture = os.path.join("texture/", blockdata["fullblocks"][str(actions["place"][1])]["texture"]), rotation = (-90,0,0), collider="box")
        block.position = actions["place"][0]
        world.block_update(list(actions["place"][0]) + [actions["place"][1]], block, "create")
        visibles = utilities.ifblockcanbeseen(actions["place"][0], world.all_nolabel, True)
        visible_chunk.append(list(actions["place"][0])+[actions["place"][1]])
        visibles_ = utilities.ifblockcanbeseen(actions["place"][0], world.all_nolabel, True)

        differ = utilities.get_difference(visibles, visibles_)
        
        for blk in differ[0]:
            try:
                visible_chunk.remove(blk)
            except ValueError:
                pass
            for e in scene.entities:
                if list(e.position) == blk[:3]:
                    destroy(e)
        event_master.chunkdata = visible_chunk

def input(key):
    if key == 'tab':    # press tab to toggle edit/play mode
        ec.enabled = not ec.enabled
        player.switch()
        if ec.enabled:
            event_master.disable_event("block_place")
        else:
            event_master.enable_event("block_place")

app.run()