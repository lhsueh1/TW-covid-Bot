import requests
from bs4 import BeautifulSoup
import re
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import logging
from my_exception import MyException


class WebCrawlerCDC():
    ENTRY_LINK = "np-16-1.html"
    URL = "https://www.mohw.gov.tw"

    CDC_NEWS_URL = "https://www.cdc.gov.tw/Category/NewsPage/EmXemht4IT-IRAPrAnyG9A"

    

    def crawl(self):
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        # 衛福部最新消息
        response = session.get(self.CDC_NEWS_URL, verify=True)

        if response.status_code != requests.codes.ok:
            raise MyException("衛福部最新消息 Status code not OK")

        soup = BeautifulSoup(response.text, "html.parser")

        titles = soup.find("tbody")

        if titles is None:
            raise MyException("Unable to find tbody. 爬蟲網址有誤或是「衛福部最新消息」壞了")

        targets = titles.select('a[title*="COVID-19"]')[:20]
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
        self.article_url = f"https://www.cdc.gov.tw{target_href}"
        print(f"新聞稿連結: {self.article_url}")

        article_content = article_soup.find(
            "p", class_="con-word").get_text()
        article_date = article_soup.find(
            "div", class_="date text-right").get_text().strip()[5:]
        

        self.title = target_title
        self.article = article_content
        self.article_date = article_date
        
        logging.info("article url: "+self.article_url)
        logging.info("article title: "+self.title)
        logging.info("article date: "+self.article_date)
        logging.info("article: "+self.article)

# For testing purpose
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    crawler = WebCrawlerCDC()
    crawler.crawl()
