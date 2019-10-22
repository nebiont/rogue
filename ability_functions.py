import tcod as libtcod
from game_messages import Message


def tackle(*args, **kwargs):
    caster = args[0]
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')
    entities = kwargs.get('entities')
    caster.animator.move(target_x, target_y, 30)
    results = []
    for entity in entities:
        if entity.x == target_x and entity.y == target_y and hasattr(entity, 'fighter'):
            results.append({'message': Message('{0} charges towards the {1}!'.format(caster.name, entity.name), libtcod.green)})
            return results
    else:    
        results.append({'message': Message('{0} charges forward!'.format(caster.name), libtcod.green)})

    return results