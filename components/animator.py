import tcod as libtcod


class Animator:
    anim_type = None
    delta_x = None
    delta_y = None
    x = None
    y = None
    time = None
    
    def update(self):
        
        if not self.time == None:
        
            if self.time <= 0:
                self.anim_type = None
                self.time = None
                self.x = None
                self.y = None

            if self.anim_type == 'move':

                if self.x == None and self.y == None:
                    self.x = self.owner.x
                    self.y = self.owner.y
                    
                final_delta_x = self.delta_x * (libtcod.sys_get_last_frame_length() / self.time)
                final_delta_y = self.delta_y * (libtcod.sys_get_last_frame_length() / self.time)
                self.x += final_delta_x
                self.y += final_delta_y
                self.owner.x += round(self.x)
                self.owner.y += round(self.y)
                self.delta_x -= final_delta_x
                self.delta_y -= final_delta_y
                self.time -= libtcod.sys_get_last_frame_length()

    #speed is tiles / second
    def move(self, target_x, target_y, speed):
        self.anim_type = 'move'
        self.delta_x = target_x - self.owner.x
        self.delta_y = target_y - self.owner.y
        self.time = self.owner.distance(target_x, target_y) / speed