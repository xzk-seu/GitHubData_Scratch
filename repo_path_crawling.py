from datetime import date
from bs4 import BeautifulSoup
import get_response
import time
import json
import os
import csv
import my_logger
from multiprocessing import Pool, Manager
from collections import OrderedDict

# 爬取每日项目的名称、owner、path


_SEARCH_URL = 'https://github.com/search'
logger = my_logger.get_logger(log_file_name='daily_page_parser.log')


def get_repo_info_single_page(d_str, page, lock):
    # 原子任务
    # 从单个搜索页面上获得该页面上项目的基本信息：项目名称、作者、path
    # 再返回一个当日数量用于验证之前的统计
    # return [name, owner, path, page]
    # 只返回当日数量，其他信息直接写入文件中
    search_condition = dict()
    search_condition['type'] = 'repository'
    search_condition['q'] = 'created:' + d_str
    search_condition['p'] = page
    result_list = list()
    result_dict = dict(date=d_str, page=page)
    max_try = 0
    resp = None
    while max_try <= 5:
        max_try += 1
        try:
            resp = get_response.get_response(_SEARCH_URL, param=search_condition)
            break
        except Exception as e:
            if max_try < 5:
                logger.info("Try: %d | Error : %s" % (max_try, str(e)))
            else:
                logger.error("Try: %d | Error : %s" % (max_try, str(e)))
        time.sleep(max_try)
    if not resp:
        return None
    soup = BeautifulSoup(resp.text, 'lxml')
    repo_list = soup.find('ul', 'repo-list').contents
    daily_num = soup.find_all('h3')[1].string.strip('\n repository results').replace(',', '')
    daily_num = int(daily_num)
    result_dict['daily_num'] = daily_num
    for i in range(1, len(repo_list), 2):
        repo_item = repo_list[i].find('h3').a
        repo_json = repo_item['data-hydro-click']
        repo_dict = json.loads(repo_json)
        repo_url = repo_dict['payload']['result']['url']
        repo_title = repo_item.string
        repo_titles = repo_title.split('/')
        repo_owner = repo_titles[0]
        repo_name = repo_titles[1]
        repo_dict = dict(name=repo_name, owner=repo_owner, path=repo_url)
        # repo = [repo_name, repo_owner, repo_url, page]
        result_list.append(repo_dict)
    logger.info("Try: %d | Date: %s | get page: %s" % (max_try, search_condition['q'], page))
    result_dict["repo"] = result_list

    y = str(d_str).split('-')[0]
    temp_path = os.path.join(os.getcwd(), 'Result', '%s temp.json' % y)
    lock.acquire()
    try:
        with open(temp_path, 'a') as fa:
            fa.write(json.dumps(result_dict)+'\n')
        logger.info('Date: %s, page: %d' % (d_str, page))
    except Exception:
        pass
    finally:
        lock.release()

    return daily_num
    # result_dict["repo"] = result_list
    # return result_dict


def get_csv_content(csv_path):
    content = list()
    with open(csv_path, 'r', newline='') as fr:
        reader = csv.DictReader(fr)
        for r in reader:
            content.append(r)
    return content


def get_date_list(y):
    # 条件1：year.csv中0<count<1000
    # 条件2：year.json中不存在
    # 根据条件获取一个日期list
    csv_path = os.path.join(os.getcwd(), 'Statistic', '%d.csv' % y)
    json_path = os.path.join(os.getcwd(), 'Result', '%d.json' % y)
    content = get_csv_content(csv_path)
    csv_list = list()
    for i in content:
        if 0 < int(i['count']) < 1000:
            csv_list.append(i['date'])
    j = dict()
    with open(json_path, 'r') as fr:
        j = json.load(fr)
    result_list = [i for i in csv_list if i not in j.keys()]
    return result_list


# def test1():
#     result_path = os.path.join(os.getcwd(), 'Result', 'test')
#     search_condition = dict()
#     search_condition['type'] = 'repository'
#     search_condition['q'] = 'created:<' + '2008-01-01'
#     d = get_repo_info_single_page(search_condition, 1)
#     with open(result_path, 'w')as fw:
#         json.dump(d, fw, indent=4)


def get_daily_repo(d_str, lock, pool):
    # 访问第一页，追加到文件中，获取项目数，计算页数，将剩余页的任务放到进程池中
    # res_list = list()
    # page_one = get_repo_info_single_page(search_condition, 1, lock)
    # res_list.append(page_one)
    # daily_num = page_one['daily_num']
    daily_num = get_repo_info_single_page(d_str, 1, lock)
    rest_page = daily_num//10
    for p in range(rest_page):
        # logger.info('rest page is %d/%d' % (p+1, rest_page))
        pool.apply_async(get_repo_info_single_page, args=(d_str,   p+2, lock))
        # repo = get_repo_info_single_page(search_condition, p+2)
        # res_list.append(repo)
    # res_dict[d_str] = res_list

    # # 将当天的数据追加到一个临时文件中，获取整年的数据后再合并
    # y = str(d_str).split('-')[0]
    # temp_path = os.path.join(os.getcwd(), 'Result', '%s temp.json' % y)
    # lock.acquire()
    # try:
    #     with open(temp_path, 'a') as fa:
    #         temp = dict()
    #         temp[d_str] = res_list
    #         fa.write(json.dumps(temp)+'\n')
    #     logger.info('get %s all repo' % d_str)
    # except Exception:
    #     pass
    # finally:
    #     lock.release()


def get_year_repo(y):
    # temp_path = os.path.join(os.getcwd(), 'Result', '%d temp.json' % y)
    # with open(temp_path, 'w') as fw:
    #     fw.truncate()
    # 处理一年的结果
    date_list = get_date_list(y)
    logger.info('there is %s days need crawling' % len(date_list))
    pool = Pool()
    m = Manager()
    lock = m.Lock()
    for d in date_list:
        get_daily_repo(d, lock, pool)
    #     pool.apply_async(get_daily_repo, args=(d, lock))
    pool.close()
    pool.join()

    # merge_temp(y)

    # # 将新爬取的与原有的合并
    # result_path = os.path.join(os.getcwd(), 'Result', '%d.json' % y)
    # with open(result_path, 'r')as fr:
    #     exsiting = json.load(fr)
    #
    # with open(temp_path, 'r') as fr:
    #     for line in fr:
    #         j = json.loads(line)
    #
    # res_d = dict(res_d)
    # res_d.update(exsiting)
    # with open(result_path, 'w')as fw:
    #     res_d = OrderedDict(sorted(res_d.items(), key=lambda x: x[0]))
    #     #  OrderedDict(sorted(d.items(), key=lambda t: t[0]))
    #     res_d = dict(res_d)
    #     json.dump(res_d, fw)


def check_missing_page(d_str):
    # 检查缺失页面，一旦缺失整天重爬
    print('check_missing_page(%s)' % d_str)


def merge_temp(y):
    # temp中一行为每天每页的数据
    # 将temp中的数据与现有的合并，然后清空temp
    result_path = os.path.join(os.getcwd(), 'Result', '%d.json' % y)
    temp_path = os.path.join(os.getcwd(), 'Result', '%d temp.json' % y)

    # 以日期为键，以一个list为值的dict
    # list的每个元素为每页项目
    new_dict = dict()
    with open(temp_path, 'r') as fr:
        for line in fr:
            j = json.loads(line)
            d = j.pop('date')
            new_list = new_dict.setdefault(d, [])
            new_list.append(j)
            new_dict[d] = new_list
    for v_list in new_dict.values():
        pass

    with open(result_path, 'r')as fr:
        exsiting = json.load(fr)

    with open(temp_path, 'r+') as fr:
        for line in fr:
            j = json.loads(line)
            exsiting.update(j)
        fr.seek(0)
        fr.truncate()

    with open(result_path, 'w')as fw:
        res_d = OrderedDict(sorted(exsiting.items(), key=lambda x: x[0]))
        #  OrderedDict(sorted(d.items(), key=lambda t: t[0]))
        res_d = dict(res_d)
        json.dump(res_d, fw)


if __name__ == '__main__':

    year = 2008
    # merge_temp(year)
    get_year_repo(year)
    # for year in range(2008, 2012+1):
    #     t = get_date_list(year)
    #     print(len(t), t)
    #     get_year_repo(year)

