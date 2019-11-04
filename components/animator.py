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
			return None

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
			self.check_if_complete()


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
		self.color = color
		self.caller = caller
		self.blocking = blocking
		Animator.animators.append(self)

	def update(self):
		#only run if there is animation time remaining
		if not self.time == None:
		
			#if animation time is over, stop update function and clear attributes
			self.check_if_complete()

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

def flash(self, entity: Entity, time: int, color: libtcod.color.Color, caller=None, blocking=False):
	"""
	Flashes to a color and back over a period of time.
	Args:
		entity (Entity): the entity to flash
		time (int): how long the flash should take
		color (libtcod.color.Color): the color to flash to
		caller: what called this animation (ability etc), only used if the animation is a blocking animation
		blocking: should this animation block the game from progessing until complete
	"""
	if caller:
		self.caller = caller
	#If this is a blocking animation we add 1 to Animator.blocking and then read it in the game loop 
	#so that we can set the gamestate to blocking. We use an int rather than a bool so that we can keep track of how many
	#animators are blocking. We only unblock the game state when all blocking animators are done.
	if blocking == True:
		Animator.blocking += 1
	
	# Tell upadte function what type of animation we are doing
	self.anim_type = 'flash'

	#Calculate delta x,y values
	self.delta_x = target_x - self.owner.x
	self.delta_y = target_y - self.owner.y

	#Calculate how long the animation will take in seconds based on speed
	self.time = self.owner.distance(target_x, target_y) / speed

