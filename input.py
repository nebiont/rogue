import tcod as libtcod
import tcod.event
import engine
from game_states import GameStates
from event_manager import *

class Input(object):
	"""
	Handles keyboard input.
	"""

	def __init__(self, evmanager, engine):
		"""
		evmanager (EventManager): Allows posting messages to the event queue.
		model (GameEngine): a strong reference to the game Model.
		"""
		self.evmanager = evmanager
		evmanager.RegisterListener(self)
		self.engine = engine

	def notify(self, event):
		"""
		Receive events posted to the message queue. 
		"""

		if isinstance(event, TickEvent):
			# Called for each game tick. We check our keyboard presses here.
			for event in libtcod.event.get():
				# handle window manager closing our window
				if event.type == "QUIT":
					self.evmanager.Post(QuitEvent())
				# handle key down events
				if event.type == "KEYDOWN":
					if event.sym == libtcod.event.K_ESCAPE:
						self.evmanager.Post(StateChangeEvent(None))
					else:
						currentstate = self.engine.state.peek()
						if currentstate == GameStates.MAIN_MENU:
							self.main_menu(event)
						if currentstate == GameStates.PLAYERS_TURN:
							self.players_turn(event)
						if currentstate == GameStates.SHOW_INVENTORY or currentstate == GameStates.DROP_INVENTORY:
							self.inventory(event)
						if currentstate == GameStates.TARGETING:
							self.targeting()
						if currentstate == GameStates.LEVEL_UP:
							self.level_up()
				if event.type == "MOUSEMOTION":
					self.evmanager.Post(Mouse_motion_event(event))

	def main_menu(self, event):
		"""
		Handles menu key events.
		"""
		key_char = chr(event.key.scancode)
		# escape pops the menu
		if event.key == libtcod.KEY_ESCAPE:
			self.evmanager.Post(StateChangeEvent(None))

		if key_char == 'a':
			self.evmanager.Post(InputEvent({'new_game': True}))
		elif key_char == 'b':
			self.evmanager.Post(InputEvent({'load_game': True}))
		elif key_char == 'c':
			self.evmanager.Post(StateChangeEvent(None))

	def players_turn(self, event):
		"""
		Handles menu key events.
		"""
		key_char = chr(event.key.scancode)
		# escape pops the menu
		if event.key == libtcod.KEY_ESCAPE:
			self.evmanager.Post(StateChangeEvent(None))
	
		# Movement keys
		if event.key == libtcod.KEY_UP or event.key == libtcod.KEY_KP8:
			self.evmanager.Post(InputEvent({'move': (0, -1)}))
		elif event.key == libtcod.KEY_DOWN or event.key == libtcod.KEY_KP2:
			self.evmanager.Post(InputEvent({'move': (0, 1)}))
		elif event.key == libtcod.KEY_LEFT or event.key == libtcod.KEY_KP4:
			self.evmanager.Post(InputEvent({'move': (-1, 0)}))
		elif event.key == libtcod.KEY_RIGHT or event.key == libtcod.KEY_KP6:
			self.evmanager.Post(InputEvent({'move': (1, 0)}))
		elif event.key == libtcod.KEY_KP1:
			self.evmanager.Post(InputEvent({'move': (-1, 1)}))
		elif event.key == libtcod.KEY_KP3:
			self.evmanager.Post(InputEvent({'move': (1, 1)}))
		elif event.key == libtcod.KEY_KP7:
			self.evmanager.Post(InputEvent({'move': (-1, -1)}))
		elif event.key == libtcod.KEY_KP9:
			self.evmanager.Post(InputEvent({'move': (1, -1)}))
		elif event.key == libtcod.KEY_KP5:
			self.evmanager.Post(InputEvent({'move': 'wait'}))

		if key_char == 'g':
			self.evmanager.Post(InputEvent({'pickup': True}))
		
		elif key_char == 'i':
			self.evmanager.Post(InputEvent({'show_inventory': True}))

		elif key_char == 'd':
			self.evmanager.Post(InputEvent({'drop_inventory': True}))

		elif key_char == 'c':
			self.evmanager.Post(InputEvent({'show_character_screen': True}))

		elif key_char == '1':
			self.evmanager.Post(InputEvent({'ability_1': True}))

		elif event.key == libtcod.KEY_ENTER:
			self.evmanager.Post(InputEvent({'take_stairs': True}))
							

