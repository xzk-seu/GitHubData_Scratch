from datetime import date
from multiprocessing import Pool
import daily_page_parse
import result_write


def stat_by_month(begin_day, end_day):
    day = begin_day
    pool = Pool()
    result_list = list()
    for d in range((end_day-begin_day).days+1):
        d_str = day.isoformat()
        res = pool.apply_async(daily_page_parse.get_daily_reponum, args=(d_str,))
        result_list.append([d_str, res])
        day += day.resolution
    pool.close()
    pool.join()
    for pair in result_list:
        pair[1] = pair[1].get()
    return result_list


if __name__ == '__main__':
    year = input('year:')
    year = int(year)
    begin = date(year, 1, 1)
    end = date(year, 12, 31)
    result = stat_by_month(begin, end)
    result_write.write_csv('%d.csv' % year, result_type=result_write.STATISTIC
                           , header=['date', 'count'], body_list=result)
