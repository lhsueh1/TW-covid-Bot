import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import pytz


class TodayConfirmed(object):
    today_confirmed = None
    today_imported = None
    today_domestic = None
    is_same_date = False
    date = None
    article = ""
    additional_text = ""

    def __init__(self):
        self.web_crawler()

    def web_crawler(self):
        try:
            response = requests.get(
                "https://www.cdc.gov.tw/Category/NewsPage/EmXemht4IT-IRAPrAnyG9A")
            soup = BeautifulSoup(response.text, "html.parser")

            titles = soup.find("tbody")
            target = titles.select('a[title*="例COVID-19確定病例"]')[0]

            target_title = target.get_text().strip()
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

            article_response = requests.get(
                "https://www.cdc.gov.tw" + target_href)
            article_soup = BeautifulSoup(article_response.text, "html.parser")

            article_content = article_soup.find("p", class_="con-word").get_text()
            article_date = article_soup.find("div", class_="date text-right").get_text().strip()[5:]
            dates = article_date.split("/")
            #print(article_content)
            #print(article_date)

            d1 = datetime(int(dates[0]), int(dates[1]), int(dates[2])).date()
            #d1 = datetime(int(dates[0]), int(dates[1]), int(dates[2])+1).date()
            d2 = datetime.now(pytz.timezone('Asia/Taipei')).date()
            self.date = d1

            texts = article_content.split()

            # Addidtional text 處理
            # 個案分佈 及 疫調資訊
            for t in texts:
                if "個案分布" in t:
                    texts = t.split("個案分布")
            self.additional_text = "個案分布"+texts[1]
            self.additional_text = self.additional_text.replace("；", "。\n")

            if self.additional_text is not None or self.additional_text != "":
                self.additional_text = "\n" + self.additional_text

            # 無新增死亡
            # 新增3例死亡

            # todo 如果發布日期不對會跳 error
            if d1 != d2:
                print("日期錯誤")
                # print(d1)
                # print(d2)
                self.is_same_date = False
            else:
                self.is_same_date = True
        except Exception as e:
            print("ERROR: TodayConfirmed init failed")
            print(e)

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

if __name__ == '__main__':
    TodayConfirmed()
    # TotalTestsConducted()
