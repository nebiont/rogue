import tcod as libtcod

def initialize_fov(game_map):
    fov_map = libtcod.map.Map(game_map.width, game_map.height, order='F')

    for y in range(game_map.height):
        for x in range(game_map.width):
            fov_map.transparent[x,y] = not game_map.tiles[x][y].block_sight
            fov_map.walkable[x,y] = not game_map.tiles[x][y].blocked

    return fov_map

def initialize_fov_enemies_block(game_map, entities, caster, target_x, target_y):
    fov_map = libtcod.map.Map(game_map.width, game_map.height, order='F')

    for y in range(game_map.height):
        for x in range(game_map.width):
            fov_map.transparent[x,y] = not game_map.tiles[x][y].block_sight
            fov_map.walkable[x,y] = not game_map.tiles[x][y].blocked

    for entity in entities:
        if entity.blocks and entity != caster and (entity.x != target_x and entity.y != target_y):
            # Set the tile as a wall so it must be navigated around
            fov_map.transparent[entity.x, entity.y] = False
            fov_map.walkable[entity.x, entity.y] = False

    return fov_map

def recompute_fov(fov_map, x, y, radius, light_walls=True, algorithm=0):
    fov_map.compute_fov(x, y, radius, light_walls, algorithm)
