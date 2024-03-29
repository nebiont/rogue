import tcod as libtcod

from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level
from components.equipment import Equipment
from components.role import Warrior, Rogue, Ranger, Warlock, Paladin
from components.animator import Animator

from entity import Entity

from game_messages import MessageLog

from game_states import GameStates

from map_objects.game_map import GameMap

from render_functions import RenderOrder

def get_constants():
	window_title = "Dans Spicy Calzone"

	screen_width = 100
	screen_height = 65

	bar_width = 25
	panel_height = 9
	panel_y = screen_height - panel_height

	message_x = bar_width + 2
	message_width = screen_width - bar_width - 2
	message_height = panel_height - 1

	map_width = 100
	map_height = screen_height - panel_height

	room_max_size = 12
	room_min_size = 6
	max_rooms = 30

	fov_algorithm = libtcod.FOV_PERMISSIVE_2
	fov_light_walls = True
	fov_radius = 10


	
	colors = {
		'dark_wall': libtcod.Color(0, 0, 100),
		'dark_ground': libtcod.Color(50, 50, 150),
		'light_wall': libtcod.Color(130, 110, 50),
		'light_ground': libtcod.Color(200, 180, 50)
	}

	constants = {
		'window_title': window_title,
		'screen_width': screen_width,
		'screen_height': screen_height,
		'bar_width': bar_width,
		'panel_height': panel_height,
		'panel_y': panel_y,
		'message_x': message_x,
		'message_width': message_width,
		'message_height': message_height,
		'map_width': map_width,
		'map_height': map_height,
		'room_max_size': room_max_size,
		'room_min_size': room_min_size,
		'max_rooms': max_rooms,
		'fov_algorithm': fov_algorithm,
		'fov_light_walls': fov_light_walls,
		'fov_radius': fov_radius,
		'colors': colors
	}

	return constants

def get_game_variables(constants, player):
	entities = [player]

	game_map = GameMap(constants['map_width'], constants['map_height'])
	game_map.make_map(constants['max_rooms'], constants['room_min_size'], constants['room_max_size'],
		constants['map_width'], constants['map_height'], player, entities)

	message_log = MessageLog(constants['message_x'], constants['message_width'], constants['message_height'])
	game_state = GameStates.PLAYERS_TURN

	return player, entities, game_map, message_log, game_state

def get_dummy_player(role):
	fighter_component = Fighter(hp=100, defense=12, power=12, hitdie=[1,8], con=11, dmg=[1,6])
	inventory_component = Inventory(26)
	level_component = Level()
	equipment_component = Equipment()
	animator_component = Animator()
	role_component = role
	player = Entity(0, 0, 1, libtcod.white, 'Player', 'Handsome fellow', blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component, inventory=inventory_component, level=level_component, equipment=equipment_component, role=role_component, animator=animator_component)
	
	return player

