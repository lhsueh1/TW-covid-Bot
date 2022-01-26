import requests
from bs4 import BeautifulSoup
import re

import logging
from my_exception import MyException


class WebCrawlerMohw():
    ENTRY_LINK = "np-16-1.html"
    URL = "https://www.mohw.gov.tw"

    def __get_news_page_link_from_latest_month_or_year(self, *more_url):

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

        logging.info(
            "WebCrawlerMohw(): get_news_page_link result url " + target_url)
        return target_url

    def __get_news_page_link(self, more_url):

        session = requests.Session()

        local_url = self.URL + "/" + more_url

        # 衛福部最新消息
        response = session.get(local_url)

        if response.status_code != requests.codes.ok:
            raise MyException("衛福部本站最新消息 Status code not OK: ",
                              response.status_code)

        soup = BeautifulSoup(response.text, "lxml")

        target = soup.select("section.list01 a")
        i = 0
        while not re.match(r'新增\d+例COVID-19\w*病例，分別為\d+例本土\w*及\d+例境外', target[i].text):
            i += 1
        logging.info(
            "WebCrawlerMohw(): get_news_page_link result url " + target[0]["href"])

        return target[i]["href"]

    def __get_news(self, url):
        session = requests.Session()

        local_url = url

        # 衛福部最新消息
        response = session.get(local_url)

        if response.status_code != requests.codes.ok:
            raise MyException("衛福部本站最新消息 Status code not OK: ",
                              response.status_code)

        soup = BeautifulSoup(response.text, "lxml")
        content = soup.select_one("section#ContentPage")
        title = content.select_one("h2").text
        article_date = content.select("ul.info li")[1].select_one("em").text
        article = content.select_one("article").text

        return (title, article_date, article)

    def crawl(self):
        this_year_url = self.__get_news_page_link_from_latest_month_or_year(
            self.ENTRY_LINK)

        if this_year_url is None:
            raise MyException("MOHW This year url is None")
        this_month_url = self.__get_news_page_link_from_latest_month_or_year(
            this_year_url)

        if this_month_url is None:
            raise MyException("MOHW This month url is None")
        article_url = self.__get_news_page_link(this_month_url)

        if article_url is None:
            raise MyException("MOHW This article url is None")
        (self.title, self.article_date, self.article) = self.__get_news(article_url)
        self.article_url = article_url
        logging.info("article url: "+self.article_url)
        logging.info("article title: "+self.title)
        logging.info("article date: "+self.article_date)
        logging.info("article: "+self.article)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    crawler = WebCrawlerMohw()
    crawler.crawl()
