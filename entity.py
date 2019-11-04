import tcod as libtcod
import math
from render_functions import RenderOrder


#TODO: Make entities list a class attribute in the Entity class

class Entity:
	"""
	A generic object to represent players, enemies, items, etc.
	"""

	def __init__(self, x, y, char, color, name, description, blocks=False, render_order=RenderOrder.CORPSE, fighter=None, ai=None, item=None, inventory=None, stairs=None, level=None, equipment=None, equippable=None, role=None, abilities=None, animator=None):
		self.x = x
		self.y = y
		self.char = char
		self.color = color
		self.name = name
		self.description = description
		self.blocks = blocks
		self.render_order = render_order
		self.fighter = fighter
		self.ai = ai
		self.item = item
		self.inventory = inventory
		self.stairs = stairs
		self.level = level
		self.equipment = equipment
		self.equippable = equippable
		self.role = role
		self.abilities = abilities
		self.animator = animator

		if self.fighter:
			self.fighter.owner = self

		if self.ai:
			self.ai.owner = self

		if self.item:
			self.item.owner = self

		if self.inventory:
			self.inventory.owner = self
		
		if self.stairs:
			self.stairs.owner = self

		if self.level:
			self.level.owner = self

		if self.equipment:
			self.equipment.owner = self

		if self.equippable:
			self.equippable.owner = self
			if not self.item:
				item = Item()
				self.item = item
				self.item.owner = self

		if self.role:
			self.role.owner = self
			self.role.role_init()

		if self.animator:
			self.animator.owner = self

	def draw(self, engine: 'GameEngine'):
		if libtcod.map_is_in_fov(engine.fov_map, self.x, self.y) or (self.stairs and engine.game_map.tiles[self.x][self.y].explored) or (self.item and engine.game_map.tiles[self.x][self.y].explored):
			libtcod.console_set_default_foreground(engine.con, self.color)
			libtcod.console_put_char(engine.con, self.x, self.y, self.char, libtcod.BKGND_NONE)

	def clear(self, engine: 'GameEngine'):
		# erase the character that represents this object
		libtcod.console_put_char(engine.con, self.x, self.y, ' ', libtcod.BKGND_NONE)

	def move(self, dx, dy):
		# Move the entity by a given amount
		self.x += dx
		self.y += dy

	def move_towards(self, target_x, target_y, game_map, entities):
		dx = target_x - self.x
		dy = target_y - self.y
		distance = math.sqrt(dx ** 2 + dy ** 2)

		dx = int(round(dx / distance))
		dy = int(round(dy / distance))

		if not (game_map.is_blocked(self.x + dx, self.y + dy) or get_blocking_entities_at_location(entities, self.x + dx, self.y + dy)):
			self.move(dx, dy)
			
	def move_to(self, target_x, target_y):
		dx = target_x - self.x
		dy = target_y - self.y
		dx = (dx - math.copysign(1, dx)) + self.x
		dy = (dy - math.copysign(1, dy)) + self.y
		
		self.x = int(dx)
		self.y = int(dy)

	def move_astar(self, target, entities, game_map):
		# Create a FOV map that has the dimensions of the map
		fov = libtcod.map.Map(game_map.width, game_map.height, order='F')
		
		# Scan the current map each turn and set all the walls as unwalkable
		for y1 in range(game_map.height):
			for x1 in range(game_map.width):
				fov.transparent[x1,y1] = not game_map.tiles[x1][y1].block_sight
				fov.walkable[x1, y1] = not game_map.tiles[x1][y1].blocked

		# Scan all the objects to see if there are objects that must be navigated around
		# Check also that the object isn't self or the target (so that the start and the end points are free)
		# The AI class handles the situation if self is next to the target so it will not use this A* function anyway
		for entity in entities:
			if entity.blocks and entity != self and entity != target:
				# Set the tile as a wall so it must be navigated around
				fov.transparent[entity.x, entity.y] = True
				fov.walkable[entity.x, entity.y] = False

		# Allocate a A* path
		# The 1.41 is the normal diagonal cost of moving, it can be set as 0.0 if diagonal moves are prohibited
		my_path = libtcod.path_new_using_map(fov, 1.41)

		# Compute the path between self's coordinates and the target's coordinates
		libtcod.path_compute(my_path, self.x, self.y, target.x, target.y)

		# Check if the path exists, and in this case, also the path is shorter than 25 tiles
		# The path size matters if you want the monster to use alternative longer paths (for example through other rooms) if for example the player is in a corridor
		# It makes sense to keep path size relatively low to keep the monsters from running around the map if there's an alternative path really far away
		if not libtcod.path_is_empty(my_path) and libtcod.path_size(my_path) < 25:
			# Find the next coordinates in the computed full path
			x, y = libtcod.path_walk(my_path, True)
			if x or y:
				# Set self's coordinates to the next path tile
				self.x = x
				self.y = y
		else:
			# Keep the old move function as a backup so that if there are no paths (for example another monster blocks a corridor)
			# it will still try to move towards the player (closer to the corridor opening)
			self.move_towards(target.x, target.y, game_map, entities)

			# Delete the path to free memory
		libtcod.path_delete(my_path)

	def distance(self, x, y):
		return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

	def distance_to(self, other):
		dx = other.x - self.x
		dy = other.y - self.y
		return math.sqrt(dx ** 2 + dy ** 2)

class Text(Entity):

	def __init__(self, x, y, text, color, render_order=RenderOrder.UI):
		self.x = x
		self.y = y
		self.text = text
		self.color = color
		self.render_order = render_order
		self.blocks = False
		self.ai = None

	def draw(self, engine: 'GameEngine'):
		overlay = libtcod.console.Console(len(self.text), 1, order='F')
		overlay.print(0,0, self.text, fg=self.color, bg=None, bg_blend=libtcod.BKGND_NONE)
		overlay.blit(engine.con, self.x, self.y, 0, 0, 0, 0, 1.0, 0)

	def clear(self, engine: 'GameEngine'):
		return


def get_blocking_entities_at_location(entities, destination_x, destination_y):
	for entity in entities:
		if entity.blocks and entity.x == destination_x and entity.y == destination_y:
			return entity
	return None
