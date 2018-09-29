import requests
from bs4 import BeautifulSoup
import random
import time
from multiprocessing import Lock

"""
    ip代理池
    实现的功能：
    1、 爬取ip代理网站的ip地址 约10~20页
    2、 利用计时器定期更新ip地址
    3、 由于程序的架构，此类对象的调用会写在spider类中，MyResquest将接受它的对象
    4、 不同的ip提供方式，随机选择和ip轮询等等
"""

_AGENTS = [
    "Googlebot/2.1 (+http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile"
    "/10A5376e Safari/8536.25 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 8_3 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/8.0 Mobile"
    "/12F70 Safari/600.1.4 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile"
    "/12F70 Safari/600.1.4 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome"
    "/27.0.1453 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome"
    "/41.0.2272.96 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1;"
    " +http://www.google.com/bot.html) Safari/537.36",
    "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; Google Web Preview Analytics) Chrome/27.0.1453 Safari"
    "/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/41.0.2272.76 Chrome"
    "/41.0.2272.76 Safari/537.36",
]


def synchronized(func):
    func.__lock__ = Lock()

    def lock_function(*args, **kwargs):
        with func.__lock__:
            return func(*args, **kwargs)


class IPProvider(object):
    instance = None

    def __init__(self, numopages=5):
        self.__numopages = numopages
        self.__ip_list = []
        self.__time_tag = time.time()
        self.__count = -1
        self.cold_start = True
        self.cold_ip = {"https": "https://114.247.89.49:8000"}
        # self.__cold_start()

    # # def __cold_start(self):
    #     ty = input("type: ")
    #     ip = input("ip: ")
    #     port = input("port: ")
    #     self.cold_ip[ty] = ty + "://" + ip + ":" + port

    def get_ip(self):
        if len(self.__ip_list) < 1 or self.__count > len(self.__ip_list) or time.time() - self.__time_tag > 600:
            self.__get_ip_list()
        self.__count += 1

        return {
            self.__ip_list[self.__count][0]: self.__ip_list[self.__count][0] + "://" + self.__ip_list[self.__count][1] + ":" + self.__ip_list[self.__count][2]
                }

    def __get_ip_list(self):
        self.__time_tag = time.time()
        self.__count = -1
        for i in range(1, self.__numopages + 1):
            soup = self.__get_soup('http://www.xicidaili.com/nn/' + str(i))
            # print(soup)
            # 每一段ip
            for tr in soup.find_all("tr"):
                item = tr.find_all("td")
                if len(item) > 6:
                    self.__ip_list.append((item[5].getText().lower(), item[1].getText(), item[2].getText()))

    def __get_soup(self, url):
        headers = {
            "User-Agent": random.choice(_AGENTS),
        }
        r = None
        if self.cold_start:
            try:
                r = requests.get(url, headers=headers, proxies=self.cold_ip)
            except Exception as e:
                print(e)
            self.cold_start = True
        else:
            max_tries = 0
            while r is None and max_tries < 6:
                r = requests.get(url, headers=headers, proxies=self.formalize(random.choice(self.__ip_list)))
                max_tries += 1
        if r is None:
            raise NotImplemented
        r.encoding = "utf-8"
        return BeautifulSoup(r.text, "lxml")

    # def formalize(self, tp):
    #     return {
    #         tp[0]: tp[0] + "://" + tp[1] + ":" + tp[2]
    #             }


def formalize(tp):
    return {tp[0]: tp[0] + "://" + tp[1] + ":" + tp[2]}


if __name__ == "__main__":
    ipp = IPProvider(5)
    ip = IPProvider(5)
    print(ipp.get_ip())
