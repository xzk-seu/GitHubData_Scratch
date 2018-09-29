import os
import csv

RESULT = 0
STATISTIC = 1


type_list = ['Result', 'Statistic']
for t in type_list:
    if not os.path.exists(t):
        os.makedirs(t)


def write_csv(csv_name, result_type=RESULT, header=None, body_list=None):
    path = '%s/%s' % (type_list[result_type], csv_name)
    if not os.path.exists(path):
        with open(path, 'w', newline='') as fw:
            csv_writer = csv.writer(fw)
            csv_writer.writerow(header)
    with open(path, 'a', newline='') as fw:
        csv_writer = csv.writer(fw)
        csv_writer.writerows(body_list)

