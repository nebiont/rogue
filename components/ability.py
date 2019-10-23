# Abilities will work similar to items, an ability class will be made and attached to the role for each ability. When you use an ability it will call the abilities.use function which will pass things off to the abilities ability_function
#TODO: make some targeting types (functions) that can be used by abilities to see if something hits, can also use this when drawing the targeting UI. Line-single target, line all targets on line, cone, AOE etc.
import tcod as libtcod
from game_messages import Message
from ability_functions import tackle
from fov_functions import initialize_fov_enemies_block, recompute_fov
from definitions import Definitions


class Ability:

    def __init__(self, name, description=None, ability_function=None, targeting=False, targeting_message=None, **kwargs):
        self.name = name
        self.description = description
        self.ability_function = ability_function
        self.targeting = targeting
        self.targeting_message = targeting_message
        self.function_kwargs = kwargs

    def use(self, **kwargs):
        results = []

        if self.ability_function is None:
                results.append({'message': Message('The {0} cannot be used'.format(self.name), libtcod.yellow)})
        else:
            if kwargs.get('complete'):
                ability_use_results = self.ability_function(self.owner, self, **kwargs)

                results.extend(ability_use_results)
                return results
            
            if self.targeting and not (kwargs.get('target_x') or kwargs.get('target_y')):
                results.append({'targeting': self})
            else:
                kwargs = {**self.function_kwargs, **kwargs}
                ability_use_results = self.ability_function(self.owner, self, **kwargs)

                results.extend(ability_use_results)

        return results
    #TODO: finish line_target, targetting system in the renderfunction, make tackle apply stun and do damage (125% weapon damage)
    # option for diagonals
    #horizontal and vert: if tar_x = cast_x OR tar_y = cast_y)
    #diag: if (tar_x - cast_x) = (tar_y - cast_y) AND (tar_x - cast_x) <= maximum_range
    def line_target(self, caster, entities_block=True, **kwargs):
        entities = kwargs.get('entities')
        fov_map = kwargs.get('fov_map')
        game_map = kwargs.get('game_map')
        maximum_range = kwargs.get('maximum_range')
        target_x = kwargs.get('target_x')
        target_y = kwargs.get('target_y')

        results = []
        
        if not entities_block:
            recompute_fov(fov_map, caster.x, caster.y, Definitions.fov_radius, light_walls=False, algorithm=Definitions.fov_algorithm)
            if not fov_map.fov[target_x, target_y].all():
                results.append({'success': False, 'message': Message('You cannot target a tile outside of your view.', libtcod.yellow)})
                return results

            if caster.distance(target_x, target_y) <= maximum_range:
                results.append({'success': False, 'message': Message('You cannot target a tile outside of range', libtcod.yellow)})
                return results
            results.append({'success': True})
            return results

        if entities_block:
            fov_map = initialize_fov_enemies_block(game_map, entities, caster, target_x, target_y)
            recompute_fov(fov_map, caster.x, caster.y, Definitions.fov_radius, light_walls=False, algorithm=Definitions.fov_algorithm)
            check = fov_map.fov[target_x, target_y].all()
            check2 = fov_map.fov[target_x, target_y]
            if not fov_map.fov[target_x, target_y].all():
                results.append({'success': False, 'message': Message('Your target is blocked.', libtcod.yellow)})
                return results
            results.append({'success': True})
            return results    

    #incomplete, allows selecting of anything in FOV and within range, but doesnt draw a path to the target
    def path_target(self, caster, entities_block=True, **kwargs):
        entities = kwargs.get('entities')
        fov_map = kwargs.get('fov_map')
        game_map = kwargs.get('game_map')
        maximum_range = kwargs.get('maximum_range')
        target_x = kwargs.get('target_x')
        target_y = kwargs.get('target_y')

        results = []
        
        if not entities_block:
            recompute_fov(fov_map, caster.x, caster.y, Definitions.fov_radius, light_walls=False, algorithm=Definitions.fov_algorithm)
            if not fov_map.fov[target_x, target_y].all():
                results.append({'success': False, 'message': Message('You cannot target a tile outside of your view.', libtcod.yellow)})
                return results

            if caster.distance(target_x, target_y) < maximum_range:
                results.append({'success': False, 'message': Message('You cannot target a tile outside of range', libtcod.yellow)})
                return results
            results.append({'success': True})
            return results

        if entities_block:
            fov_map = initialize_fov_enemies_block(game_map, entities, caster, target_x, target_y)
            recompute_fov(fov_map, caster.x, caster.y, Definitions.fov_radius, light_walls=False, algorithm=Definitions.fov_algorithm)
            check = fov_map.fov[target_x, target_y].all()
            check2 = fov_map.fov[target_x, target_y]
            if not fov_map.fov[target_x, target_y].all():
                results.append({'success': False, 'message': Message('Your target is blocked.', libtcod.yellow)})
                return results
            results.append({'success': True})
            return results

