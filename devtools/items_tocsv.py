import csv
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import definitions
import yaml
import os
from time import sleep



yaml_stream = open(os.path.join(definitions.ROOT_DIR, 'data','objects','items.yaml'), 'r')
yaml_file = yaml.load(yaml_stream)
header_row = ['ID']
row = []

for i in yaml_file[0]:
    header_row.append(i)
with open('test.csv', mode='w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(header_row)
    for i in yaml_file:
        row.append(i)
        for x in yaml_file[i]:
            row.append(yaml_file[i][x])
        csv_writer.writerow(row)
        row = []
            

