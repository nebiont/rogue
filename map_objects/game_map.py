import tcod as libtcod
import yaml
from random import randint
from map_objects.tile import Tile
from map_objects.rectangle import Rect
from entity import Entity
from components.ai import BasicMonster
from components.fighter import Fighter
from components.item import Item
from item_functions import heal, cast_lightning
from render_functions import RenderOrder


class GameMap:
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.tiles = self.initialize_tiles()

	def initialize_tiles(self):
		tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]

		return tiles
	
	def make_map(self, max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities, max_monsters_per_room, max_items_per_room):
		rooms = []
		num_rooms = 0

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
				self.place_entities(new_room, entities, max_monsters_per_room, max_items_per_room)
				rooms.append(new_room)
				num_rooms += 1

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
	
	def place_entities(self, room, entities, max_monsters_per_room, max_items_per_room):
		# Get a random number of monsters
		number_of_monsters = randint(0, max_monsters_per_room)
		number_of_items = randint(0, max_items_per_room)

		# Load item list so it can be used to generate items
		item_stream = open(".\\data\\objects\\items.yaml", 'r')
		item_list = yaml.load(item_stream)
		total_item_chance = 0

		# Calculate total item loot chance weighting so that we can use this in our loot alogrithm
		for x in item_list.values():
			total_item_chance += x.get('loot_chance')


		for i in range(number_of_monsters):
			# Choose a random location in the room
			x = randint(room.x1 + 1, room.x2 - 1)
			y = randint(room.y1 + 1, room.y2 - 1)

			if not any([entity for entity in entities if entity.x == x and entity.y == y]):
				if randint(0, 100) < 80:
					fighter_component = Fighter(hp=10, defense=0, power=3)
					ai_component = BasicMonster()

					monster = Entity(x, y, 'o', libtcod.desaturated_green, 'Orc', blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)
				else:
					fighter_component = Fighter(hp=16, defense=1, power=4)
					ai_component = BasicMonster()

					monster = Entity(x, y, 'T', libtcod.darker_green, 'Troll', blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)

				entities.append(monster)

		
			

		for i in range(number_of_items):
			x = randint(room.x1 + 1, room.x2 - 1)
			y = randint(room.y1 + 1, room.y2 - 1)

			if not any([entity for entity in entities if entity.x == x and entity.y == y]):
				
				rand_item = randint(1, total_item_chance)
				

				item_chance = randint(0, 100)

				if item_chance < 70:
					item_component = Item(use_function=heal, amount=4)
					item = Entity(x, y, '!', libtcod.violet, 'Healing Potion', render_order=RenderOrder.ITEM, item=item_component)
					
				else:
					item_component = Item(use_function=cast_lightning, damage=20, maximum_range=5)
					item = Entity(x, y, '#', libtcod.yellow, 'Lightning Scroll', render_order=RenderOrder.ITEM, item=item_component)

				entities.append(item)
		  
	
	def is_blocked(self, x, y):
		if self.tiles[x][y].blocked:
			return True
		
		return False