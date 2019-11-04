import tcod as libtcod
from components.animator import Animator
from input_handlers import handle_keys, handle_mouse, handle_main_menu, handle_role_select
from loader_functions.initialize_new_game import get_constants, get_game_variables, get_dummy_player
from loader_functions.data_loaders import load_game, save_game
from menus import main_menu, message_box, role_menu
from entity import get_blocking_entities_at_location
from fov_functions import initialize_fov, recompute_fov
from game_states import GameStates
from death_functions import kill_monster, kill_player
from game_messages import Message, MessageLog
from components.role import Warrior, Ranger, Rogue, Warlock, Paladin
from pygame import mixer
from random import randint
from event_manager import *
from input import MouseHandler
import definitions
import os
from time import sleep
#TODO: implement mouse controls, im already halfway their with the tackle animation
#TODO: Targeting should be a class (our list of instance variables for the engine class is getting pretty long, shoudl split some stuff out into its own class)
#TODO: Move the con variables (panel and con) to the render function, Main-menu and Role-Menu use them.


class GameEngine:

	def __init__(self, evmanager):
		"""
		evmanager (EventManager): Allows posting messages to the event queue.
		
		Attributes:
		running (bool): True while the engine is online. Changed via QuitEvent().
		"""
		
		self.evmanager = evmanager
		evmanager.RegisterListener(self)
		self.state = StateMachine()
		self.running = False

		#define main variables
		self.constants = get_constants()
		
		# Create game area and info area, this will be drawn to our root console so that we can see them
		self.con = libtcod.console_new(self.constants['screen_width'], self.constants['screen_height'])
		self.panel = libtcod.console_new(self.constants['screen_width'], self.constants['panel_height'])

		self.player = get_dummy_player(Warrior())
		self.entities = []
		self.game_map = None
		self.message_log: MessageLog  = None
		self.game_state = None

		self.show_main_menu = True
		self.show_game = False
		self.show_load_error_message = False

		#input related
		self.mouse = MouseHandler()
		self.action = {}

		self.main_menu_background_image = libtcod.image_load(os.path.join(definitions.ROOT_DIR,'data','menu_background.png'))

		self.fov_recompute = None
		self.fov_map = None
		self.target_fov_map = None
		self.fov_map_no_walls = None

		

		mixer.init()
		mixer.music.load(os.path.join(definitions.ROOT_DIR, 'data', 'music', 'title.mp3'))
		mixer.music.set_volume(0.05)
		#mixer.music.play(loops=-1)
		

	def state_control(self, state):
		switcher = {
			GameStates.MAIN_MENU: self.main_menu,
			GameStates.ROLE_MENU: self.role_menu,
			GameStates.PLAY_GAME: self.play_game,
			GameStates.PLAYERS_TURN: self.player_turn,
			GameStates.BLOCKING_ANIMATION: self.blocking_animation_update,
			GameStates.ENEMY_TURN: self.enemy_turn,
			GameStates.SHOW_INVENTORY: self.inventory,
			GameStates.DROP_INVENTORY: self.inventory,
			GameStates.TARGETING: self.targeting,
			GameStates.CHARACTER_SCREEN: self.player_turn,
			GameStates.LEVEL_UP: self.level_up
		}
		func = switcher.get(state)
		func()

	def notify(self, event):
		"""
		Called by an event in the message queue. 
		"""

		if isinstance(event, QuitEvent):
			self.running = False

		if isinstance(event, StateChangeEvent):
			# pop request
			if not event.state:
				# false if no more states are left
				if not self.state.pop():
					self.evmanager.Post(QuitEvent())
			else:
				# push a new state on the stack
				self.state.push(event.state)

		if isinstance(event, InputEvent):
			self.action = event.action

		if isinstance(event, Mouse_event):
			if event.mouse_event.type == "MOUSEMOTION":
				self.mouse.motion = event.mouse_event
			if event.mouse_event.type =="MOUSEBUTTONDOWN":
				self.mouse.button = event.mouse_event

	def run(self):
		"""
		Starts the game engine loop.

		This pumps a Tick event into the message queue for each loop.
		The loop ends when this object hears a QuitEvent in notify(). 
		"""
		self.running = True
		self.evmanager.Post(InitializeEvent())
		self.state.push(GameStates.MAIN_MENU)
		while self.running:
			# Detect blocking animations and change gamestate to blocking
			if Animator.blocking > 0 and not self.state.peek() == GameStates.BLOCKING_ANIMATION:
				self.state.push(GameStates.BLOCKING_ANIMATION)
			# Update any animators
			self.state_control(self.state.peek())
			for animator in Animator.animators:
				animator.update()
			# Clear the action so that we don't remember actions from previous game states / ticks
			self.action = {}
			newTick = TickEvent()
			self.evmanager.Post(newTick)
			


	def main_menu(self):
		#TODO: Separate a bunch of this stuff to the render_function
		# Check for input

		main_menu(self.con, self.main_menu_background_image, self.constants['screen_width'], self.constants['screen_height'])

		if self.show_load_error_message:
			message_box(self.con, 'No save game to load', 50, self.constants['screen_width'], self.constants['screen_height'])

		libtcod.console_flush()

		new_game = self.action.get('new_game')
		load_saved_game = self.action.get('load_game')
		exit_game = self.action.get('exit')

		if self.show_load_error_message and (new_game or load_saved_game or exit_game):
			self.show_load_error_message = False
		elif new_game:
			self.state.push(GameStates.ROLE_MENU)
		
		elif load_saved_game:
			try:
				self.player, self.entities, self.game_map, self.message_log, self.game_state = load_game()
				self.con.clear()
				self.state.push(GameStates.PLAY_GAME)
			except FileNotFoundError:
				self.show_load_error_message = True


	def role_menu(self):
		warrior = self.action.get('warrior')
		ranger = self.action.get('ranger')
		rogue = self.action.get('rogue')
		paladin = self.action.get('paladin')
		warlock = self.action.get('warlock')
		back = self.action.get('exit')
		accept = self.action.get('accept')
		libtcod.console_clear(0)
		role_menu(self.con,self.constants['screen_width'],self.constants['screen_height'], self.player.role)
		libtcod.console_flush()

		if warrior:
			self.player = get_dummy_player(Warrior())
			role_menu(self.con,self.constants['screen_width'],self.constants['screen_height'], self.player.role)
			libtcod.console_flush()
		if ranger:
			self.player = get_dummy_player(Ranger())
			role_menu(self.con,self.constants['screen_width'],self.constants['screen_height'], self.player.role)
			libtcod.console_flush()
		if rogue:
			self.player = get_dummy_player(Rogue())
			role_menu(self.con,self.constants['screen_width'],self.constants['screen_height'], self.player.role)
			libtcod.console_flush()
		if paladin:
			self.player = get_dummy_player(Paladin())
			role_menu(self.con,self.constants['screen_width'],self.constants['screen_height'], self.player.role)
			libtcod.console_flush()
		if warlock:
			self.player = get_dummy_player(Warlock())
			role_menu(self.con,self.constants['screen_width'],self.constants['screen_height'], self.player.role)
			libtcod.console_flush()
		if accept:
			self.player, self.entities, self.game_map, self.message_log, self.game_state = get_game_variables(self.constants, self.player)
			libtcod.console_clear(self.con)
			self.state.pop()
			self.state.push(GameStates.PLAY_GAME)
		if back:
			self.state.pop()
		
	def play_game(self):
		# Intialize FOV map.
		self.fov_recompute = True # Recompute FOV after the player moves
		self.fov_map = initialize_fov(self.game_map)
		self.target_fov_map = initialize_fov(self.game_map)
		self.fov_map_no_walls = initialize_fov(self.game_map)

		# Store the item that the player used to enter targeting mode (ie lightning scroll). This is so that we know what item we need to remove from inventory etc.
		self.targeting_item = None
		self.cursor_radius = 1

		# For showing object descriptions
		self.description_recompute = True
		self.description_list = []
		self.description_index = 0	
		self.prev_mouse_y = None
		self.prev_mouse_x = None

		self.player_turn_results = []

		self.state.pop()
		self.state.push(GameStates.PLAYERS_TURN)
		self.state_control(self.state.peek())

		

	def player_turn(self):

		# Recompute FOV
		if self.fov_recompute:
			recompute_fov(self.fov_map, self.player.x, self.player.y, self.constants['fov_radius'], self.constants['fov_light_walls'], self.constants['fov_algorithm'])
			recompute_fov(self.fov_map_no_walls, self.player.x, self.player.y, self.constants['fov_radius'], light_walls=False, algorithm=self.constants['fov_algorithm'])
			
		
	
		self.show_descriptions()

		# Store input results
		move = self.action.get('move')
		pickup = self.action.get('pickup')
		show_inventory = self.action.get('show_inventory')
		drop_inventory = self.action.get('drop_inventory')
		self.inventory_index = self.action.get('inventory_index')
		take_stairs = self.action.get('take_stairs')
		level_up = self.action.get('level_up')
		show_character_screen = self.action.get('show_character_screen')
		ability_1 = self.action.get('ability_1')
		exit = self.action.get('exit')
		fullscreen = self.action.get('fullscreen')
		

		# Player Actions
		# Move
		if move:
			if not move == 'wait':
				dx, dy = move
				destination_x = self.player.x + dx
				destination_y = self.player.y + dy

				# Check to see if the location we want to move to is blocked by a wall or inhabited by a creature
				if not self.game_map.is_blocked(destination_x, destination_y):
					target = get_blocking_entities_at_location(self.entities, destination_x, destination_y)

					# If blocked by a creature, attack
					if target:
						attack_results = self.player.fighter.attack(target)
						self.player_turn_results.extend(attack_results)
					# Otherwise, move.
					else:
						self.player.move(dx, dy)
						self.fov_recompute = True
					self.turn_swap()
			else:
				self.turn_swap()

		elif pickup:
			for entity in self.entities:
				if entity.item and entity.x == self.player.x and entity.y == self.player.y:
					pickup_results = self.player.inventory.add_item(entity)
					self.player_turn_results.extend(pickup_results)

					break
			else:
				self.message_log.add_message(Message('There is nothing here to pick up.', libtcod.yellow))
		#Ability complete checks:
		for ability in self.player.abilities:
			if not ability.animator == None:
				if ability.animator.complete:
					self.player_turn_results.extend(ability.use(complete=True))
					ability.animator = None


		if ability_1:
			self.player_turn_results.extend(self.player.abilities[0].use())


		if show_inventory:
			self.player.inventory.sort_items()
			self.state.push(GameStates.SHOW_INVENTORY)

		if drop_inventory:
			self.state.push(GameStates.DROP_INVENTORY)



		if take_stairs:
			for entity in self.entities:
				if entity.stairs and entity.x == self.player.x and entity.y == self.player.y: 
					self.entities = self.game_map.next_floor(self.player, self.message_log, self.constants)
					self.fov_map = initialize_fov(self.game_map)
					self.target_fov_map = initialize_fov(self.game_map)
					self.fov_map_no_walls = initialize_fov(self.game_map)
					self.fov_recompute = True
					self.con.clear()

					break
			else:
				self.message_log.add_message(Message('There are no stairs here.', libtcod.yellow))


		if show_character_screen:
			self.state.push(GameStates.CHARACTER_SCREEN)

	
						
		if exit:
			if self.state.peek() == GameStates.TARGETING:
				self.player_turn_results.append({'targeting_cancelled': True})
				self.cursor_radius = 1
			else:
				save_game(self.player, self.entities, self.game_map, self.message_log, self.game_state)
				return True


		if fullscreen:
			libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

		self.process_turn_results()


	def enemy_turn(self):
		for entity in self.entities:
			if entity.ai:
				enemy_turn_results = entity.ai.take_turn(self.player, self.fov_map, self.game_map, self.entities)

				# Capture enemy turn message queue, analyze and react accordingly.
				for enemy_turn_result in enemy_turn_results:
					message = enemy_turn_result.get('message')
					dead_entity = enemy_turn_result.get('dead')

					if message:
						self.message_log.add_message(message)

					if dead_entity:
						if dead_entity == self.player:
							message, game_state = kill_player(dead_entity)
							self.state.push(game_state)
						else:
							message = kill_monster(dead_entity)

						self.message_log.add_message(message)
			
		else:            

			self.turn_swap()
	
	def show_descriptions(self):
		#TODO: needs a rewrite and variable scoping
		# Show object descriptions
		if self.description_recompute == True:

			for entity in self.entities:

				if (self.prev_mouse_x != self.mouse.motion.tile.x) or (self.prev_mouse_y != self.mouse.motion.tile.y):
					self.description_list = []
					self.description_index = 0
				if entity.x == self.mouse.motion.tile.x and entity.y == self.mouse.motion.tile.y:
					self.description_list.append(entity)
					self.prev_mouse_x = self.mouse.motion.tile.x
					self.prev_mouse_y = self.mouse.motion.tile.y

			
		if len(self.description_list) > 0:
			self.description_recompute = False
			# We need to check to see if the mouse position changed and then clear our description list if it did, otherwise it will keep growing
			if (self.prev_mouse_x != self.mouse.motion.tile.x) or (self.prev_mouse_y != self.mouse.motion.tile.y):
				self.description_list = []
				self.description_index = 0
				self.description_recompute = True
			#TODO: should not be handling mouse button here, should happen in input
			if self.mouse.button.button == libtcod.event.BUTTON_LEFT:
				self.description_index += 1
			if self.description_index > (len(self.description_list) - 1):
				self.description_index = 0
	
	def process_turn_results(self):
		# Check player message queue and react accordingly
		for player_turn_result in self.player_turn_results:
			message = player_turn_result.get('message')
			dead_entity = player_turn_result.get('dead')
			item_added = player_turn_result.get('item_added')
			item_consumed = player_turn_result.get('consumed')
			item_dropped = player_turn_result.get('item_dropped')
			equip = player_turn_result.get('equip')
			targeting = player_turn_result.get('targeting')
			targeting_cancelled = player_turn_result.get('targeting_cancelled')
			ability_used = player_turn_result.get("ability_used")
			xp = player_turn_result.get('xp')

			if message:
				self.message_log.add_message(message)

			if targeting_cancelled:
				self.state.pop()

				self.message_log.add_message(Message('Targeting cancelled'))

			if dead_entity:
				if dead_entity == self.player:
					message, game_state = kill_player(dead_entity)
					self.state.push(game_state)

				else:
					message = kill_monster(dead_entity)

				self.message_log.add_message(message)

			if item_added:
				self.entities.remove(item_added)

				self.turn_swap()

			if item_consumed:
				self.turn_swap()
			
			if targeting:
				self.state.push(GameStates.TARGETING)

				self.targeting_item = targeting
				if hasattr(self.targeting_item, 'item'):
					self.message_log.add_message(self.targeting_item.item.targeting_message)
				else:
					self.message_log.add_message(self.targeting_item.targeting_message)

			if ability_used:
					self.turn_swap()

			if item_dropped:
				self.entities.append(item_dropped)
				self.turn_swap()

			if equip:
				equip_results = self.player.equipment.toggle_equip(equip)

				for equip_result in equip_results:
					equipped = equip_result.get('equipped')
					dequipped = equip_result.get('dequipped')

					if equipped:
						self.message_log.add_message(Message('You equipped the {0}'.format(equipped.name)))

					if dequipped:
						self.message_log.add_message(Message('You removed the {0}'.format(dequipped.name)))

				self.turn_swap()

			if xp:
				leveled_up = self.player.level.add_xp(xp)
				self.message_log.add_message(Message('You gain {0} experience points.'.format(xp)))

				if leveled_up:
					self.message_log.add_message(Message('Your battle skills grow stronger! You reached level {0}'.format(
													self.player.level.current_level) + '!', libtcod.yellow))
					if (self.player.level.current_level % 2) == 0:
						self.state.push(GameStates.LEVEL_UP)
					else:
						hp_increase = randint(self.player.fighter.hitdie[0], self.player.fighter.hitdie[1]) + int((self.player.fighter.con - 10) / 2)
						self.player.fighter.base_max_hp += hp_increase
						self.player.fighter.hp += hp_increase
						self.message_log.add_message(Message('Your HP has increased by {0}'.format(hp_increase) + '!', libtcod.yellow)) 
		#Clear results queue for next turn
		self.player_turn_results = []

	def targeting(self):
		left_click = self.action.get('left_click')
		if hasattr(self.targeting_item, 'item'):
			self.cursor_radius = self.targeting_item.item.function_kwargs.get('radius')
		else:
			self.cursor_radius = self.targeting_item.function_kwargs.get('radius')
		if left_click:
			self.target_x, self.target_y = self.mouse.button.tile
			if hasattr(self.targeting_item, 'item'):
				self.item_use_results = self.player.inventory.use(self.targeting_item, entities=self.entities, fov_map=self.fov_map, game_map=self.game_map, target_fov_map=self.target_fov_map,target_x=self.target_x, target_y=self.target_y)
			else:
				self.item_use_results = self.targeting_item.use(entities=self.entities, fov_map=self.fov_map, game_map=self.game_map, target_fov_map=self.target_fov_map,target_x=self.target_x, target_y=self.target_y)
			left_click = None
			self.player_turn_results.extend(self.item_use_results)
			self.cursor_radius = 1
			# Cancel targeting if the ability or item was used
			for item_use_result in self.item_use_results:
				if item_use_result.get('ability_used') or item_use_result.get('consumed'):
					self.state.pop()
			self.process_turn_results()
	
	def inventory(self):
		#TODO: needs to pass an invetory index to use_or_drop_item when state is drop or show inventory
		self.inventory_index = self.action.get('inventory_index')
		if not self.inventory_index == None:
			try:
				if self.state.peek() == GameStates.SHOW_INVENTORY:
					self.player_turn_results.extend(self.use_or_drop_item(self.inventory_index, 'use'))
					self.state.pop()
				else:
					self.player_turn_results.extend(self.use_or_drop_item(self.inventory_index, 'drop'))
					self.state.pop()
				return
			except :
				return


	def blocking_animation_update(self):
		if Animator.blocking == 0:
			# If the blocking animation is done, remove the blocking gamestate and then process turn results. Will need
			# to reimplement if I want blocking animations on the enemies turn.
			self.state.pop()
			self.process_turn_results()

	
	def use_or_drop_item(self, inventory_index, action: str):
		try:
			if self.inventory_index is not None and self.inventory_index < len(self.player.inventory.items):
				item = self.player.inventory.items[self.inventory_index]
				if action == 'use':
					return self.player.inventory.use(item, entities=self.entities, fov_map=self.fov_map)

				if action == 'drop':
					return self.player.inventory.drop_item(item)
		except:
			return None


	def turn_swap(self):
		if self.state.peek() == GameStates.ENEMY_TURN:
			self.state.pop()
			self.state.push(GameStates.PLAYERS_TURN)
		elif self.state.peek() == GameStates.PLAYERS_TURN:
			self.state.pop()
			self.state.push(GameStates.ENEMY_TURN)

	def level_up(self):
		level_up = self.action.get('level_up')

		if level_up:
			if level_up == 'hp':
				self.player.fighter.con += 1
				self.message_log.add_message(Message('Your Constitution has increased by 1!', libtcod.yellow))
			elif level_up == 'str':
				self.player.fighter.base_power += 1
				self.message_log.add_message(Message('Your Strength has increased by 1!', libtcod.yellow))
			elif level_up == 'def':
				self.player.fighter.base_defense += 1
				self.message_log.add_message(Message('Your Defense has increased by 1!', libtcod.yellow))

			hp_increase = randint(self.player.fighter.hitdie[0], self.player.fighter.hitdie[1]) + int((self.player.fighter.con - 10) / 2)
			self.player.fighter.base_max_hp += hp_increase
			self.player.fighter.hp += hp_increase
			self.message_log.add_message(Message('Your HP has increased by {0}'.format(hp_increase) + '!', libtcod.yellow))
			self.state.pop()


class StateMachine(object):
	"""
	Manages a stack based state machine.
	peek(), pop() and push() perform as traditionally expected.
	peeking and popping an empty stack returns None.
	"""
	
	def __init__ (self):
		self.statestack = []
	
	def peek(self):
		"""
		Returns the current state without altering the stack.
		Returns None if the stack is empty.
		"""
		try:
			return self.statestack[-1]
		except IndexError:
			# empty stack
			return None
	
	def pop(self):
		"""
		Returns the current state and remove it from the stack.
		Returns None if the stack is empty.
		"""
		try:
			self.statestack.pop()
			return len(self.statestack) > 0
		except IndexError:
			# empty stack
			return None
	
	def push(self, state):
		"""
		Push a new state onto the stack.
		Returns the pushed value.
		"""
		self.statestack.append(state)
		return state
