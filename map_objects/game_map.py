import tcod as libtcod
import yaml
from random import randint
from game_messages import Message
from map_objects.tile import Tile
from map_objects.rectangle import Rect
from entity import Entity
from components.ai import BasicMonster
from components.fighter import Fighter
from components.item import Item
from components.stairs import Stairs
from item_functions import heal, cast_lightning, cast_fireball, cast_confuse, cast_polymorph
from random_utils import from_dungeon_level, random_choice_from_dict
from render_functions import RenderOrder
import definitions
import os

class GameMap:
	def __init__(self, width, height, dungeon_level=1):
		self.width = width
		self.height = height
		self.tiles = self.initialize_tiles()
		self.dungeon_level = dungeon_level

	def initialize_tiles(self):
		tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]

		return tiles
	
	def make_map(self, max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities):
		rooms = []
		num_rooms = 0
		center_of_last_room_x = None
		center_of_last_room_y = None

		for r in range(max_rooms):
			# random width and height
			w = randint(room_min_size, room_max_size)
			h = randint(room_min_size, room_max_size)

			# random position without going out of bound of map
			x = randint(0, map_width - w - 1)
			y = randint(0, map_height - h - 1)

			# 'Rect' class makes rectangles easier to work with
			new_room = Rect(x, y, w, h)

			# run through the other rooms and see if they intersect with this one
			for other_room in rooms:
				if new_room.intersect(other_room):
					break
			else:
				#This means there are no intersections so this room is valid
				
				# 'paint' room to maps tiles
				self.create_room(new_room)

				#center coordinates of new room will be useful later
				(new_x, new_y) = new_room.center()
				center_of_last_room_x = new_x
				center_of_last_room_y = new_y

				if num_rooms == 0:
					#this si the first room where the player starts at
					player.x = new_x
					player.y = new_y
				else:
					#all rooms after the first:
					#connect it to the previous room with a tunnel

					#center coordinates of previous room
					(prev_x, prev_y) = rooms[num_rooms - 1].center()

					#flip a coin (random number that is either 0 or 1)
					if randint(0, 1) == 1:
						#first move horizontally, then vertically
						self.create_h_tunnel(prev_x, new_x, prev_y)
						self.create_v_tunnel(prev_y, new_y, new_x)
					else:
						#first move vertically, then horizontally
						self.create_v_tunnel(prev_y, new_y, prev_x)
						self.create_h_tunnel(prev_x, new_x, new_y)
				#finally, append the new room to the list
				self.place_entities(new_room, entities)
				rooms.append(new_room)
				num_rooms += 1

		stairs_component = Stairs(self.dungeon_level + 1)
		down_stairs = Entity(center_of_last_room_x, center_of_last_room_y, '>', libtcod.white,
							'Stairs', 'Stairs down to floor {0}'.format(self.dungeon_level + 1), render_order=RenderOrder.STAIRS, stairs=stairs_component)
		entities.append(down_stairs)
	def create_room(self, room):
		# go through the tiles in the rectangle and make them passable
		for x in range(room.x1 + 1, room.x2):
			for y in range(room.y1 + 1, room.y2):
				self.tiles[x][y].blocked = False
				self.tiles[x][y].block_sight = False

	def create_h_tunnel(self, x1, x2, y):
		for x in range(min(x1, x2), max(x1, x2) + 1):
			self.tiles[x][y].blocked = False
			self.tiles[x][y].block_sight = False

	def create_v_tunnel(self, y1, y2, x):
		for y in range(min(y1, y2), max(y1, y2) + 1):
			self.tiles[x][y].blocked = False
			self.tiles[x][y].block_sight = False
	
	def place_entities(self, room, entities):
		# Get a random number of monsters
		max_monsters_per_room = from_dungeon_level([[2, 1], [3, 4], [5, 6]], self.dungeon_level)
		max_items_per_room = from_dungeon_level([[1, 1], [2, 4]], self.dungeon_level)
		number_of_monsters = randint(0, max_monsters_per_room)
		number_of_items = randint(0, max_items_per_room)
		monster_stream = open(os.path.join(definitions.ROOT_DIR,'data','objects','monsters.yaml'), 'r')
		monster_list = yaml.load(monster_stream)
		monster_chances = {}		
		for i in monster_list:
			monster_chances[i] = from_dungeon_level(monster_list[i].get('spawn_chance'), self.dungeon_level)

		# Load item list so it can be used to generate items
		item_stream = open(os.path.join(definitions.ROOT_DIR,'data','objects','items.yaml'), 'r')
		item_list = yaml.load(item_stream)
		item_chances = {}
		for i in item_list:
			item_chances[i] = item_list[i].get('loot_chance')


		for i in range(number_of_monsters):
			# Choose a random location in the room
			x = randint(room.x1 + 1, room.x2 - 1)
			y = randint(room.y1 + 1, room.y2 - 1)

			if not any([entity for entity in entities if entity.x == x and entity.y == y]):
				monster_roll = random_choice_from_dict(monster_chances)
				monster_object = monster_list[monster_roll]

				fighter_component = Fighter(monster_object.get('hp'), monster_object.get('defense'), monster_object.get('power'), monster_object.get('xp'))
				ai_component = BasicMonster()

				monster = Entity(x, y, monster_object.get('char'), eval(monster_object.get('color')), monster_object.get('name'), monster_object.get('description'), blocks=True, render_order=eval(monster_object.get('render_order')), fighter=fighter_component, ai=ai_component)

				entities.append(monster)

		for i in range(number_of_items):
			x = randint(room.x1 + 1, room.x2 - 1)
			y = randint(room.y1 + 1, room.y2 - 1)

			if not any([entity for entity in entities if entity.x == x and entity.y == y]):
				item_roll = random_choice_from_dict(item_chances)
				item_object = item_list[item_roll]
				args = {}
				kwargs = {}

				for k, v in item_object['args'].items():
					args[k] = eval(v)

				for k, v in item_object['kwargs'].items():
					kwargs[k] = v

				item_component = Item(**args, **kwargs)
				item = Entity(x, y, item_object.get('char'), eval(item_object.get('color')), item_object.get('name'), item_object.get('description'), render_order=eval(item_object.get('render_order')), item=item_component)

				entities.append(item)
		  
	
	def is_blocked(self, x, y):
		if self.tiles[x][y].blocked:
			return True
		
		return False

	def next_floor(self, player, message_log, constants):
		self.dungeon_level += 1
		entities = [player]


		self.tiles = self.initialize_tiles()
		self.make_map(constants['max_rooms'],constants['room_min_size'], constants['room_max_size'],
					constants['map_width'], constants['map_height'], player, entities)

		player.fighter.heal(player.fighter.max_hp // 2)

		message_log.add_message(Message('You take a moment to rest and recover your strength.', libtcod.light_violet))	

		return entities