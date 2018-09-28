from bs4 import BeautifulSoup
from datetime import date
from Logger import logger
from multiprocessing import Pool
import time
import json
import Resp
import daily_page_parse


_SEARCH_URL = 'https://github.com/search'


if __name__ == '__main__':
    d = date.today()
    p = Pool()
    d = date(2008, 12, 31)
    result_dict = dict()
    count = 5
    while count:
        d_str = d.isoformat()
        number_of_repo = p.apply_async(daily_page_parse.get_daily_reponum, args=(d_str,)).get()
        result_dict[d_str] = number_of_repo
        d -= d.resolution
        count -= 1
    p.close()
    p.join()
    with open('result.json', 'w') as fw:
        fw.writelines(json.dumps(result_dict, indent=4))
