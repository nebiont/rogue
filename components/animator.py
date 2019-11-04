import tcod as libtcod
from entity import Entity

#TODO: Could split the update types out into each animation method, and then maintain an instance variable list that tracks what animation methods to call and then call them in the update funciton of the Animator class.
#TODO: Handle allowing the animator to set engine.fov_recompute = True to allow some animations to update the player FOV.
class Animator:
	animators = []
	blocking = 0
	
	def __init__(self):
		self.caller = None

	def update(self):
		return
	
	def check_if_complete(self):
		if self.time <= 0:
			if self.blocking == True:
				Animator.blocking -= 1
			# Remove this animator as it is no longer needed
			self.remove()
			return True

	def remove(self):
		Animator.animators.remove(self)
		del self

#speed is tiles / second
class Move_To(Animator):
	animators = None

	def __init__(self, owner: Entity, target_x: int, target_y: int, speed: int, caller=None, blocking=False):
		self.target_x = target_x
		self.target_y = target_y
		self.speed = speed
		self.delta_x = None
		self.delta_y = None
		self.x = None
		self.y = None
		self.time = None
		self.caller = caller
		self.complete = None
		self.owner = owner
		self.blocking = blocking
		Animator.animators.append(self)


		if caller:
			self.caller = caller
		#If this is a blocking animation we add 1 to Animator.blocking and then read it in the game loop 
		#so that we can set the gamestate to blocking. We use an int rather than a bool so that we can keep track of how many
		#animators are blocking. We only unblock the game state when all blocking animators are done.
		if self.blocking == True:
			Animator.blocking += 1

		#Calculate delta x,y values
		self.delta_x = target_x - self.owner.x
		self.delta_y = target_y - self.owner.y

		#Calculate how long the animation will take in seconds based on speed
		self.time = self.owner.distance(target_x, target_y) / speed

	def update(self):
		#only run if there is animation time remaining
		if not self.time == None:
		
			#if animation time is over, stop update function and clear attributes
			if self.check_if_complete():
				return


			#because we have to round our coordinate values before drawing, we need to store what the float values of the x, y coords are
			#we will adjust these values and then set the entiites x,y to match a rounded value of these. then we can refer to these on the next tick
			if self.x == None and self.y == None:
				self.x = self.owner.x
				self.y = self.owner.y

			final_delta_x = self.delta_x * (libtcod.sys_get_last_frame_length() / self.time)
			final_delta_y = self.delta_y * (libtcod.sys_get_last_frame_length() / self.time)
			self.x += final_delta_x
			self.y += final_delta_y

			# We clamp to the target coordinates, otherwise overshooting the target is possible due to the rounding.
			# The if statements are what clamps it
			if abs(self.target_x - abs(round(self.x))) <= 1:
				self.owner.x = self.target_x
			else:
				self.owner.x = round(self.x)

			if abs(self.target_y - abs(round(self.y))) <= 1:
				self.owner.y = self.target_y
			else: 
				self.owner.y = round(self.y)

			self.delta_x -= final_delta_x
			self.delta_y -= final_delta_y

			self.time -= libtcod.sys_get_last_frame_length()

class Flash(Animator):
	animators = None


	def __init__(self, entity: Entity, time: int, color: libtcod.color.Color, caller=None, blocking=False):
		"""
		Flashes to a color and back over a period of time.
		Args:
			entity (Entity): the entity to flash
			time (int): how long the flash should take
			color (libtcod.color.Color): the color to flash to
			caller: what called this animation (ability etc), only used if the animation is a blocking animation
			blocking: should this animation block the game from progessing until complete
		"""
		self.entity = entity
		self.time = time
		self.final_color = color
		self.caller = caller
		self.original_color = self.entity.color
		self.current_color = self.original_color
		self.blocking = blocking
		Animator.animators.append(self)
		#If this is a blocking animation we add 1 to Animator.blocking and then read it in the game loop 
		#so that we can set the gamestate to blocking. We use an int rather than a bool so that we can keep track of how many
		#animators are blocking. We only unblock the game state when all blocking animators are done.
		if self.blocking == True:
			Animator.blocking += 1

		self.delta_r = (self.final_color[0] - self.original_color[0]) / (self.time / 2)
		self.delta_g = (self.final_color[1] - self.original_color[1]) / (self.time / 2)
		self.delta_b = (self.final_color[2] - self.original_color[2]) / (self.time / 2)
		self.delta_color = [self.delta_r, self.delta_g, self.delta_b]

	def update(self):
		#only run if there is animation time remaining
		if not self.time == None:
		
			#if animation time is over, stop update function and clear attributes
			if self.check_if_complete():
				self.entity.color = self.original_color

			# if we've hit the final color lets swap the sign on delta color so that we transition back to the original color
			if self.current_color == self.final_color:
				for i, color in enumerate(self.delta_color):
					self.delta_color[i] = color * -1


			# Set current color
			self.current_color = [x + int(y * libtcod.sys_get_last_frame_length()) for x, y in zip (self.current_color, self.delta_color)]
			for i, color in enumerate(self.current_color):
				if color > 255:
					self.current_color[i] = 255
				if color < 0:
					self.current_color[i] = 0
			self.entity.color = self.current_color

			self.time -= libtcod.sys_get_last_frame_length()



