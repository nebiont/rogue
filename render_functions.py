import tcod as libtcod
from enum import Enum, auto
from game_states import GameStates
from menus import inventory_menu, entity_description, level_up_menu, character_screen, message_box, role_menu
from fov_functions import recompute_fov
import math

class RenderOrder(Enum):
	STAIRS = auto()
	CORPSE = auto()
	ITEM = auto()
	ACTOR = auto()

def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
	bar_width = int(float(value) / maximum * total_width)

	libtcod.console_set_default_background(panel, back_color)
	libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

	libtcod.console_set_default_background(panel, bar_color)
	if bar_width > 0:
		libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

	libtcod.console_set_default_foreground(panel, libtcod.white)
	libtcod.console_print_ex(panel, int(x + total_width / 2), y, libtcod.BKGND_NONE, libtcod.CENTER, '{0}: {1}/{2}'.format(name, value, maximum))


def render_all(con, panel, mouse, entities, player, game_map, fov_map, fov_recompute, message_log, screen_width, screen_height, bar_width, panel_height, panel_y, colors, game_state, description_list, description_index, cursor_radius, target_fov_map, fov_map_no_walls):

	# draw all the tiles in the game map
	if fov_recompute:
		for y in range(game_map.height):
			for x in range(game_map.width):
				visible = libtcod.map_is_in_fov(fov_map, x, y)
				wall = game_map.tiles[x][y].block_sight

				if visible:
					if wall:
						libtcod.console_set_char_background(con, x, y, colors.get('light_wall'), libtcod.BKGND_SET)
					else:
						libtcod.console_set_char_background(con, x, y, colors.get('light_ground'), libtcod.BKGND_SET)
					game_map.tiles[x][y].explored = True
				elif game_map.tiles[x][y].explored:
					if wall:
						libtcod.console_set_char_background(con, x, y, colors.get('dark_wall'), libtcod.BKGND_SET)
					else:
						libtcod.console_set_char_background(con, x, y, colors.get('dark_ground'), libtcod.BKGND_SET)			

	#draw all entities in the list
	entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)
	for entity in entities_in_render_order:
		draw_entity(con, entity, fov_map, game_map)

	libtcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)
	
	draw_cursor(mouse, cursor_radius, game_state, target_fov_map, fov_map_no_walls, screen_width, screen_height)
	
	#clear info panel
	libtcod.console_set_default_background(panel, libtcod.black)
	libtcod.console_clear(panel)

	# Print the game messages, one line at a time
	y = 1
	for message in message_log.messages:
		libtcod.console_set_default_foreground(panel, message.color)
		libtcod.console_print_ex(panel, message_log.x, y, libtcod.BKGND_NONE, libtcod.LEFT, message.text)
		y += 1

	render_bar(panel, 1, 1, bar_width, 'HP', player.fighter.hp, player.fighter.max_hp, libtcod.light_red, libtcod.darker_red)
	libtcod.console_print_ex(panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT, 'Dungeon Level: {0}'.format(game_map.dungeon_level))
	libtcod.console_blit(panel, 0, 0, screen_width, panel_height, 0, 0, panel_y)

	if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
		if game_state == GameStates.SHOW_INVENTORY:
			inventory_title = 'Press the key next to an item to use it, or Esc to cancel.'
		else:
			inventory_title = 'Press the key next to an item to drop it, or Esc to cancel.'

		inventory_menu(con, inventory_title, player.inventory, 50, screen_width, screen_height)

	elif game_state == GameStates.LEVEL_UP:
		level_up_menu(con, 'Level up! Choose a stat to raise:', player, 40, screen_width, screen_height)

	elif game_state == GameStates.CHARACTER_SCREEN:
		character_screen(player, 30, screen_width, screen_height)

	elif len(description_list) > 0:
		entity_description(con, description_list, description_index, 50, screen_width, screen_height)
	


def clear_all(con, entities):
	for entity in entities:
		clear_entity(con, entity)

def draw_entity(con, entity, fov_map, game_map):
	if libtcod.map_is_in_fov(fov_map, round(entity.x), round(entity.y)) or (entity.stairs and game_map.tiles[entity.x][entity.y].explored) or (entity.item and game_map.tiles[entity.x][entity.y].explored):
		libtcod.console_set_default_foreground(con, entity.color)
		libtcod.console_put_char(con, round(entity.x), round(entity.y), entity.char, libtcod.BKGND_NONE)

def clear_entity(con, entity):
	# erase the character that represents this object
	libtcod.console_put_char(con, round(entity.x), round(entity.y), ' ', libtcod.BKGND_NONE)

def draw_cursor(mouse, cursor_radius, game_state, target_fov_map, fov_map_no_walls, screen_width, screen_height):
	
	#Checks to see that the item we are using has no radius so that we dont waste time computing a target reticule
	if cursor_radius == 1 or cursor_radius == None:
		cursor = libtcod.console_new(1, 1)
		libtcod.console_set_default_foreground(cursor, libtcod.white)
		cursor.draw_rect(0, 0, 1, 1, 0, bg=libtcod.white)
		libtcod.console_blit(cursor, 0, 0, 1, 1, 0, mouse.cx, mouse.cy, 1.0, 0.7)
	
	# If we have a radius greater than one then draw a circle with a radius of cursor_radius. Game state needs to be targetting, this makes it so when we cancel targetting our cursor goes back to normal
	elif game_state == GameStates.TARGETING:
		#I needed to add a buffer to the screen width otherwise the targeting reticule would wrap to the otehr side of the screen when it was on the left side.
		cursor = libtcod.console.Console(screen_width + 20, screen_height)
		libtcod.console_set_default_background(cursor, [245, 245, 245])
		libtcod.console_set_key_color(cursor, [245, 245, 245])
		cursor.draw_rect(0,0, screen_width, screen_height,0,bg=[245, 245, 245])

		#Compute FOV from the cursors perspective. This makes it so walls etc. will block our reticule from showing green
		recompute_fov(target_fov_map, mouse.cx, mouse.cy, cursor_radius, light_walls=False, algorithm=libtcod.FOV_RESTRICTIVE)

		#Check all coords within the target radius from our cursors
		for x in range(mouse.cx - cursor_radius, mouse.cx + cursor_radius + 1):
			for y in range(mouse.cy - cursor_radius, mouse.cy + cursor_radius + 1):
				if math.sqrt((x - mouse.cx) ** 2 + (y - mouse.cy) ** 2) <= cursor_radius:
					#This FOV is computer from the player perspective, but with walls not lighting. This makes it so that if our cursors is on a wall the reticule will be red.
					if not libtcod.map_is_in_fov(fov_map_no_walls, x, y):
						cursor.draw_rect(x,y,1,1,0,bg=libtcod.red)
					#Check FOV of the cursors so that walls will block our reticule. If coordinate is in FOV we color it green.
					elif libtcod.map_is_in_fov(target_fov_map, x, y):
						cursor.draw_rect(x,y,1,1,0,bg=libtcod.light_green)
					else:
						cursor.draw_rect(x,y,1,1,0,bg=libtcod.red)
		libtcod.console_blit(cursor, 0, 0, 0, 0, 0,0, 0, 0, 0.4)

				
	
