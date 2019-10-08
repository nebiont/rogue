import tcod as libtcod

from game_messages import Message
from components.ai import ConfusedMonster, PolymorphedMonster

def heal(*args, **kwargs):
    entity = args[0]
    amount = kwargs.get('amount')

    results = []

    if entity.fighter.hp == entity.fighter.max_hp:
        results.append({'consumed': False, 'message': Message('You are already at full health', libtcod.yellow)})

    else:
        entity.fighter.heal(amount)
        results.append({'consumed': True, 'message': Message('You were healed for {0} HP.'.format(amount), libtcod.green)})

    return results

def cast_lightning(*args, **kwargs):
    caster = args[0]
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    damage = kwargs.get('damage')
    maximum_range = kwargs.get('maximum_range')

    results = []

    target = None
    closest_distance = maximum_range + 1

    for entity in entities:
        if entity.fighter and entity != caster and libtcod.map_is_in_fov(fov_map, entity.x, entity.y):
            distance = caster.distance_to(entity)

            if distance < closest_distance:
                target = entity
                closest_distance = distance
    
    if target:
        results.append({'consumed': True, 'target': target, 'message': Message('A lightning bolt strikes {0} with a loud thunder! The damage is {1}'.format(target.name, damage))})
        results.extend(target.fighter.take_damage(damage))
    else:
        results.append({'consumed': False, 'target': None, 'message': Message('No enemy is close enough to strike.', libtcod.red)})

    return results

def cast_fireball(*args, **kwargs):
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    damage = kwargs.get('damage')
    radius = kwargs.get('radius')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    results = []

    if not libtcod.map_is_in_fov(fov_map, target_x, target_y):
        results.append({'consumed': False, 'message': Message('You cannot target a tile outside of your view.', libtcod.yellow)})
        return results

    results.append({'consumed': True, 'message': Message('The fireball explodes, burning everything within {0} tiles!'.format(radius), libtcod.orange)})

    for entity in entities:
        if entity.distance(target_x, target_y) <= radius and entity.fighter:
            results.append({'message': Message('The {0} gets burned for {1} hit points'.format(entity.name, damage), libtcod.orange)})
            results.extend(entity.fighter.take_damage(damage))

    return results

def cast_confuse(*args, **kwargs):
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')
    number_of_turns = kwargs.get('number_of_turns')

    results = []

    if not libtcod.map_is_in_fov(fov_map, target_x, target_y):
        results.append({'consumed': False, 'message': Message('You cannot target a tile outside of your view.', libtcod.yellow)})
        return results

    for entity in entities:
        if entity.x == target_x and entity.y == target_y and entity.ai:
            confused_ai = ConfusedMonster(entity.ai, number_of_turns=number_of_turns)

            confused_ai.owner = entity
            entity.ai = confused_ai
            entity.color = libtcod.dark_purple

            results.append({'consumed': True, 'message': Message('The eyes of the {0} look vacant and they begin to stumble around.'.format(entity.name), libtcod.light_green)})

            break
    else:
            results.append({'consumed': False, 'message': Message('There is no targetable enemy at that location.', libtcod.yellow)})

    return results

def cast_polymorph(*args, **kwargs):
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')
    number_of_turns = kwargs.get('number_of_turns')
    polymorph_char = kwargs.get('polymorph_char')
    polymorph_animal = kwargs.get('polymorph_animal')

    results = []

    if not libtcod.map_is_in_fov(fov_map, target_x, target_y):
        results.append({'consumed': False, 'message': Message('You cannot target a tile outside of your view.', libtcod.yellow)})
        return results

    for entity in entities:
        if entity.x == target_x and entity.y == target_y and entity.ai:
            polymorph_ai = PolymorphedMonster(entity.ai, entity.char, number_of_turns=number_of_turns)

            polymorph_ai.owner = entity
            entity.ai = polymorph_ai
            entity.char = polymorph_char

            results.append({'consumed': True, 'message': Message('The {0} dissapears in a puff of smoke, as the smoke clears a {1} has taken its place.'.format(entity.name, polymorph_animal), libtcod.light_green)})

            break
    else:
            results.append({'consumed': False, 'message': Message('There is no targetable enemy at that location.', libtcod.yellow)})

    return results