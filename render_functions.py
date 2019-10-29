import tcod as libtcod
from enum import Enum, auto
from game_states import GameStates
from menus import inventory_menu, entity_description, level_up_menu, character_screen, message_box, role_menu
from fov_functions import recompute_fov
import math
import os
import definitions
from event_manager import *

class RenderOrder(Enum):
	STAIRS = auto()
	CORPSE = auto()
	ITEM = auto()
	ACTOR = auto()
class Renderer:

	def __init__(self, evmanager, game_engine):
		"""
		evmanager (EventManager): Allows posting messages to the event queue.
		model (GameEngine): a strong reference to the game Model.
				
		Attributes:
		isinitialized (bool): pygame is ready to draw.
		screen (pygame.Surface): the screen surface.
		clock (pygame.time.Clock): keeps the fps constant.
		smallfont (pygame.Font): a small font.
		"""
		
		self.evmanager = evmanager
		evmanager.RegisterListener(self)
		self.engine = game_engine
		self.isinitialized = False
		self.screen = None
		
	def state_control(self, state):
		switcher = {
			GameStates.MAIN_MENU: None,
			GameStates.PLAYERS_TURN: self.render_all
		}
		func = switcher.get(state)
		if not func == None:
			func()
	
	def notify(self, event):
		"""
		Receive events posted to the message queue. 
		"""

		if isinstance(event, InitializeEvent):
			self.initialize()
		elif isinstance(event, QuitEvent):
			# shut down the pygame graphics
			self.isinitialized = False
			#TODO: add quit function from libtcod
			#pygame.quit()
		elif isinstance(event, TickEvent):
			self.state_control(self.engine.state.peek())

	def initialize(self):
		"""
		Set up the pygame graphical display and loads graphical resources.
		"""
		#Get game engine.constants
		self.constants = self.engine.constants

		#Get colors
		self.colors = self.constants['colors']

		# Limit FPS to 100 so we dont kill CPUs
		#libtcod.sys_set_fps(60)

		# Load font and create root console (what you see)
		libtcod.console_set_custom_font(os.path.join(definitions.ROOT_DIR,'Nice_curses_12x12.png'), libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
		libtcod.console_init_root(self.constants['screen_width'], self.constants['screen_height'], self.constants['window_title'], False)
		self.isinitialized = True	
	
	
	def render_all(self):
		"""
		Draw the current game state on screen.
		Does nothing if isinitialized == False (pygame.init failed)
		"""
		
		if not self.isinitialized:
			return
		# draw all the tiles in the game map
		#libtcod.console_clear(self.engine.con)
		libtcod.console_blit(self.engine.con, 0, 0, self.constants['screen_width'], self.constants['screen_height'], 0, 0, 0)
		if self.engine.fov_recompute:
			for y in range(self.engine.game_map.height):
				for x in range(self.engine.game_map.width):
					visible = libtcod.map_is_in_fov(self.engine.fov_map, x, y)
					wall = self.engine.game_map.tiles[x][y].block_sight

					if visible:
						if wall:
							libtcod.console_set_char_background(self.engine.con, x, y, self.colors.get('light_wall'), libtcod.BKGND_SET)
						else:
							libtcod.console_set_char_background(self.engine.con, x, y, self.colors.get('light_ground'), libtcod.BKGND_SET)
						self.engine.game_map.tiles[x][y].explored = True
					elif self.engine.game_map.tiles[x][y].explored:
						if wall:
							libtcod.console_set_char_background(self.engine.con, x, y, self.colors.get('dark_wall'), libtcod.BKGND_SET)
						else:
							libtcod.console_set_char_background(self.engine.con, x, y, self.colors.get('dark_ground'), libtcod.BKGND_SET)			
			self.fov_recompute = False


		#draw all entities in the list
		entities_in_render_order = sorted(self.engine.entities, key=lambda x: x.render_order.value)
		for entity in entities_in_render_order:
			self.draw_entity(self.engine.con, entity, self.engine.fov_map, self.engine.game_map)

		libtcod.console_blit(self.engine.con, 0, 0, self.constants['screen_width'], self.constants['screen_height'], 0, 0, 0)
		
		#TODO: handle when there is no cursor
		#self.draw_cursor(self.engine.mouse, self.engine.cursor_radius, self.engine.game_state, self.engine.target_fov_map, self.engine.fov_map_no_walls, self.engine.screen_width, self.engine.screen_height)
		
		#clear info panel
		libtcod.console_set_default_background(self.engine.panel, libtcod.black)
		libtcod.console_clear(self.engine.panel)

		# Print the game messages, one line at a time
		y = 1
		for message in self.engine.message_log.messages:
			libtcod.console_set_default_foreground(self.engine.panel, message.color)
			libtcod.console_print_ex(self.engine.panel, self.engine.message_log.x, y, libtcod.BKGND_NONE, libtcod.LEFT, message.text)
			y += 1

		self.render_bar(self.engine.panel, 1, 1, self.constants['bar_width'], 'HP', self.engine.player.fighter.hp, self.engine.player.fighter.max_hp, libtcod.light_red, libtcod.darker_red)
		libtcod.console_print_ex(self.engine.panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT, 'Dungeon Level: {0}'.format(self.engine.game_map.dungeon_level))
		libtcod.console_blit(self.engine.panel, 0, 0, self.constants['screen_width'], self.constants['panel_height'], 0, 0, self.constants['panel_y'])

		if self.engine.game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
			if self.engine.game_state == GameStates.SHOW_INVENTORY:
				inventory_title = 'Press the key next to an item to use it, or Esc to cancel.'
			else:
				inventory_title = 'Press the key next to an item to drop it, or Esc to cancel.'

			inventory_menu(self.engine.con, inventory_title, self.engine.player.inventory, 50, self.constants['screen_width'], self.constants['screen_height'])

		elif self.engine.game_state == GameStates.LEVEL_UP:
			level_up_menu(self.engine.con, 'Level up! Choose a stat to raise:', self.engine.player, 40, self.constants['screen_width'], self.constants['screen_height'])

		elif self.engine.game_state == GameStates.CHARACTER_SCREEN:
			character_screen(self.engine.player, 30, self.constants['screen_width'], self.constants['screen_height'])

		elif len(self.engine.description_list) > 0:
			entity_description(self.engine.con, self.engine.description_list, self.engine.description_index, 50, self.constants['screen_width'], self.constants['screen_height'])
		libtcod.console_flush()
		self.clear_all(self.engine.con, self.engine.entities)
		
		

	def clear_all(self, con, entities):
		for entity in entities:
			self.clear_entity(con, entity)

	def render_bar(self, panel, x, y, total_width, name, value, maximum, bar_color, back_color):
		bar_width = int(float(value) / maximum * total_width)

		libtcod.console_set_default_background(panel, back_color)
		libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

		libtcod.console_set_default_background(panel, bar_color)
		if bar_width > 0:
			libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

		libtcod.console_set_default_foreground(panel, libtcod.white)
		libtcod.console_print_ex(panel, int(x + total_width / 2), y, libtcod.BKGND_NONE, libtcod.CENTER, '{0}: {1}/{2}'.format(name, value, maximum))

	def draw_entity(self, con, entity, fov_map, game_map):
		if libtcod.map_is_in_fov(fov_map, entity.x, entity.y) or (entity.stairs and game_map.tiles[entity.x][entity.y].explored) or (entity.item and game_map.tiles[entity.x][entity.y].explored):
			libtcod.console_set_default_foreground(con, entity.color)
			libtcod.console_put_char(con, entity.x, entity.y, entity.char, libtcod.BKGND_NONE)

	def clear_entity(self, con, entity):
		# erase the character that represents this object
		libtcod.console_put_char(con, entity.x, entity.y, ' ', libtcod.BKGND_NONE)

	def draw_cursor(self, mouse, cursor_radius, game_state, target_fov_map, fov_map_no_walls, screen_width, screen_height):
		
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

				
	
