import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import re
import datetime
import pytz
import traceback
import json
import os.path
from my_exception import MyException


class WebCrawlerMohw(MyException):
    ENTRY_LINK = "np-16-1.html"
    URL = "https://www.mohw.gov.tw"

    def get_news_page_link_from_latest_month_or_year(self, *more_url):

        session = requests.Session()

        local_url = self.URL

        if more_url is not None:
            for link in more_url:
                local_url += "/" + link

        # 衛福部最新消息
        response = session.get(local_url)

        if response.status_code != requests.codes.ok:
            raise MyException("衛福部本站最新消息 Status code not OK: ",
                              response.status_code)

        soup = BeautifulSoup(response.text, "lxml")

        target_url = soup.select_one("section.nplist a")["href"]

        print("get_news_page_link_from_latest_month_or_year result url", local_url)
        return target_url

    def get_news_page_link(self, more_url):

        session = requests.Session()

        local_url = self.URL + "/" + more_url

        # 衛福部最新消息
        response = session.get(local_url)

        print("get_news_page_link local url", local_url)

        if response.status_code != requests.codes.ok:
            raise MyException("衛福部本站最新消息 Status code not OK: ",
                              response.status_code)

        soup = BeautifulSoup(response.text, "lxml")

        target = soup.select("section.list01 a")
        target_text = target[0].text
        if re.match(r'新增\d+例COVID-19\w*病例，分別為\d+例本土\w*及\d+例境外', target_text):
            print("get_news_page_link result url", target[0]["href"])
            return target[0]["href"]
        elif re.match(r'新增\d+例COVID-19\w*病例，分別為\d+例本土\w*及\d+例境外', target[1].text):
            print("get_news_page_link result url", target[1]["href"])
            return target[1]["href"]
        else:
            return None

    def get_news_article(self, url):
        session = requests.Session()

        local_url = url

        # 衛福部最新消息
        response = session.get(local_url)

        if response.status_code != requests.codes.ok:
            raise MyException("衛福部本站最新消息 Status code not OK: ",
                              response.status_code)

        soup = BeautifulSoup(response.text, "lxml")
        content = soup.select_one("section#ContentPage")
        print(content)

    def crawl(self):
        this_year_url = self.get_news_page_link_from_latest_month_or_year(
            self.ENTRY_LINK)

        if this_year_url is None:
            raise MyException("MOHW This year url is None")
        this_month_url = self.get_news_page_link_from_latest_month_or_year(
            this_year_url)

        if this_month_url is None:
            raise MyException("MOHW This month url is None")
        article_url = self.get_news_page_link(this_month_url)

        if article_url is None:
            raise MyException("MOHW This article url is None")
        article = self.get_news_article(article_url)
        print(article)


if __name__ == '__main__':
    crawler = WebCrawlerMohw()
    crawler.crawl()
