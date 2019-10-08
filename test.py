import yaml
import tcod as libtcod
from random import randint

test = libtcod.Color(255, 255, 0)
print(test) 

libtcod.white

# item_stream = open('.\\data\\objects\\items.yaml', 'r')
# item_list = yaml.load(item_stream)
# loot_table = []


# print(item_list[0]['item_component']['kwargs'])
# for i in item_list:
#     loot_chance = item_list[i].get('loot_chance')
#     for r in range(loot_chance):
#         loot_table_item = [i, loot_chance]
#         loot_table.append(loot_table_item)
# print(loot_table)
# print(len(loot_table))
# print(item_list[randint(0,2)])
# for r in item_list:
#     loot_table[r] = item_list[r].get('loot_chance')

#     print(loot_table)
    #print(item_list[x].get('loot_chance'))
    # print(x.get('name'))
    # print(x['item_component'].get('use_function'))
    # print(x['item_component']['kwargs'])
    
