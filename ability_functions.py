import tcod as libtcod
from game_messages import Message


def tackle(*args, **kwargs):
    caster = args[0]
    caller = args[1]
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')
    entities = kwargs.get('entities')
    complete = kwargs.get('complete')
    results = []
    
    if complete:
        results.append({'ability_used': True})
        return results
    for entity in entities:
        if entity.x == target_x and entity.y == target_y and not entity.fighter == None:
            results.append({'message': Message('{0} charges towards the {1}!'.format(caster.name, entity.name), libtcod.green)})
            caster.animator.move_to(target_x, target_y, 30, caller, blocking=True)
            return results
    else:    
        results.append({'ability_used': True, 'message': Message('{0} charges forward!'.format(caster.name), libtcod.green)})
        caster.animator.move_to(target_x, target_y, 30, caller, blocking=True)

    return results