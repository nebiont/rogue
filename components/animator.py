import tcod as libtcod

#TODO: Handle allowing the animator to set engine.fov_recompute = True to allow some animations to update the player FOV.
class Animator:
    animators = []
    blocking = 0

    def __init__(self):
        self.anim_type = None
        self.delta_x = None
        self.delta_y = None
        self.x = None
        self.y = None
        self.time = None
        self.caller = None
        self.complete = None
        Animator.animators.append(self)
    
    def update(self):
        #only run if there is animation time remaining
        if not self.time == None:
            
            #if animation time is over, stop update function and clear attributes
            if self.time <= 0:
                self.anim_type = None
                self.time = None
                self.x = None
                self.y = None
                self.complete = True
                Animator.blocking -= 1
                return None
            if self.anim_type == 'move':

                #because we have to round our coordinate values before drawing, we need to store what the float values of the x, y coords are
                #we will adjust these values and then set the entiites x,y to match a rounded value of these. then we can refer to these on the next tick
                if self.x == None and self.y == None:
                    self.x = self.owner.x
                    self.y = self.owner.y

                final_delta_x = self.delta_x * (libtcod.sys_get_last_frame_length() / self.time)
                final_delta_y = self.delta_y * (libtcod.sys_get_last_frame_length() / self.time)
                self.x += final_delta_x
                self.y += final_delta_y
                self.owner.x = round(self.x)
                self.owner.y = round(self.y)
                self.delta_x -= final_delta_x
                self.delta_y -= final_delta_y
                self.time -= libtcod.sys_get_last_frame_length()

    #speed is tiles / second
    def move_to(self, target_x, target_y, speed, caller, blocking=False):
        self.caller = caller
        #If this is a blocking animation we add 1 to Animator.blocking and then read it in the game loop 
        #so that we can set the gamestate to blocking. We use an int rather than a bool so that we can keep track of how many
        #animators are blocking. We only unblock the game state when all blocking animators are done.
        if blocking == True:
            Animator.blocking += 1
        
        # Tell upadte function what type of animation we are doing
        self.anim_type = 'move'

        #Calculate delta x,y values
        self.delta_x = target_x - self.owner.x
        self.delta_y = target_y - self.owner.y

        #Calculate how long the animation will take in seconds based on speed
        self.time = self.owner.distance(target_x, target_y) / speed