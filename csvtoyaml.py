import csv
import definitions
import yaml
import os
from time import sleep



yaml_stream = open(os.path.join('test.yaml'), 'r', newline="")
yaml_object = yaml.load(yaml_stream)
yaml_store = {}


with open('test.csv', mode='r') as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=',')
	line_count = 0
	first_row = []
	for row in csv_reader:
		x=0
		if line_count == 0:
			line_count += 1
			first_row = row

		else:
			x = 1
			for i in row:
				yaml_store = {row[0]: {first_row[x]: row[x]}}
				x += 1
				print(yaml_store)
				# yaml_stream[row[0]] = {}
				# yaml_store[row[0]][first_row[x]] = row[x]
				


# for i in yaml_file[0]:
#     header_row.append(i)
# with open('test.csv', mode='w', newline='') as csv_file:
#     csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
#     csv_writer.writerow(header_row)
#     for i in yaml_file:
#         row.append(i)
#         for x in yaml_file[i]:
#             row.append(yaml_file[i][x])
#         csv_writer.writerow(row)
#         row = []
			

