import tcod as libtcod


class Animator:
    anim_type = None
    delta_x = None
    delta_y = None
    time = None
    
    def update(self):
        
        if not self.time == None:
        
            if self.time <= 0:
                self.anim_type = None
                self.time = None

            if self.anim_type == 'move':
                final_delta_x = self.delta_x * (libtcod.sys_get_last_frame_length() / self.time)
                final_delta_y = self.delta_y * (libtcod.sys_get_last_frame_length() / self.time)
                self.owner.x += final_delta_x
                self.owner.y += final_delta_y
                self.delta_x -= final_delta_x
                self.delta_y -= final_delta_y
                self.time -= libtcod.sys_get_last_frame_length()

    #speed is tiles / second
    def move(self, target_x, target_y, speed):
        self.anim_type = 'move'
        self.delta_x = target_x - self.owner.x
        self.delta_y = target_y - self.owner.y
        self.time = self.owner.distance(target_x, target_y) / speed