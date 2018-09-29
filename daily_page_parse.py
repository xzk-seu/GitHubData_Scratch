from datetime import date
from bs4 import BeautifulSoup
import get_response
import time
import json
import my_logger


_SEARCH_URL = 'https://github.com/search'
logger = my_logger.get_logger(log_file_name='daily_page_parser.log')


def get_daily_reponum(created_at):
    search_condition = dict()
    search_condition['type'] = 'repository'
    search_condition['q'] = 'created:' + created_at
    num = None
    max_try = 0
    while max_try <= 5:
        max_try += 1
        try:
            resp = get_response.get_response(_SEARCH_URL, param=search_condition)
            soup = BeautifulSoup(resp.text, 'lxml')
            result_str = soup.find_all('h3')[1].string.strip('\n repository results').replace(',', '')
            num = int(result_str)
            logger.info("Try: %d | Date: %s | get : %s" % (max_try, created_at, result_str))
            break
        except Exception as e:
            time.sleep(max_try)
            logger.error("Try: %d | Error : %s" % (max_try, str(e)))
    return num


def daily_page_parse(created_at, page=1):
    result_dict = dict()
    search_condition = dict()
    search_condition['type'] = 'repository'
    search_condition['q'] = 'created:' + created_at
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
                repo = dict(name=repo_name, owner=repo_owner, path=repo_url)
                result_dict[repo_title] = repo
                logger.info("Try: %d | Date: %s | get : %s" % (max_try, created_at, repo_titles))
            break
        except Exception as e:
            time.sleep(max_try)
            logger.error("Try: %d  | Date: %s | Error : %s" % (max_try, created_at, str(e)))
    return result_dict


def get_daily_result(d_str):
    count = get_daily_reponum(d_str)
    result = dict()
    max_page = (count // 10) + 1
    for page in range(1, max_page):
        result['page:' + str(page)] = daily_page_parse(d.isoformat(), page)
    filename = '%s result.json' % d_str
    with open(filename, 'w') as fw:
        fw.writelines(json.dumps(result, indent=4))
    logger.info('%s done' % d_str)


if __name__ == '__main__':
    d = date(2008, 12, 31)
    for day in range(356):
        get_daily_result(d.isoformat())
        d -= d.resolution
