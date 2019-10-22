# Abilities will work similar to items, an ability class will be made and attached to the role for each ability. When you use an ability it will call the abilities.use function which will pass things off to the abilities ability_function
import tcod as libtcod
from game_messages import Message
from ability_functions import tackle


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
            if self.targeting and not (kwargs.get('target_x') or kwargs.get('target_y')):
                results.append({'targeting': self})
            else:
                kwargs = {**self.function_kwargs, **kwargs}
                ability_use_results = self.ability_function(self.owner, **kwargs)

                results.extend(ability_use_results)

        return results

