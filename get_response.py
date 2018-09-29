import requests
import my_logger
from ip_pool import IPProvider
import ip_pool
import random


_AGENTS = ip_pool._AGENTS
ip = IPProvider()
_HEADERS = {'User-Agent': random.choice(_AGENTS)}


def get_response(url, param=None):
    pr = ip.get_ip()
    # logger = my_logger.get_logger(log_file_name='response.log')
    # logger.info(str(pr))
    r = requests.get(url=url, params=param, headers=_HEADERS, proxies=pr)
    r.raise_for_status()
    r.encoding = r.apparent_encoding
    return r
