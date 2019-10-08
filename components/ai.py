import tcod as libtcod
from random import randint
from game_messages import Message
from entity import Entity, get_blocking_entities_at_location


class BasicMonster:
    def take_turn(self, target, fov_map, game_map, entities):
        results = []
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):

            if monster.distance_to(target) >= 2:
                monster.move_astar(target, entities, game_map)

            elif target.fighter.hp > 0:
                attack_results = monster.fighter.attack(target)
                results.extend(attack_results)

        return results

class ConfusedMonster:
    def __init__(self, previous_ai, previous_color, number_of_turns=10):
        self.previous_ai = previous_ai
        self.number_of_turns = number_of_turns
        self.previous_color = previous_color

    def take_turn(self, target, fov_map, game_map, entities):
        results = []
        target_list = []
        percent = randint(0, 100)
        
        if self.number_of_turns > 0:

            # Generate target list out of the enemies near the confused monster
            for x in range(self.owner.x - 1, self.owner.x + 1):
                for y in range(self.owner.y -1, self.owner.y +1):
                        blocking_entity = get_blocking_entities_at_location(entities, x, y)
                        if not blocking_entity == None:
                            target_list.append(blocking_entity)
            
            if percent <= 40:
                if not target_list == None:
                    self.target = target_list[randint(0, len(target_list) - 1)]
                    
                    if target.fighter.hp > 0:
                        attack_results = self.owner.fighter.attack(self.target)
                        results.extend(attack_results)

                else:
                    random_x = self.owner.x + randint(0, 2) - 1
                    random_y = self.owner.y + randint(0, 2) - 1

                    if random_x != self.owner.x and random_y != self.owner.y:
                        self.owner.move_towards(random_x, random_y, game_map, entities)

                    self.number_of_turns -= 1
            
            else:
                random_x = self.owner.x + randint(0, 2) - 1
                random_y = self.owner.y + randint(0, 2) - 1

                if random_x != self.owner.x and random_y != self.owner.y:
                    self.owner.move_towards(random_x, random_y, game_map, entities)

                self.number_of_turns -= 1

        else:
            self.owner.ai = self.previous_ai
            self.owner.color = self.previous_color
            results.append({'message': Message('The {0} is no longer confused!'.format(self.owner.name),libtcod.red)})
        return results

class PolymorphedMonster:
    def __init__(self, previous_ai, previous_char, previous_color, number_of_turns=10):
        self.previous_ai = previous_ai
        self.previous_char = previous_char
        self.number_of_turns = number_of_turns
        self.previous_color = previous_color

    def take_turn(self, target, fov_map, game_map, entities):
        results = []

        if self.number_of_turns > 0:
            
            random_x = self.owner.x + randint(0, 2) - 1
            random_y = self.owner.y + randint(0, 2) - 1

            if random_x != self.owner.x and random_y != self.owner.y:
                self.owner.move_towards(random_x, random_y, game_map, entities)

            self.number_of_turns -= 1
        else:
            self.owner.ai = self.previous_ai
            self.owner.char = self.previous_char
            self.owner.color = self.previous_color
            results.append({'message': Message('The {0} is no longer polymorhped!'.format(self.owner.name),libtcod.red)})
        return results    