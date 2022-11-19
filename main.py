from ursina import *
import json
import os
import worldgen
from world_event_handle import *

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
chunk = worldgen.generate_chunk()

visible_chunk = []
for block_ in chunk:
    if worldgen.ifblockcanbeseen(block_, chunk):
        visible_chunk.append(block_)
        block = Entity(model = os.path.join("model/", blockdata["fullblocks"][str(block_[3])]["model"]), texture = os.path.join("texture/", blockdata["fullblocks"][str(block_[3])]["texture"]), rotation = (-90,0,0), collider="box")
        block.x = block_[0]
        block.z = block_[2]
        block.y = block_[1]

#get rid of load screen after world has initially loaded
destroy(box)
destroy(text1)

class Player(Entity):
    def __init__(self):
        super().__init__()
        self.model = "model/player.obj"
        self.texture = "texture/player.png"
        self.position = (0,6,0)
        self.scale = (0.4,0.4,0.4)
        self.collider = BoxCollider(self,(0,1.3,1),Vec3(self.model_bounds[0], self.model_bounds[1], self.model_bounds[2]-0.1))#custom box collider because original origin is slightly off
        self.init_jump_energy = 2.2
        self.jump_energy = 0

    def update(self):
        if self.jump_energy > 0: 
            self.y += self.jump_energy*0.1
            if self.jump_energy > 0.1:
                self.jump_energy -= 0.1
            else:
                self.jump_energy = 0
    
        if not self.intersects().entities and not self.jump_energy > 0:#gravity
            self.y -= 0.2
            for object_ in self.intersects().entities:
                self.y = object_.y + 2.2

    def input(self,key):
        if key == 'tab':    # press tab to toggle edit/play mode
            ec.enabled = not ec.enabled

        if held_keys["w"]:
            self.x += 0.08
            for object_ in self.intersects().entities:
                if object_.y > round(self.y) - 2:#check if the block is higher than the self's current y level
                    print(object_.y)
                    self.x -= 0.08
        elif held_keys["s"]:
            self.x -= 0.08
            for object_ in self.intersects().entities:
                if object_.y > round(self.y) - 2:#check if the block is higher than the self's current y level
                    print(object_.y)
                    self.x += 0.08
        elif held_keys["a"]:
            self.z += 0.08
            for object_ in self.intersects().entities:
                if object_.y > round(self.y) - 2:#check if the block is higher than the self's current y level
                    print(object_.y)
                    self.z -= 0.08
        elif held_keys["d"]:
            self.z -= 0.08
            for object_ in self.intersects().entities:
                if object_.y > round(self.y) - 2:#check if the block is higher than the self's current y level
                    print(object_.y)
                    self.z += 0.08

        if held_keys["space"]:
            if self.intersects().entities:
                self.jump_energy = self.init_jump_energy


event_master = EventsMaster(blockdata, visible_chunk)

def update():
    actions = event_master.trigger(mouse)
    if "breaking" in actions:#apply the breaking animation on blocks
        indicator = Entity(name = "break-indicate", model = os.path.join("model/", blockdata["specialblocks"]["break-indicate"]["model"]), texture = os.path.join("texture/", blockdata["specialblocks"]["break-indicate"]["animation"], "/breaking-"+str(actions["breaking"][1])+".png"), rotation = (-90,0,0), position = actions["breaking"][0], scale = blockdata["specialblocks"]["break-indicate"]["scale"])
    else:
        for e in scene.entities:
            if e.name == "break-indicate":
                destroy(e)
    if "destroy" in actions:
        global chunk, visible_chunk
        chunk = [block for block in chunk if not Vec3(block[0], block[1], block[2]) == actions["destroy"].position]#remove block from world list
        destroy(actions["destroy"])

        new_visible_chunk = []
        for blk in chunk:
            if worldgen.ifblockcanbeseen(blk, chunk):
                new_visible_chunk.append(blk)
        differ = worldgen.get_difference(visible_chunk, new_visible_chunk)
        visible_chunk = new_visible_chunk
        event_master.chunkdata = visible_chunk
        for blk in differ[1]:
            block = Entity(model = os.path.join("model/", blockdata["fullblocks"][str(blk[3])]["model"]), texture = os.path.join("texture/", blockdata["fullblocks"][str(blk[3])]["texture"]), rotation = (-90,0,0), collider="box")
            block.x = blk[0]
            block.z = blk[2]
            block.y = blk[1]
    if "place" in actions:
        block = Entity(model = os.path.join("model/", blockdata["fullblocks"][str(actions["place"][1])]["model"]), texture = os.path.join("texture/", blockdata["fullblocks"][str(actions["place"][1])]["texture"]), rotation = (-90,0,0), collider="box")
        block.position = actions["place"][0]
        chunk.append(list(actions["place"][0])+[actions["place"][1]])
        new_visible_chunk = []
        for blk in chunk:
            if worldgen.ifblockcanbeseen(blk, chunk):
                new_visible_chunk.append(blk)
        differ = worldgen.get_difference(visible_chunk, new_visible_chunk)
        visible_chunk = new_visible_chunk
        event_master.chunkdata = visible_chunk
        for blk in differ[0]:
            for e in scene.entities:
                if list(e.position) == blk[:3]:
                    destroy(e)


ec = EditorCamera(rotation_smoothing=10, enabled=1, rotation=(30,30,0))
player = Player()

app.run()