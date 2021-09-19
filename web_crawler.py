#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import pytz
import traceback
import json
import os.path

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

    def __init__(self, url, **kwargs):
        if "recrawl" in kwargs:
            if kwargs["recrawl"]:
                self.web_crawler(url)
            else:
                self.init(url, **kwargs)
        elif url != 0:
            self.init(url, **kwargs)

    def init(self, url, **kwargs):
        if os.path.isfile('TodayConfirmed.json'):
            try:
                with open('TodayConfirmed.json', 'r', encoding='utf8') as openfile:
                    today_dict = json.load(openfile)
                    self.today_confirmed = today_dict["today_confirmed"]
                    self.today_domestic = today_dict["today_domestic"]
                    self.today_imported = today_dict["today_imported"]
                    self.today_deaths = today_dict["today_deaths"]
                    self.additional_text = today_dict["additional_text"]
                    json_datetime = today_dict["date"]
                    self.date = datetime.fromisoformat(json_datetime)
                    self.article_link = today_dict["article_link"]
                    self.error = today_dict["error"]

                    self.date_compare(self.date)

                    if self.error is not False:
                        print("Error info in today confirmed info json is not false. Trying web crawler.")
                        self.web_crawler(url)
                    elif self.is_same_date is not True:
                        print("Today is a new day. Trying web crawler.")
                        self.web_crawler(url)
                    else:
                        print("Extracted today confirmed info from json.")

            except Exception as e:
                print("Unable to extract today confirmed info from json. Trying web crawler.")
                tb_msg = traceback.format_tb(e.__traceback__)
                print(*tb_msg, sep='\n')
                self.web_crawler(url)
        else:
            self.web_crawler(url)

    def web_crawler(self, url, **kwargs):
        self.today_confirmed = 0
        self.today_domestic = 0
        self.today_imported = 0
        self.today_deaths = 0
        self.additional_text = ""

        if "max_retries" in kwargs:
            max_retries = kwargs["max_retries"]
        else:
            max_retries = 3

        if "SSLVerify" in kwargs:
            SSLVerify = kwargs["SSLVerify"]
        else:
            SSLVerify = True

        try:
            session = requests.Session()
            retry = Retry(connect=max_retries, backoff_factor=0.5)
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            session.mount('https://', adapter)

            # 衛福部最新消息
            response = session.get(url, verify = SSLVerify)

            if response.status_code != requests.codes.ok:
                raise MyException("衛福部最新消息 Status code not OK")

            soup = BeautifulSoup(response.text, "html.parser")

            titles = soup.find("tbody")

            if titles is None:
                raise MyException("Unable to find tbody. 爬蟲網址有誤或是「衛福部最新消息」壞了")

            targets = titles.select('a[title*="COVID-19"]')[:5]
            for target in targets:
                title = target.get('title')
                print(f"找到的標題：{title}")
                if re.search(r'COVID-19\w*病例', title):
                    target_title = title
                    target_href = target.get("href")
                    break

            # 病例公布新聞稿
            article_response = requests.get(
                "https://www.cdc.gov.tw" + target_href)
            article_soup = BeautifulSoup(article_response.text, "html.parser")
            self.article_link = f"https://www.cdc.gov.tw{target_href}"
            print(f"新聞稿連結: {self.article_link}")

            article_content = article_soup.find("p", class_="con-word").get_text()
            article_date = article_soup.find("div", class_="date text-right").get_text().strip()[5:]
            dates = article_date.split("/")

            self.data_extractor(target_title, article_content)

            d1 = datetime(int(dates[0]), int(dates[1]), int(dates[2]))
            self.date_compare(d1)
            self.date = d1


        except requests.exceptions.HTTPError as e:
            print("HTTPError: ", e.reason)
            self.error = e

        except Exception as e:
            print("ERROR: TodayConfirmed init failed")
            tb_msg = traceback.format_tb(e.__traceback__)
            print(*tb_msg, sep='\n')

        self.error = False
        self.save_to_json()

    def data_extractor(self, title, article_content):
        # 文章標題的確診病例、本土、境外處理
        if re.match(r'新增\d+例COVID-19\w*病例，分別為\d+例本土及\d+例境外移入', title):
            newstr = ''.join((ch if ch in '0123456789' else ' ') for ch in title)
            listOfNumbers = [int(i) for i in newstr.split()]
            #print(listOfNumbers)
            self.today_confirmed = listOfNumbers[0]
            self.today_domestic = listOfNumbers[2]
            self.today_imported = listOfNumbers[3]

        elif re.match(r'新增\d+例境外移入COVID-19\w*病例', title):
            newstr = ''.join((ch if ch in '0123456789' else ' ') for ch in title)
            listOfNumbers = [int(i) for i in newstr.split()]
            #print(listOfNumbers)
            self.today_confirmed = listOfNumbers[0]
            self.today_domestic = 0
            self.today_imported = listOfNumbers[0]

        # 如果標題找不到境外移入、本土的病例數量的話，透過文章分析
        # 利用article_content找到 新增\d+例境外移入 並判斷本土數量
        elif re.search(r'新增\d+例COVID-19\w*病例', title):
            newstr = ''.join((ch if ch in '0123456789' else ' ') for ch in title)
            listOfNumbers = [int(i) for i in newstr.split()]
            self.today_confirmed = listOfNumbers[0]

            imported_text_match = re.search(r'新增\w?\d+例境外移入', article_content)
            if imported_text_match is not None:
                num_mtach = re.search(r'\d+', imported_text_match.group(0))
                self.today_imported = int(num_mtach.group(0))

            domestic_text_match = re.search(r'新增\w?\d+例本土病例', article_content)
            if domestic_text_match is not None:
                num_mtach = re.search(r'\d+', domestic_text_match.group(0))
                self.today_imported = int(num_mtach.group(0))

            if self.today_domestic is None and self.today_confirmed is not None and self.today_imported is not None:
                self.today_domestic = int(self.today_confirmed) - int(self.today_imported)

            if self.today_imported is None and self.today_confirmed is not None and self.today_domestic is not None:
                self.today_imported = int(self.today_confirmed) - int(self.today_domestic)

        texts = article_content.split()

        self.additional_text = texts[1]
        self.additional_text = self.additional_text.replace("；", "。\n")
        self.additional_text = self.additional_text.replace("指揮中心表示，", "")
        self.additional_text = self.additional_text.replace("指揮中心說明，", "")
        self.additional_text = self.additional_text.replace("，個案分佈", "\n個案分佈")
        self.additional_text = self.additional_text.replace("，個案分布", "。\n個案分布")
        self.additional_text = self.additional_text.replace("，將持續進行疫情調查，以釐清感染源", "")
        self.additional_text = self.additional_text.replace("，衛生單位刻正進行相關疫調及接觸者匡列", "")
        self.additional_text = self.additional_text.replace("。衛生單位將持續進行疫情調查及防治，以釐清感染源", "")
        self.additional_text = self.additional_text.replace("，衛生單位將持續進行疫情調查及防治，以釐清感染源", "")
        self.additional_text = self.additional_text.replace("衛生單位持續進行疫情調查及防治，接觸者匡列中。", "")
        self.additional_text = self.additional_text.replace("詳如新聞稿附件。", "")


        if self.additional_text is not None and self.additional_text != "":
            self.additional_text = "\n" + self.additional_text

        # 死亡分析
        regex_death = re.compile(r"新增(\d+-*\d*)例死亡")
        match_death = regex_death.search(article_content)
        if match_death is not None:
            self.today_deaths = match_death.group(1)

        if re.search(r"無新增死亡", article_content):
            self.today_deaths = 0

    def save_to_json(self):
        formatted_datetime = self.date.isoformat()

        dict = {
            "today_confirmed" : self.today_confirmed,
            "today_domestic" : self.today_domestic,
            "today_imported" : self.today_imported,
            "today_deaths" : self.today_deaths,
            "additional_text" : self.additional_text,
            "date" : formatted_datetime,
            "article_link" : self.article_link,
            "error" : self.error,
        }

        json_object = json.dumps(dict, indent = 4, ensure_ascii = False)

        with open("TodayConfirmed.json", "w", encoding='utf8') as outfile:
            outfile.write(json_object)

    def date_compare(self, article_date):
        """如果新聞稿發布日期<今日日期-12小時，會發出錯誤"""

        d2 = datetime.now(pytz.timezone('Asia/Taipei')) - timedelta(hours=36)
        d2 = d2.replace(tzinfo=None)
        if article_date < d2:
            print(f"日期錯誤:{article_date}")
            self.is_same_date = False
        else:
            self.is_same_date = True

class MyException(Exception):

    pass


if __name__ == '__main__':
    TodayConfirmed()
    # TotalTestsConducted()
