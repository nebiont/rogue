import yaml

item_stream = open('.\\data\\objects\\items.yaml', 'r')
item_list = yaml.load(item_stream)
for x in item_list.values():
    print(x.get('name'))
    print(x['item_component'].get('use_function'))
    print(x['item_component']['kwargs'])