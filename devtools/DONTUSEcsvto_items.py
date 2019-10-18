import csv
import yaml
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import definitions




yaml_stream = open(os.path.join(definitions.ROOT_DIR, 'data', 'objects','items.yaml'), 'w', newline="")
yaml_store = {}

with open('test.csv', mode='r') as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=',')
	line_count = 0
	first_row = []
	for row in csv_reader:
		x=0
		if line_count == 0:
			first_row = row
			line_count += 1

		else:
			x = 1
			temp = {}
			for i in row:
				parsed = (int(row[0]), row[1], row[2], row[3], row[4], eval(row[5]),
							row[6], eval(row[7]), eval(row[8]))
				if i == row[len(row) - 1]:
					break
				temp[first_row[x]] = parsed[x]
				x += 1
				print(yaml_store)
			yaml_store[row[0]] = temp
yaml.dump(yaml_store, yaml_stream)


