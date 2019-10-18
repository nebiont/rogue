import csv
import yaml
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import definitions
from collections import OrderedDict




yaml_stream = open(os.path.join(definitions.ROOT_DIR, 'data', 'objects','test.yaml'), 'w', newline="")
yaml_store = []

with open('test.csv', mode='r') as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=',')
	line_count = 0
	first_row = []
	for row in csv_reader:
		
		if line_count == 0:
			first_row = row
			line_count += 1
		else:
			x = 0
			temp = []
			yaml_store.append({row[0]: None})
			#yaml_store.append(row[0])
			for i in row:
				parsed = (int(row[0]), row[1], row[2], row[3], row[4],
							eval(row[5]), row[6], int(row[7]), int(row[8]),
							int(row[9]), int(row[10]))
				if i == row[len(row) - 1]:
					break

				temp.append({str(first_row[x+1]): parsed[x+1]})
				x += 1
				print(yaml_store)
			yaml_store[int(row[0])][str(row[0])] = temp
			#yaml_store[int(row[0])] = temp
yaml.dump(yaml_store, yaml_stream)


