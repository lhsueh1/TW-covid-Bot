#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import pytz


class TodayConfirmed(object):
    """
    透過爬蟲找尋衛福部的最新消息中，
    第一篇標題含有"例COVID-19確定病例"的文章，
    並透過該文章的內容取得以下變數之資訊。
    """
    today_confirmed = None
    today_imported = None
    today_domestic = None
    today_deaths = None
    # To identify if today is the same day as this press release
    is_same_date = False
    date = None
    article = ""
    additional_text = ""
    article_link = ""
    error = False

    def __init__(self, url):
        self.web_crawler(url)

    def web_crawler(self, url):
        try:
            session = requests.Session()
            retry = Retry(connect=3, backoff_factor=0.5)
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            session.mount('https://', adapter)

            # 衛福部最新消息
            response = session.get(url)

            if response.status_code != requests.codes.ok:
                raise MyException("衛福部最新消息 Status code not OK")

            soup = BeautifulSoup(response.text, "html.parser")

            titles = soup.find("tbody")

            if titles is None:
                raise MyException("Unable to find tbody. 爬蟲網址有誤或是「衛福部最新消息」壞了")

            target = titles.select('a[title*="例COVID-19確定病例"]')[0]

            # 目標文章標題文字
            target_title = target.get_text().strip()

            # 目標文章超連結
            target_href = target.get("href")
            #print(target_title)
            #print(target_href)

            # 文章標題的確診病例、本土、境外處理
            newstr = ''.join((ch if ch in '0123456789' else ' ') for ch in target_title)
            listOfNumbers = [int(i) for i in newstr.split()]
            #print(listOfNumbers)
            self.today_confirmed = listOfNumbers[0]
            self.today_domestic = listOfNumbers[2]
            self.today_imported = listOfNumbers[3]

            # 病例公布新聞稿
            article_response = requests.get(
                "https://www.cdc.gov.tw" + target_href)
            article_soup = BeautifulSoup(article_response.text, "html.parser")
            self.article_link = f"https://www.cdc.gov.tw{target_href}"
            print(f"新聞稿連結: {self.article_link}")

            article_content = article_soup.find("p", class_="con-word").get_text()
            article_date = article_soup.find("div", class_="date text-right").get_text().strip()[5:]
            dates = article_date.split("/")
            #print(article_content)
            #print(article_date)


            texts = article_content.split()

            # Addidtional text 處理
            # 個案分佈 及 疫調資訊
            for t in texts:
                if "個案分布" in t:
                    texts = t.split("個案分布")
            self.additional_text = "個案分布"+texts[1]
            self.additional_text = self.additional_text.replace("；", "。\n")
            self.additional_text = self.additional_text.replace("，將持續進行疫情調查，以釐清感染源", "")


            if self.additional_text is not None or self.additional_text != "":
                self.additional_text = "\n" + self.additional_text

            # 死亡分析
            regex_death = re.compile(r"新增(\d+-*\d*)例死亡")
            match_death = regex_death.search(article_content)
            if match_death is not None:
                self.today_deaths = match_death.group(1)

            if re.search(r"無新增死亡", article_content):
                self.today_deaths = 0

            # todo 如果新聞稿發布日期<今日日期-12小時，會發出錯誤
            d1 = datetime(int(dates[0]), int(dates[1]), int(dates[2]))
            #d1 = datetime(int(dates[0]), int(dates[1]), int(dates[2])+1)
            d2 = datetime.now(pytz.timezone('Asia/Taipei')) - timedelta(hours=36)
            d2 = d2.replace(tzinfo=None)
            self.date = d1
            if d1 < d2:
                print("日期錯誤")
                self.is_same_date = False
            else:
                self.is_same_date = True

        except requests.exceptions.HTTPError as e:
            print("HTTPError: ", e.reason)
            error = e
        except Exception as e:
            print("ERROR: TodayConfirmed init failed")
            print(e)
            error = e

# class TotalTestsConducted(object):
#     total_tests_conducted = None
#
#     def __init__(self):
#         self.web_crawler()
#
#     def web_crawler(self):
#         # try:
#
#         h = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0"}
#         response = requests.get(
#             "https://sites.google.com/cdc.gov.tw/2019ncov/total-tests-conducted-tw", headers=h)
#         soup = BeautifulSoup(response.text, "html.parser")
#
#
#
#         self.total_tests_conducted = soup.find(id="num9").get_text().strip()
#         print(self.total_tests_conducted)
#         # except Exception as e:
#         #     print("ERROR: TotalTestsConducted init failed")
#         #     print(e)

class MyException(Exception):
    pass

if __name__ == '__main__':
    TodayConfirmed()
    # TotalTestsConducted()
