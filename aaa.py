# import requests

# url = "https://www.baidu.com/s?wd=%E6%AD%A6%E6%B1%89%E5%8C%BB%E7%BE%8E&pn=10"
# response = requests.get(url)
# if response.status_code == 200:
#   soup = BeautifulSoup(response.text, "html.parser")
#   print(soup)
#   a_tags = soup.find_all("a")
#   print(a_tags)
#   for a_tag in a_tags:
#       data_landurl = a_tag.get("data-landurl")
#       print(data_landurl)
#       if data_landurl and data_landurl.startswith("https://ada.baidu.com"):
#           print("找到匹配的URL:", data_landurl)


# -*-coding:utf8-*-

import re
import time
import random
import requests
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup


# 加载关键词列表
def load_keywords():
    key_words = []
    with open('./catchad/kw_city.txt', 'r', encoding='utf-8') as f_city, open('./catchad/kw_hospital.txt', 'r', encoding='utf-8') as f_hospital:
        city_list = [city.strip() for city in f_city.readlines()]
        hospital_list = [hospital.strip() for hospital in f_hospital.readlines()]
        if city_list and hospital_list:
            key_words = [f"{city}{hospital}" for city in city_list for hospital in hospital_list]

    return key_words


def headers():
    return {
        "User-Agent": UserAgent().random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,"
                  "image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Accept-Encoding": "gzip, deflate"
    }


def proxies():
    return {
        # 如需使用代理请自行替换，这里有一些不太好用的免费代理
        # - https://www.docip.net/#index
        # - https://openproxy.space/list

        # "http": "x.x.x.x:xx",
        # "https": "x.x.x.x:xx",
    }


def fetch(keyword):
    delay = random.uniform(0.5, 2.5)
    time.sleep(delay)
    print(f"当前关键字: {keyword}")

    max_page = 2
    url_template = 'http://www.baidu.com/s?wd={}&pn={}'
    pattern = r'https?://ada\.baidu\.com/site/[\w.-]+/xyl\?imid=[\w-]+'
    results = []
    try:
        urls_to_fetch = [url_template.format(keyword, page * 10) for page in range(max_page)]
        for url in urls_to_fetch:
            response = requests.get(url, headers=headers(), proxies=proxies())
            soup = BeautifulSoup(response.text, "html.parser")
            a_tags = soup.find_all("a")
            print(a_tags)
            # 提取匹配项并添加到结果列表中
            matches = re.findall(pattern, response.text)
            if matches:
                results.extend(matches)

    except Exception as e:
        print('Exception - ' + str(e))
    finally:
        if results:
            return list(set(results))

def scrape_ada():
    keywords = load_keywords()

    with open('./api.txt', 'a+', encoding='utf-8') as f:
        with ThreadPoolExecutor() as executor:
            for result in executor.map(fetch, keywords):
                if result:
                    f.write('\n'.join(result) + '\n')
        # 去重
        f.seek(0)
        unique_urls = set(line.strip() for line in f if line.strip())
        f.seek(0)
        f.truncate()
        f.write('\n'.join(unique_urls) + '\n')
        print('完成 api.txt 去重更新')


if __name__ == "__main__":
    scrape_ada()


