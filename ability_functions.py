import tcod as libtcod
from game_messages import Message


def tackle(*args, **kwargs):
    caster = args[0]
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')
    caster.animator.move(target_x, target_y, 30)
    results = []
    results.append({'message': Message('I eat some poop', libtcod.green)})

    return results