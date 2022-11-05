from ursina import *
import worldgen

app = Ursina(borderless=False)

chunk = worldgen.generate_chunk()

for block_ in chunk:
    if worldgen.ifblockcanbeseen(block_, chunk):
        if block_[3] == 1:
            block = Entity(model = "model/block.obj", texture = "texture/plain_dirt.png", rotation = (-90,0,0), collider="box")
        elif block_[3] == 0:
            block = Entity(model = "model/block.obj", texture = "texture/grass.png", rotation = (-90,0,0), collider="box")
            
        block.x = block_[0]
        block.z = block_[2]
        block.y = block_[1]
    
class Player(Entity):
    def __init__(self):
        super().__init__()
        self.model = "model/player.obj"
        self.texture = "texture/player.png"
        self.position = (0,6,0)
        self.scale=(0.4,0.4,0.4)
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


ec = EditorCamera(rotation_smoothing=10, enabled=1, rotation=(30,30,0))
player = Player()


app.run()