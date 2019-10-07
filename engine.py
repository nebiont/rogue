import tcod as libtcod
from input_handlers import handle_keys
from entity import Entity, get_blocking_entities_at_location
from render_functions import clear_all, render_all, RenderOrder
from map_objects.game_map import GameMap
from fov_functions import initialize_fov, recompute_fov
from game_states import GameStates
from components.fighter import Fighter
from components.inventory import Inventory
from death_functions import kill_monster, kill_player
from game_messages import MessageLog, Message

def main():
	#define main variables
	screen_width = 80
	screen_height = 50
	bar_width = 20
	panel_height = 7
	panel_y = screen_height - panel_height
	message_x = bar_width + 2
	message_width = screen_width - bar_width - 2
	message_height = panel_height - 1
	map_width = 80
	map_height = 43
	room_max_size = 10
	room_min_size = 6
	max_rooms = 30
	fov_algorithm = libtcod.FOV_PERMISSIVE_2
	fov_light_walls = True
	fov_radius = 10
	max_monsters_per_room = 3
	max_items_per_room = 2
	
	colors = {
		'dark_wall': libtcod.Color(0, 0, 100),
		'dark_ground': libtcod.Color(50, 50, 150),
		'light_wall': libtcod.Color(130, 110, 50),
		'light_ground': libtcod.Color(200, 180, 50)
	}
	
	# Define entities
	fighter_component = Fighter(hp=30, defense=2, power=5)
	inevntory_component = Inventory(26)
	player = Entity(0, 0, 1, libtcod.white, 'Player', blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component, inventory=inevntory_component)
	entities = [player]

	# Load font and create root console (what you see)
	libtcod.console_set_custom_font('Nice_curses_12x12.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
	libtcod.console_init_root(screen_width, screen_height, "Brett's Dungeon", False)

	# Create game area and info area, this will be drawn to our root console so that we can see them
	con = libtcod.console_new(screen_width, screen_height)
	panel = libtcod.console_new(screen_width, panel_height)

	# Create our map
	game_map = GameMap(map_width, map_height)
	game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities, max_monsters_per_room, max_items_per_room)

	# Intialize FOV map.
	fov_recompute = True # Recompute FOV after the player moves
	fov_map = initialize_fov(game_map)

	# Create message log
	message_log = MessageLog(message_x, message_width, message_height)

	# Capture keyboard and mouse input
	key = libtcod.Key()
	mouse = libtcod.Mouse()

	# Initialize the game state
	game_state = GameStates.PLAYERS_TURN
	previous_game_state = game_state

	#Our main loop
	while not libtcod.console_is_window_closed():
		# Check for input
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)
		action = handle_keys(key, game_state)

		# Recompute FOV
		if fov_recompute:
			recompute_fov(fov_map, player.x, player.y, fov_radius, fov_light_walls, fov_algorithm)
		
		# Draw our scene
		render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log, screen_width, screen_height, bar_width, panel_height, panel_y, colors, game_state)
		fov_recompute = False
		libtcod.console_flush()

		# Clear our 'drawing consoles' so we dont leave a trail on the main console screen
		clear_all(con, entities)

		# Store input results
		move = action.get('move')
		pickup = action.get('pickup')
		show_inventory = action.get('show_inventory')
		drop_inventory = action.get('drop_inventory')
		inventory_index = action.get('inventory_index')
		exit = action.get('exit')
		fullscreen = action.get('fullscreen')

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
			game_state = GameStates.SHOW_INVENTORY

		if drop_inventory:
			if game_state != GameStates.DROP_INVENTORY:
				previous_game_state = game_state
			game_state = GameStates.DROP_INVENTORY

		if inventory_index is not None and previous_game_state != GameStates.PLAYER_DEAD and inventory_index < len(player.inventory.items):
			item = player.inventory.items[inventory_index]
			if game_state == GameStates.SHOW_INVENTORY:
				player_turn_results.extend(player.inventory.use(item))

			elif game_state == GameStates.DROP_INVENTORY:
				player_turn_results.extend(player.inventory.drop_item(item))
						
		if exit:
			if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
				game_state = previous_game_state
			else:
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

			if message:
				message_log.add_message(message)

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

			if item_dropped:
				entities.append(item_dropped)
				game_state = GameStates.ENEMY_TURN


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

