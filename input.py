import tcod as libtcod
import tcod.event
import engine
from game_states import GameStates
from event_manager import *

class InputHandler(object):
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
				if event.type == "KEYDOWN" or event.type == "TEXTINPUT" or event.type == "MOUSEBUTTONDOWN":
					if event.type =="KEYDOWN":
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
						# if currentstate == GameStates.TARGETING:
						# 	self.targeting()
						if currentstate == GameStates.LEVEL_UP:
							self.level_up(event)
						if currentstate == GameStates.ROLE_MENU:
							self.role_menu(event)
				if event.type == "MOUSEMOTION":
					self.evmanager.Post(Mouse_motion_event(event))

	def main_menu(self, event):
		"""
		Handles menu key events.
		"""
		key_char = None
		if event.type == "TEXTINPUT":
			key_char = event.text
		if event.type == "KEYDOWN":
			if event.sym == libtcod.event.K_ESCAPE:
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
		if event.type == "TEXTINPUT":
			key_char = event.text
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

		elif event.type == "KEYDOWN":
			if event.sym == libtcod.event.K_ESCAPE:
				self.evmanager.Post(StateChangeEvent(None))
		
			# Movement keys
			if event.sym == libtcod.event.K_UP or event.sym == libtcod.event.K_KP_8:
				self.evmanager.Post(InputEvent({'move': (0, -1)}))
			elif event.sym == libtcod.event.K_DOWN or event.sym == libtcod.event.K_KP_2:
				self.evmanager.Post(InputEvent({'move': (0, 1)}))
			elif event.sym == libtcod.event.K_LEFT or event.sym == libtcod.event.K_KP_4:
				self.evmanager.Post(InputEvent({'move': (-1, 0)}))
			elif event.sym == libtcod.event.K_RIGHT or event.sym == libtcod.event.K_KP_6:
				self.evmanager.Post(InputEvent({'move': (1, 0)}))
			elif event.sym == libtcod.event.K_KP_1:
				self.evmanager.Post(InputEvent({'move': (-1, 1)}))
			elif event.sym == libtcod.event.K_KP_3:
				self.evmanager.Post(InputEvent({'move': (1, 1)}))
			elif event.sym == libtcod.event.K_KP_7:
				self.evmanager.Post(InputEvent({'move': (-1, -1)}))
			elif event.sym == libtcod.event.K_KP_9:
				self.evmanager.Post(InputEvent({'move': (1, -1)}))
			elif event.sym == libtcod.event.K_KP_5:
				self.evmanager.Post(InputEvent({'move': 'wait'}))

			elif event.sym == libtcod.event.K_KP_ENTER:
				self.evmanager.Post(InputEvent({'take_stairs': True}))

		elif event.type == "MOUSEBUTTONDOWN":
			if event.button == libtcod.event.BUTTON_LEFT:
				self.evmanager.Post(InputEvent({'left-click': event.tile}))
			elif event.button == libtcod.event.BUTTON_RIGHT:
				self.evmanager.Post(InputEvent({'right-click': event.tile}))
							
	def inventory(self, event):
		"""
		Handles menu key events.
		"""
		if event.type == "TEXTINPUT":
			index = ord(event.text) - ord('a')
		# escape pops the menu
		elif event.type == "KEYDOWN":
			if event.sym == libtcod.event.K_ESCAPE:
				self.evmanager.Post(StateChangeEvent(None))

		if index >= 0:
			self.evmanager.Post(InputEvent({'inventory_index': index}))

	def level_up(self, event):
		"""
		Handles menu key events.
		"""
		if event.type == "TEXTINPUT":
			key_char = event.text
		# escape pops the menu
		elif event.type == "KEYDOWN":
			if event.sym == libtcod.event.K_ESCAPE:
				self.evmanager.Post(StateChangeEvent(None))

		if key_char == 'a':
			self.evmanager.Post({'level_up': 'hp'})
		elif key_char =='b':
			self.evmanager.Post({'level_up': 'str'})
		elif key_char =='c':
			self.evmanager.Post({'level_up': 'def'})	

	def role_menu(self, event):
		"""
		Handles menu key events.
		"""
		if event.type == "TEXTINPUT":
			key_char = event.text
		# escape pops the menu
		elif event.type == "KEYDOWN":
			if event.sym == libtcod.event.K_ESCAPE:
				self.evmanager.Post(StateChangeEvent(None))
				self.evmanager.Post(InputEvent({'back': True}))
			if event.sym == libtcod.event.K_KP_ENTER:
				self.evmanager.Post(InputEvent({'accept': True}))

		if key_char == 'a':
			self.evmanager.Post({'warrior': True})
		elif key_char =='b':
			self.evmanager.Post({'ranger': True})
		elif key_char =='c':
			self.evmanager.Post({'rogue': True})
		elif key_char =='d':
			self.evmanager.Post({'paladin': True})
		elif key_char =='e':
			self.evmanager.Post({'warlock': True})
	