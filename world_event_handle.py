import time
from ursina import Vec3

class EventsMaster:
    def __init__(self, blockdata, chunkdata):
        self.registered_events = ["block_break", "block_place"] # when adding new event, it must be recorded here
        self.actives = {}
        self.cooldowns = {"block_place":150}#also add a cooldown if you wish the event to not execute continuously
        self.cooldown_records = {}
        self.blockdata = blockdata
        self.chunkdata = chunkdata

    def trigger(self, mouse):
        self.mouse = mouse

        for event in self.registered_events:
            if event in self.cooldowns:
                now = round(time.time()*1000)
                if event in self.cooldown_records:
                    passed = now - self.cooldown_records[event]
                    if passed >= self.cooldowns[event]:
                        self.cooldown_records[event] = now
                        event_func = getattr(self, event)
                        event_func()
                else:
                    self.cooldown_records[event] = now
                    event_func = getattr(self, event)
                    event_func()
            else:
                event_func = getattr(self, event)
                event_func()

        actions = self.process()
        return actions
    #---------------------------the event stuff---------------------------------------
    def block_break(self):
        if not self.mouse.collision == None:
            hitinfo = self.mouse.collision
            hovered_entity = hitinfo.entity
            if self.mouse.left == True:
                if "breaking" in self.actives:
                    if not self.actives["breaking"][0].position == hovered_entity.position:#check if player has changed to mine another block
                        self.actives["breaking"] = [hovered_entity, round(time.time()*1000)]
                else:
                    self.actives["breaking"] = [hovered_entity, round(time.time()*1000)]
            else:
                if "breaking" in self.actives:
                    self.actives.pop("breaking")

    def block_place(self):
        if "place" in self.actives:
            self.actives.pop("place")
        if not self.mouse.collision == None:
            hitinfo = self.mouse.collision
            hovered_entity = hitinfo.entity
            if self.mouse.right == True and self.actives == {}:
                    print(hitinfo.normal*2)
                    if not self.getBlockDat(hovered_entity.position + Vec3(hitinfo.normal[0], hitinfo.normal[2], -hitinfo.normal[1])*2): #have to change the order of values because hitinfo.normal is actually messed up
                        self.actives["place"] = [hovered_entity.position + Vec3(hitinfo.normal[0], hitinfo.normal[2], -hitinfo.normal[1])*2, 1]

    #------------------------------ends--------------------------------------------------------
    def getBlockDat(self, coords):
        for block in self.chunkdata:
            if block[0] == coords[0] and block[1] == coords[1] and block[2] == coords[2]:
                return block
        return False

    def process(self):
        actions = {}
        for event in list(self.actives): #list() to avoid dictionary changed size error
            if event == "breaking":
                block_breaking = self.getBlockDat(self.actives["breaking"][0].position)
                hardness = self.blockdata["fullblocks"][str(block_breaking[3])]["hardness"]#get hardness by id
                time_requires = hardness*500
                time_mined = round(time.time()*1000) - self.actives["breaking"][1]
                if time_mined >= time_requires:
                    actions["destroy"] = self.actives["breaking"][0]
                    self.actives.pop("breaking")
                else:
                    percentage = time_mined/time_requires*100
                    actions["breaking"] = [self.actives["breaking"][0].position, round(percentage/10)]
            else:
                actions[event] = self.actives[event]
        
        return actions
     