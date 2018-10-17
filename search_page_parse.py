from datetime import date
from bs4 import BeautifulSoup
import get_response
import time
import json
import os
import csv
import my_logger


# 用于解析通过搜索得到的页面


_SEARCH_URL = 'https://github.com/search'
logger = my_logger.get_logger(log_file_name='daily_page_parser.log')


def get_repo_num(search_condition):
    # 根据一定的查询条件获得符合该查询条件的项目数量
    num = None
    max_try = 0
    while max_try <= 5:
        max_try += 1
        try:
            resp = get_response.get_response(_SEARCH_URL, param=search_condition)
            soup = BeautifulSoup(resp.text, 'lxml')
            result_str = soup.find_all('h3')[1].string.strip('\n repository results').replace(',', '')
            num = int(result_str)
            logger.info("Try: %d | Date: %s | get : %s" % (max_try, search_condition['q'], result_str))
            break
        except ValueError:
            # "We couldn't find any repositories matching 'created:xxxx-xx-xx'"
            logger.error("Try: %d | Date: %s | Error : %s" % (max_try, search_condition['q'], result_str))
            return 0
        except Exception as e:
            time.sleep(max_try)
            logger.error("Try: %d | Date: %s | Error : %s" % (max_try, search_condition['q'], str(e)))
    return num


def get_daily_reponum(created_at):
    # 获得每日创建项目的数量
    t = created_at.split('-')
    y = t[0]
    path = 'Statistic/%s.csv' % y
    if os.path.exists(path):
        with open(path, 'r') as fr:
            lines = csv.reader(fr)
            for line in lines:
                if line[0] == created_at:
                    logger.info('%s get from %s' % (line[1], path))
                    return line[1]
    else:
        search_condition = dict()
        search_condition['type'] = 'repository'
        search_condition['q'] = 'created:' + created_at
        return get_repo_num(search_condition)


def get_repo_info_single_page(search_condition, page=1):
    # 从单个搜索页面上获得该页面上项目的基本信息：项目名称、作者、path
    # return [name, owner, path, page]
    result_list = list()
    search_condition['p'] = page
    max_try = 0
    while max_try <= 5:
        max_try += 1
        try:
            resp = get_response.get_response(_SEARCH_URL, param=search_condition)
            soup = BeautifulSoup(resp.text, 'lxml')
            repo_list = soup.find('ul', 'repo-list').contents
            for i in range(1, len(repo_list), 2):
                repo_item = repo_list[i].find('h3').a
                repo_json = repo_item['data-hydro-click']
                repo_dict = json.loads(repo_json)
                repo_url = repo_dict['payload']['result']['url']
                repo_title = repo_item.string
                repo_titles = repo_title.split('/')
                repo_owner = repo_titles[0]
                repo_name = repo_titles[1]
                repo = [repo_name, repo_owner, repo_url, page]
                result_list.append(repo)
                logger.info("Try: %d | Date: %s | get : %s" % (max_try, search_condition['q'], repo_titles))
            break
        except Exception as e:
            time.sleep(max_try)
            logger.error("Try: %d  | Date: %s | Error : %s" % (max_try, search_condition['q'], str(e)))
    return result_list


def get_daily_result(d_str):
    count = get_daily_reponum(d_str)
    result = dict()
    search_condition = dict()
    search_condition['type'] = 'repository'
    search_condition['q'] = 'created:' + d_str
    max_page = (count // 10) + 1
    for page in range(1, max_page):
        result['page:' + str(page)] = get_repo_info_single_page(d_str, page)
    filename = '%s result.json' % d_str
    with open(filename, 'w') as fw:
        fw.writelines(json.dumps(result, indent=4))
    logger.info('%s done' % d_str)


if __name__ == '__main__':
    d = date(2008, 12, 31)
    r = get_daily_reponum(d.isoformat())
    print(r)

    # for day in range(356):
    #     get_daily_result(d.isoformat())
    #     d -= d.resolution
