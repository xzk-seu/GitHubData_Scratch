from datetime import date
from bs4 import BeautifulSoup
import get_response
import time
import json
import os
import csv
import my_logger
from multiprocessing import Pool, Manager

# 爬取每日项目的名称、owner、path


_SEARCH_URL = 'https://github.com/search'
logger = my_logger.get_logger(log_file_name='daily_page_parser.log')


def get_repo_info_single_page(search_condition, page):
    # 从单个搜索页面上获得该页面上项目的基本信息：项目名称、作者、path
    # 再返回一个当日数量用于验证之前的统计
    # return [name, owner, path, page]
    result_list = list()
    result_dict = dict(page=page)
    search_condition['p'] = page
    max_try = 0
    resp = None
    while max_try <= 5:
        max_try += 1
        try:
            resp = get_response.get_response(_SEARCH_URL, param=search_condition)
            break
        except Exception as e:
            if max_try < 5:
                logger.info("Try: %d  | Date: %s | Error : %s" % (max_try, search_condition['q'], str(e)))
            else:
                logger.error("Try: %d  | Date: %s | Error : %s" % (max_try, search_condition['q'], str(e)))
        time.sleep(max_try)
    if not resp:
        return None
    soup = BeautifulSoup(resp.text, 'lxml')
    repo_list = soup.find('ul', 'repo-list').contents
    daily_num = soup.find_all('h3')[1].string.strip('\n repository results').replace(',', '')
    daily_num = int(daily_num)
    result_dict['daily_num'] = daily_num
    print(daily_num)
    for i in range(1, len(repo_list), 2):
        repo_item = repo_list[i].find('h3').a
        repo_json = repo_item['data-hydro-click']
        repo_dict = json.loads(repo_json)
        repo_url = repo_dict['payload']['result']['url']
        repo_title = repo_item.string
        repo_titles = repo_title.split('/')
        repo_owner = repo_titles[0]
        repo_name = repo_titles[1]

        print(repo_name)
        repo_dict = dict(name=repo_name, owner=repo_owner, path=repo_url)

        # repo = [repo_name, repo_owner, repo_url, page]
        result_list.append(repo_dict)
        logger.info("Try: %d | Date: %s | get : %s" % (max_try, search_condition['q'], repo_titles))

    result_dict["repo"] = result_list
    return result_dict


def get_csv_content(csv_path):
    content = list()
    with open(csv_path, 'r', newline='') as fr:
        reader = csv.DictReader(fr)
        for r in reader:
            content.append(r)
    return content


def get_date_list(y):
    # 条件：0<count<1000
    # 根据条件获取一个日期list
    csv_path = os.path.join(os.getcwd(), 'Statistic', '%d.csv' % y)
    content = get_csv_content(csv_path)
    result_list = list()
    for i in content:
        if 0 < int(i['count']) < 1000:
            result_list.append(i['date'])
    return result_list


def test1():
    result_path = os.path.join(os.getcwd(), 'Result', 'test')
    search_condition = dict()
    search_condition['type'] = 'repository'
    search_condition['q'] = 'created:<' + '2008-01-01'
    d = get_repo_info_single_page(search_condition, 1)
    with open(result_path, 'w')as fw:
        json.dump(d, fw, indent=4)


def get_daily_repo(d_str, res_dict):
    search_condition = dict()
    res_list = list()
    search_condition['type'] = 'repository'
    search_condition['q'] = 'created:' + d_str
    page_one = get_repo_info_single_page(search_condition, 1)
    res_list.append(page_one)
    daily_num = page_one['daily_num']
    rest_page = daily_num//10
    for p in range(rest_page):
        repo = get_repo_info_single_page(search_condition, p+2)
        res_list.append(repo)
    res_dict[d_str] = res_list


def test():
    # 处理一年的结果
    date_list = get_date_list(2012)
    logger.info('there is %s days need crawling' % len(date_list))
    pool = Pool()
    m = Manager()
    res_d = m.dict()
    for d in date_list:
        pool.apply_async(get_daily_repo, args=(d, res_d))
    pool.close()
    pool.join()
    result_path = os.path.join(os.getcwd(), 'Result', 'test')
    with open(result_path, 'w')as fw:
        json.dump(res_d, fw, indent=4)


if __name__ == '__main__':
    test()

