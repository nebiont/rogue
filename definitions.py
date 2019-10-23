import os
import tcod as libtcod

class Definitions:
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
ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) 
DEV_TOOLS = os.path.join(ROOT_DIR, 'devtools')