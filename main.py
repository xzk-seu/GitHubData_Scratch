from datetime import date
from multiprocessing import Pool
import time
import json
import get_response
import search_page_parse
import result_write


_SEARCH_URL = 'https://github.com/search'


if __name__ == '__main__':
    d = date.today()
    p = Pool()
    d = date(2008, 12, 31)
    result_dict = dict()
    count = 365
    while count:
        d_str = d.isoformat()
        number_of_repo = p.apply_async(search_page_parse.get_daily_reponum, args=(d_str,)).get()
        result_write.write_csv('2008.csv', result_type='Statistic', header=['date', 'count'], body_list=[[d_str, number_of_repo]])
        # result_dict[d_str] = number_of_repo
        d -= d.resolution
        count -= 1
    p.close()
    p.join()
    # with open('result.json', 'w') as fw:
    #     fw.writelines(json.dumps(result_dict, indent=4))
