import csv
import definitions
import yaml
import os
from time import sleep



yaml_stream = open(os.path.join('test.yaml'), 'rw')
yaml_object = yaml.load(yaml_stream)


with open('test.csv', mode='r', newline='') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            line_count += 1
        else:
            yaml_object[row[0]]['name'] = row[1]


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
            

