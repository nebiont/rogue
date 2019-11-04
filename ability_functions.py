import tcod as libtcod
from game_messages import Message
import components.animator as animator

## if there is an an entity at targ_x targ_y then move final position 1 x,y towards caster
def tackle(*args, **kwargs):
    caster = args[0]
    caller = args[1]
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')
    entities = kwargs.get('entities')
    complete = kwargs.get('complete')
    results = []
    
    #If animation is complete, mark the ability as used so the casters turn ends.
    if complete:
        results.append({'ability_used': True})
        return results
    
    #Check if we are targetting an enemy or not:
    results.extend(caller.line_target(caster, entities_block=True, **kwargs))
    if results[0].get('success'):
        for entity in entities:
            if entity.x == target_x and entity.y == target_y and not entity.fighter == None:
                results.append({'ability_used': True, 'message': Message('{0} charges towards the {1}!'.format(caster.name, entity.name), libtcod.green)})
                animation = animator.Move_To(caster, target_x, target_y, 30, caller, blocking=True)
                return results
        else:    
            results.append({'ability_used': True, 'message': Message('{0} charges forward!'.format(caster.name), libtcod.green)})
            animation = animator.Move_To(caster, target_x, target_y, 30, caller, blocking=True)
            return results

    return results 

