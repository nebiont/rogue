import tcod as libtcod
from input_handlers import handle_keys, handle_mouse, handle_main_menu
from loader_functions.initialize_new_game import get_constants, get_game_variables
from loader_functions.data_loaders import load_game, save_game
from menus import main_menu, message_box
from entity import get_blocking_entities_at_location
from render_functions import clear_all, render_all
from fov_functions import initialize_fov, recompute_fov
from game_states import GameStates
from death_functions import kill_monster, kill_player
from game_messages import Message, MessageLog
from pygame import mixer
from random import randint
import definitions
import os



def main():
	#define main variables
	constants = get_constants()
	
	# Limit FPS to 100 so we dont kill CPUs
	libtcod.sys_set_fps(60)

	# Load font and create root console (what you see)
	libtcod.console_set_custom_font(os.path.join(definitions.ROOT_DIR,'Nice_curses_12x12.png'), libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
	libtcod.console_init_root(constants['screen_width'], constants['screen_height'], constants['window_title'], False)

	# Create game area and info area, this will be drawn to our root console so that we can see them
	con = libtcod.console_new(constants['screen_width'], constants['screen_height'])
	panel = libtcod.console_new(constants['screen_width'], constants['panel_height'])

	player = None
	entities = []
	game_map = None
	message_log: MessageLog  = None
	game_state = None

	show_main_menu = True
	show_load_error_message = False

	main_menu_background_image = libtcod.image_load(os.path.join(definitions.ROOT_DIR,'data','menu_background.png'))

	# Capture keyboard and mouse input
	key = libtcod.Key()
	mouse = libtcod.Mouse()


	mixer.init()
	mixer.music.load(os.path.join(definitions.ROOT_DIR, 'data', 'music', 'title.mp3'))
	#mixer.music.play(loops=-1)
	#Our main loop
	while not libtcod.console_is_window_closed():
		# Check for input
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
		
		
		
		if show_main_menu:
			# Start music

			main_menu(con, main_menu_background_image, constants['screen_width'], constants['screen_height'])

			if show_load_error_message:
				message_box(con, 'No save game to load', 50, constants['screen_width'], constants['screen_height'])

			libtcod.console_flush()

			
			action = handle_main_menu(key)

			new_game = action.get('new_game')
			load_saved_game = action.get('load_game')
			exit_game = action.get('exit')

			if show_load_error_message and (new_game or load_saved_game or exit_game):
				show_load_error_message = False
			elif new_game:
				player, entities, game_map, message_log, game_state = get_game_variables(constants)
				game_state = GameStates.PLAYERS_TURN

				show_main_menu = False
			
			elif load_saved_game:
				try:
					player, entities, game_map, message_log, game_state = load_game()
					show_main_menu = False
				except FileNotFoundError:
					show_load_error_message = True
			
			elif exit_game:
				break

		else:
			libtcod.console_clear(con)
			play_game(player, entities, game_map, message_log, game_state, con, panel, constants)

			show_main_menu = True

		

def play_game(player, entities, game_map, message_log, game_state, con, panel, constants):
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

		# Recompute FOV
		if fov_recompute:
			recompute_fov(fov_map, player.x, player.y, constants['fov_radius'], constants['fov_light_walls'], constants['fov_algorithm'])
			recompute_fov(fov_map_no_walls, player.x, player.y, constants['fov_radius'], light_walls=False, algorithm=constants['fov_algorithm'])
		
	
		# Show object descriptions
		if description_recompute == True:

			for entity in entities:
				if libtcod.map_is_in_fov(fov_map, entity.x, entity.y):
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

		# Clear our 'drawing consoles' so we dont leave a trail on the main console screen
		clear_all(con, entities)


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
			cursor_radius = targeting_item.item.function_kwargs.get('radius')
			if left_click:
				target_x, target_y = left_click
				
				item_use_results = player.inventory.use(targeting_item, entities=entities, fov_map=fov_map, target_fov_map=target_fov_map,target_x=target_x, target_y=target_y)
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

				message_log.add_message(targeting_item.item.targeting_message)

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

if __name__ == '__main__':
	main()

