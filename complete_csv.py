import csv
import daily_page_parse
from multiprocessing import Pool
import my_logger


logger = my_logger.get_logger(log_file_name='complete.log')


def get_csv_content(csv_path):
    content = list()
    with open(csv_path, 'r', newline='') as fr:
        reader = csv.DictReader(fr)
        for r in reader:
            content.append(r)
    return content


def get_miss_list(content):
    result_miss_list = list()
    for i in content:
        if i['count'] == '':
            result_miss_list.append(i['date'])
    return result_miss_list


def complete_csv(csv_path, content, key, value, complement):
    for k, v in complement.items():
        for i in content:
            if i[key] == k:
                i[value] = v
                break
    with open(csv_path, 'w', newline='') as fw:
        fieldnames = [key, value]
        csv_write = csv.DictWriter(fw, fieldnames=fieldnames)
        csv_write.writeheader()
        csv_write.writerows(content)


if __name__ == '__main__':
    name = input('csv name:')
    path = '%s/%s.%s' % ('Statistic', name, 'csv')
    content_dict = get_csv_content(path)
    miss_list = get_miss_list(content_dict)
    logger.info('miss list len: %d' % len(miss_list))
    pool = Pool()
    result_list = list()
    print('The size of miss list is: %d' % len(miss_list))
    handle = input('How many miss you want handle?(<%d)' % len(miss_list))
    handle_num = int(handle)
    for m in miss_list[0:handle_num]:
        logger.info('miss list item: %s' % m)
        res = pool.apply_async(daily_page_parse.get_daily_reponum, args=(m,))
        result_list.append([m, res])
    pool.close()
    pool.join()

    complement_dict = dict()
    for pair in result_list:
        num = pair[1].get()
        if num and num != '':
            complement_dict[pair[0]] = num
    logger.info('complement list len: %d' % len(complement_dict))

    complete_csv(path, content_dict, 'date', 'count', complement_dict)



