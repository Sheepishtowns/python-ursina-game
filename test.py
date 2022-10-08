from ursina import *
from perlin_noise import PerlinNoise
from numpy import floor

#VARIABLES
chunkSize = 16
freq = 24
amp = 5

app = Ursina(borderless=False)
noise = PerlinNoise(octaves=2, seed=100)


for i in range(chunkSize**2):
    block = Entity(model = "model/block.obj", texture = "texture/grass.png", rotation = (-90,0,0), collider="box")
    block.x = floor(i/chunkSize*2)
    block.z = floor(i%chunkSize*2)
    block.y = floor(noise([block.x/freq, block.z/freq]) * amp)
    #block.showTightBounds()


class Player(Entity):
    def __init__(self):
        super().__init__()
        self.model = "model/player.obj"
        self.texture = "texture/player.png"
        self.position = (0,6,0)
        self.scale=(0.4,0.4,0.4)
        self.collider = BoxCollider(self,(0,1.3,1),Vec3(self.model_bounds[0], self.model_bounds[1], self.model_bounds[2]-0.1))#custom box collider because original origin is slightly off
        self.init_jump_energy = 2
        self.jump_energy = 0

    def update(self):
        print("p"+str(self.y))
        if not self.intersects().entities and not self.jump_energy > 0:#gravity
            self.y -= 0.2
        if self.jump_energy > 0: 
            self.y += self.jump_energy*0.2
            self.jump_energy -= 0.2

    def input(self,key):
        if key == 'tab':    # press tab to toggle edit/play mode
            ec.enabled = not ec.enabled

        if held_keys["w"]:
            self.x += 0.08
            for object_ in self.intersects().entities:
                if object_.y > self.y - 2.2:#check if the block is higher than the self's current y level
                    print(object_.y)
                    self.x -= 0.08
        elif held_keys["s"]:
            self.x -= 0.08
            for object_ in self.intersects().entities:
                if object_.y > self.y - 2.2:#check if the block is higher than the self's current y level
                    print(object_.y)
                    self.x += 0.08
        elif held_keys["a"]:
            self.z += 0.08
            for object_ in self.intersects().entities:
                if object_.y > self.y - 2.2:#check if the block is higher than the self's current y level
                    print(object_.y)
                    self.z -= 0.08
        elif held_keys["d"]:
            self.z -= 0.08
            for object_ in self.intersects().entities:
                if object_.y > self.y - 2.2:#check if the block is higher than the self's current y level
                    print(object_.y)
                    self.z += 0.08

        if held_keys["space"]:
            
            if self.intersects().entities:
                self.jump_energy = self.init_jump_energy

ec = EditorCamera(rotation_smoothing=10, enabled=1, rotation=(30,30,0))
player = Player()


app.run()