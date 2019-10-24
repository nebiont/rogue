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
import definitions
import os
from time import sleep
#TODO: implement mouse controls, im already halfway their with the tackle animation
#TODO: make main and renderer their own classes, should allow easier passing of info also set me up to do screen shake animations


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

		self.main_menu_background_image = libtcod.image_load(os.path.join(definitions.ROOT_DIR,'data','menu_background.png'))

		# Capture keyboard and mouse input
		self.key = libtcod.Key()
		self.mouse = libtcod.Mouse()

		self.fov_recompute = None
		self.fov_map = None
		self.target_fov_map = None
		self.fov_map_no_walls = None

		mixer.init()

	def state_control(self, state):
		switcher = {
			GameStates.MAIN_MENU: self.main_menu,
			GameStates.PLAY_GAME: self.play_game
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
					self.evManager.Post(QuitEvent())
			else:
				# push a new state on the stack
				self.state.push(event.state)

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
			self.state_control(self.state.peek())
			newTick = TickEvent()
			self.evmanager.Post(newTick)
			


	def main_menu(self):
		mixer.music.load(os.path.join(definitions.ROOT_DIR, 'data', 'music', 'title.mp3'))
		#mixer.music.play(loops=-1)
		# Check for input
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, self.key, self.mouse)
		
		if self.show_main_menu:

			main_menu(self.con, self.main_menu_background_image, self.constants['screen_width'], self.constants['screen_height'])

			if self.show_load_error_message:
				message_box(self.con, 'No save game to load', 50, self.constants['screen_width'], self.constants['screen_height'])

			libtcod.console_flush()

			
			action = handle_main_menu(self.key)

			new_game = action.get('new_game')
			load_saved_game = action.get('load_game')
			exit_game = action.get('exit')

			if self.show_load_error_message and (new_game or load_saved_game or exit_game):
				self.show_load_error_message = False
			elif new_game:
				self.show_main_menu = False
				self.show_game = True
			
			elif load_saved_game:
				try:
					self.player, self.entities, self.game_map, self.message_log, self.game_state = load_game()
					self.show_main_menu = False
				except FileNotFoundError:
					self.show_load_error_message = True

		elif self.show_game == True:
			action = handle_role_select(self.key)
			warrior = action.get('warrior')
			ranger = action.get('ranger')
			rogue = action.get('rogue')
			paladin = action.get('paladin')
			warlock = action.get('warlock')
			back = action.get('exit')
			accept = action.get('accept')
			libtcod.console_clear(0)
			role_menu(self.con,self.constants['screen_width'],self.constants['screen_height'], self.player.role)
			libtcod.console_flush()

			if warrior:
				player = get_dummy_player(Warrior())
				role_menu(self.con,self.constants['screen_width'],self.constants['screen_height'], player.role)
				libtcod.console_flush()
			if ranger:
				player = get_dummy_player(Ranger())
				role_menu(self.con,self.constants['screen_width'],self.constants['screen_height'], player.role)
				libtcod.console_flush()
			if rogue:
				player = get_dummy_player(Rogue())
				role_menu(self.con,self.constants['screen_width'],self.constants['screen_height'], player.role)
				libtcod.console_flush()
			if paladin:
				player = get_dummy_player(Paladin())
				role_menu(self.con,self.constants['screen_width'],self.constants['screen_height'], player.role)
				libtcod.console_flush()
			if warlock:
				player = get_dummy_player(Warlock())
				role_menu(self.con,self.constants['screen_width'],self.constants['screen_height'], player.role)
				libtcod.console_flush()
			if accept:
				self.player, self.entities, self.game_map, self.message_log, self.game_state = get_game_variables(self.constants, self.player)
				show_game = False
			if back:
				show_main_menu = True

		else:
			libtcod.console_clear(self.con)
			game_state = GameStates.PLAYERS_TURN
			self.play_game(self.player, self.entities, self.game_map, self.message_log, self.game_state, self.con, self.panel, self.constants)

			show_main_menu = True
		
	def play_game(self, player, entities, game_map, message_log, game_state, con, panel, constants):
		# Intialize FOV map.
		fov_recompute = True # Recompute FOV after the player moves
		fov_map = initialize_fov(game_map)
		target_fov_map = initialize_fov(game_map)
		fov_map_no_walls = initialize_fov(game_map)


		# Capture keyboard and mouse input
		key = libtcod.Key()
		mouse = libtcod.Mouse()
		game_state = GameStates.PLAYERS_TURN
		previous_game_state = game_state

		# Store the item that the player used to enter targeting mode (ie lightning scroll). This is so that we know what item we need to remove from inventory etc.
		targeting_item = None
		cursor_radius = 1

		# For showing object descriptions
		description_recompute = True
		description_list = []
		description_index = 0	
		prev_mouse_y = None
		prev_mouse_x = None

		# Start music
		mixer.init()
		mixer.music.load(os.path.join(definitions.ROOT_DIR, 'data', 'music', 'bgm2.mp3'))
		#mixer.music.play(loops=-1)

		#Our main loop
		while not libtcod.console_is_window_closed():
			# Check for input
			libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
			for animator in Animator.animators:
				animator.update()
			if Animator.blocking > 0:
				if not game_state == GameStates.BLOCKING_ANIMATION:
					previous_game_state = game_state
				game_state = GameStates.BLOCKING_ANIMATION

			if Animator.blocking == 0 and game_state == GameStates.BLOCKING_ANIMATION:
					game_state = previous_game_state

			# Recompute FOV
			if fov_recompute:
				recompute_fov(fov_map, player.x, player.y, constants['fov_radius'], constants['fov_light_walls'], constants['fov_algorithm'])
				recompute_fov(fov_map_no_walls, player.x, player.y, constants['fov_radius'], light_walls=False, algorithm=constants['fov_algorithm'])
			
		
			# Show object descriptions
			if description_recompute == True:

				for entity in entities:

					if (prev_mouse_x != mouse.cx) or (prev_mouse_y != mouse.cy):
						description_list = []
						description_index = 0
					if entity.x == mouse.cx and entity.y == mouse.cy:
						description_list.append(entity)
						prev_mouse_x = mouse.cx
						prev_mouse_y = mouse.cy

				
			if len(description_list) > 0:
				description_recompute = False
				# We need to check to see if the mouse position changed and then clear our description list if it did, otherwise it will keep growing
				if (prev_mouse_x != mouse.cx) or (prev_mouse_y != mouse.cy):
					description_list = []
					description_index = 0
					description_recompute = True
				if mouse.lbutton_pressed:
					description_index += 1
				if description_index > (len(description_list) - 1):
					description_index = 0


			
			# Draw our scene
			render_all(con, panel, mouse, entities, player, game_map, fov_map, fov_recompute, message_log, constants['screen_width'], constants['screen_height'], constants['bar_width'], constants['panel_height'], constants['panel_y'], constants['colors'], game_state, description_list, description_index, cursor_radius, target_fov_map, fov_map_no_walls)
			fov_recompute = False
			libtcod.console_flush()



			# Store input results
			action = handle_keys(key, game_state)
			mouse_action = handle_mouse(mouse)
			key = libtcod.Key()
			mouse = libtcod.Mouse()
			move = action.get('move')
			pickup = action.get('pickup')
			show_inventory = action.get('show_inventory')
			drop_inventory = action.get('drop_inventory')
			inventory_index = action.get('inventory_index')
			take_stairs = action.get('take_stairs')
			level_up = action.get('level_up')
			show_character_screen = action.get('show_character_screen')
			ability_1 = action.get('ability_1')
			exit = action.get('exit')
			fullscreen = action.get('fullscreen')
			left_click = mouse_action.get('left_click')
			right_click = mouse_action.get('right_click')
			


			#Instatiate our message queue for the players turn
			player_turn_results = []

			# Player Actions
			# Move
			if move and game_state == GameStates.PLAYERS_TURN:
				if not move == 'wait':
					dx, dy = move
					destination_x = player.x + dx
					destination_y = player.y + dy

					# Check to see if the location we want to move to is blocked by a wall or inhabited by a creature
					if not game_map.is_blocked(destination_x, destination_y):
						target = get_blocking_entities_at_location(entities, destination_x, destination_y)

						# If blocked by a creature, attack
						if target:
							attack_results = player.fighter.attack(target)
							player_turn_results.extend(attack_results)
						# Otherwise, move.
						else:
							player.move(dx, dy)
							fov_recompute = True
						game_state = GameStates.ENEMY_TURN
				else:
					game_state = GameStates.ENEMY_TURN

			elif pickup and game_state == GameStates.PLAYERS_TURN:
				for entity in entities:
					if entity.item and entity.x == player.x and entity.y == player.y:
						pickup_results = player.inventory.add_item(entity)
						player_turn_results.extend(pickup_results)

						break
				else:
					message_log.add_message(Message('There is nothing here to pick up.', libtcod.yellow))
			#Ability complete checks:
			for ability in player.abilities:
				if player.animator.caller == ability and player.animator.complete:
					player_turn_results.extend(ability.use(complete=True))
					player.animator.caller = None
					player.animator.complete = None

			if ability_1:
				player_turn_results.extend(player.abilities[0].use())


			if show_inventory:
				if game_state != GameStates.SHOW_INVENTORY:
					previous_game_state = game_state
				player.inventory.sort_items()
				game_state = GameStates.SHOW_INVENTORY

			if drop_inventory:
				if game_state != GameStates.DROP_INVENTORY:
					previous_game_state = game_state
				game_state = GameStates.DROP_INVENTORY

			#Use or drop item in inventory
			if inventory_index is not None and previous_game_state != GameStates.PLAYER_DEAD and inventory_index < len(player.inventory.items):
				item = player.inventory.items[inventory_index]
				if game_state == GameStates.SHOW_INVENTORY:
					player_turn_results.extend(player.inventory.use(item, entities=entities, fov_map=fov_map))

				elif game_state == GameStates.DROP_INVENTORY:
					player_turn_results.extend(player.inventory.drop_item(item))

			if take_stairs and game_state == GameStates.PLAYERS_TURN:
				for entity in entities:
					if entity.stairs and entity.x == player.x and entity.y == player.y: 
						entities = game_map.next_floor(player, message_log, constants)
						fov_map = initialize_fov(game_map)
						target_fov_map = initialize_fov(game_map)
						fov_map_no_walls = initialize_fov(game_map)
						fov_recompute = True
						libtcod.console_clear(con)

						break
				else:
					message_log.add_message(Message('There are no stairs here.', libtcod.yellow))

			if level_up:
				if level_up == 'hp':
					player.fighter.con += 1
					message_log.add_message(Message('Your Constitution has increased by 1!', libtcod.yellow))
				elif level_up == 'str':
					player.fighter.base_power += 1
					message_log.add_message(Message('Your Strength has increased by 1!', libtcod.yellow))
				elif level_up == 'def':
					player.fighter.base_defense += 1
					message_log.add_message(Message('Your Defense has increased by 1!', libtcod.yellow))

				hp_increase = randint(player.fighter.hitdie[0], player.fighter.hitdie[1]) + int((player.fighter.con - 10) / 2)
				player.fighter.base_max_hp += hp_increase
				player.fighter.hp += hp_increase
				message_log.add_message(Message('Your HP has increased by {0}'.format(hp_increase) + '!', libtcod.yellow))
				game_state = previous_game_state

			if show_character_screen:
				if not game_state == GameStates.CHARACTER_SCREEN:
					previous_game_state = game_state
				game_state = GameStates.CHARACTER_SCREEN

			if game_state == GameStates.TARGETING:

				if hasattr(targeting_item, 'item'):
					cursor_radius = targeting_item.item.function_kwargs.get('radius')
				else:
					cursor_radius = targeting_item.function_kwargs.get('radius')
				if left_click:
					target_x, target_y = left_click
					if hasattr(targeting_item, 'item'):
						item_use_results = player.inventory.use(targeting_item, entities=entities, fov_map=fov_map, game_map=game_map, target_fov_map=target_fov_map,target_x=target_x, target_y=target_y)
					else:
						item_use_results = targeting_item.use(entities=entities, fov_map=fov_map, game_map=game_map, target_fov_map=target_fov_map,target_x=target_x, target_y=target_y)
					player_turn_results.extend(item_use_results)
					cursor_radius = 1
				
				elif right_click:
					player_turn_results.append({'targeting_cancelled': True})
					cursor_radius = 1		
							
			if exit:
				if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY, GameStates.CHARACTER_SCREEN):
					game_state = previous_game_state
				elif game_state == GameStates.TARGETING:
					player_turn_results.append({'targeting_cancelled': True})
					cursor_radius = 1
				else:
					save_game(player, entities, game_map, message_log, game_state)
					return True


			if fullscreen:
				libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

			# Check player message queue and react accordingly
			for player_turn_result in player_turn_results:
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
					message_log.add_message(message)

				if targeting_cancelled:
					game_state = previous_game_state

					message_log.add_message(Message('Targeting cancelled'))

				if dead_entity:
					if dead_entity == player:
						message, game_state = kill_player(dead_entity)
					else:
						message = kill_monster(dead_entity)

					message_log.add_message(message)

				if item_added:
					entities.remove(item_added)

					game_state = GameStates.ENEMY_TURN

				if item_consumed:
					game_state = GameStates.ENEMY_TURN
				
				if targeting:
					previous_game_state = GameStates.PLAYERS_TURN
					game_state = GameStates.TARGETING

					targeting_item = targeting
					if hasattr(targeting_item, 'item'):
						message_log.add_message(targeting_item.item.targeting_message)
					else:
						message_log.add_message(targeting_item.targeting_message)

				if ability_used:
					if Animator.blocking == 0:
						game_state = GameStates.ENEMY_TURN

				if item_dropped:
					entities.append(item_dropped)
					game_state = GameStates.ENEMY_TURN

				if equip:
					equip_results = player.equipment.toggle_equip(equip)

					for equip_result in equip_results:
						equipped = equip_result.get('equipped')
						dequipped = equip_result.get('dequipped')

						if equipped:
							message_log.add_message(Message('You equipped the {0}'.format(equipped.name)))

						if dequipped:
							message_log.add_message(Message('You removed the {0}'.format(dequipped.name)))

					game_state = GameStates.ENEMY_TURN

				if xp:
					leveled_up = player.level.add_xp(xp)
					message_log.add_message(Message('You gain {0} experience points.'.format(xp)))

					if leveled_up:
						message_log.add_message(Message('Your battle skills grow stronger! You reached level {0}'.format(
														player.level.current_level) + '!', libtcod.yellow))
						if (player.level.current_level % 2) == 0:
							previous_game_state = game_state
							game_state = GameStates.LEVEL_UP
						else:
							hp_increase = randint(player.fighter.hitdie[0], player.fighter.hitdie[1]) + int((player.fighter.con - 10) / 2)
							player.fighter.base_max_hp += hp_increase
							player.fighter.hp += hp_increase
							message_log.add_message(Message('Your HP has increased by {0}'.format(hp_increase) + '!', libtcod.yellow))


			# Enemy Turn
			if game_state == GameStates.ENEMY_TURN:
				for entity in entities:
					if entity.ai:
						enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities)

						# Capture enemy turn message queue, analyze and react accordingly.
						for enemy_turn_result in enemy_turn_results:
							message = enemy_turn_result.get('message')
							dead_entity = enemy_turn_result.get('dead')

							if message:
								message_log.add_message(message)

							if dead_entity:
								if dead_entity == player:
									message, game_state = kill_player(dead_entity)
								else:
									message = kill_monster(dead_entity)

								message_log.add_message(message)

								if game_state == GameStates.PLAYER_DEAD:
									break
						if game_state == GameStates.PLAYER_DEAD:
							break

					
				else:            

					game_state = GameStates.PLAYERS_TURN

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
