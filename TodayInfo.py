
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import re
import datetime
import pytz
import traceback
import json
import os.path
import logging

from my_exception import MyException


class TodayInfo:
    """
    本日疫情資訊的物件

    Attributes
    ----------
    today_confirmed : int or str
        今日確診人數
    today_imported : int or str
        今日境外移入確診人數
    today_domestic : int or str
        今日本土確診人數
    today_deaths : int or str
        今日死亡人數
    article_title : str
        文章標題
    additional_text : str
        顯示於資訊中的額外文字描述
    article : str
        爬蟲下來的文章全文
    article_link : str
        透過爬蟲取得的文章連結
    is_same_date : bool
        文章發布日期是否是今天
    date : str
        文章發布日期
    error : bool or str
        是否有錯誤、錯誤訊息
    __is_generated : bool
        確診人數等資料是否以填入

    Methods
    -------
    check_generate_status()
        確認並更新 is_generated 的狀態
    """

    def __init__(self,
                 today_confirmed,
                 today_imported,
                 today_domestic,
                 today_deaths=0,
                 additional_text="",
                 article_link="",
                 error=False,
                 article_title="",
                 article=None,
                 is_generate=True):
        """
        Python 只能有一個 constructor
        如果沒有要一次把所有資訊初始化，可以透過下面的 clssmethod。例如：
        today = TodayInfo.from_article(article)
        或
        today = TodayInfo.create_empty()
        之後再生成文章

        Parameters
        ----------
        today_confirmed : int or str
            今日確診人數
        today_imported : int or str
            今日境外移入確診人數
        today_domestic : int or str
            今日本土確診人數
        today_deaths : int or str
            今日死亡人數
        additional_text : str, optional
            顯示於資訊中的額外文字描述
        article_link : str, optional
            透過爬蟲取得的文章連結
        is_same_date : bool, optional
            文章發布日期是否是今天
        error : bool or str
            是否有錯誤、錯誤訊息
        article_title : str, optional
            文章標題
        article : str, optional
            爬蟲下來的文章全文
        is_generated : bool, optional
            確診人數等資料是否以填入

        Returns
        -------
        None
        """
        self.today_confirmed = today_confirmed
        self.today_imported = today_imported
        self.today_domestic = today_domestic
        self.today_deaths = today_deaths
        self.additional_text = additional_text
        self.article = article
        self.article_title = article_title
        self.article_link = article_link
        # To identify if today is the same day as this press release
        self.is_same_date = True
        self.date = datetime.date.today()
        self.error = error
        self.__is_generated = is_generate

    @classmethod
    def from_article(cls, article: str):
        """
        輸入文章，需要再呼叫 function 透過文章分析資料
        """
        logging.info("TodayInfo: from article")
        error = "Object initialized by article only."
        return cls(today_confirmed=None, today_imported=None, today_domestic=None, article=article, is_generate=False, error=error)

    @classmethod
    def create_empty(cls):
        """
        先init object，需要再呼叫 function 爬蟲來取得資料
        """
        logging.info("TodayInfo: create_empty")
        error = "Object not initialized."
        return cls(today_confirmed=None, today_imported=None, today_domestic=None, is_generate=False, error=error)

    @classmethod
    def from_json(cls, filepath=None):
        """
        透過本地json取得資料。若讀取失敗會呼叫 create_empty()
        """
        logging.info("TodayInfo: init from json")
        if filepath is None:
            filepath = 'TodayConfirmed.json'
        if os.path.isfile(filepath):
            try:
                with open(filepath, 'r', encoding='utf8') as openfile:
                    today_dict = json.load(openfile)
                    today_confirmed = today_dict["today_confirmed"]
                    today_domestic = today_dict["today_domestic"]
                    today_imported = today_dict["today_imported"]
                    today_deaths = today_dict["today_deaths"]
                    additional_text = today_dict["additional_text"]
                    json_datetime = today_dict["date"]
                    date = datetime.date.fromisoformat(json_datetime)
                    article_link = today_dict["article_link"]
                    error = today_dict["error"]
                    is_same_date = cls.__date_compare(date)

                    if error is not False:
                        logging.warning(
                            "Error info in today confirmed info json is not false. Initialize from json failed.")
                        return cls.create_empty()
                    elif is_same_date is not True:
                        logging.warning(
                            "Today is a new day. Initialize from json failed.")
                        return cls.create_empty()
                    else:
                        logging.info(
                            "Extracted today confirmed info from json.")
                        return cls(today_confirmed, today_imported, today_domestic, today_deaths, additional_text, article_link, error)

            except Exception as e:
                logging.error(
                    "Unable to extract today confirmed info from json. Initialize from json failed.")
                print(e)
                tb_msg = traceback.format_tb(e.__traceback__)
                print(*tb_msg, sep='\n')
                # self.web_crawler(url)
                return cls.create_empty()

    def check_generate_status(self):
        if self.today_confirmed is None or self.today_imported is None or self.today_domestic is None:
            self.__is_generated = False
            return False
        if TodayInfo.__date_compare(self.date):
            self.is_same_date = True
            self.__is_generated = True
            return True
        else:
            self.is_same_date = False
            self.__is_generated = False
            return False
            

    @staticmethod
    def __date_compare(article_date):
        """如果新聞稿發布日期<今日日期-12小時，會發出錯誤"""

        d2 = datetime.date.today()
        if article_date < d2:
            print(f"日期錯誤:{article_date}")
            return False
        else:
            return True

    def __str__(self) -> str:
        """
        印出 TodayInfo 的資訊
        """
        if self.__is_generated:
            str = f"""
TodayInfo:
today_confirmed = {self.today_confirmed}
today_imported = {self.today_imported}
today_domestic = {self.today_domestic}
today_deaths = {self.today_deaths}
is_same_date = {self.is_same_date}
date = {self.date}
additional_text = {self.additional_text}
error = {self.error}
"""
        else:
            str = f"""
Today info not generated.
Error message:
{self.error}
"""
        return str

    def date_str_to_datetime(self):
        if isinstance(self.date, str):
            date_text_match = re.search(
                r'\d{3,4}[-/]\d{1,2}[-/]\d{1,2}', self.date)
            if date_text_match is not None:
                date_text = re.findall(r'\d+', date_text_match.group(0))
                date_year = int(date_text[0])

                # 中華民國還沒死透
                if date_year < 2000:
                    date_year = date_year + 1911

                date_month = int(date_text[1])

                date_day = int(date_text[2])
                self.date = datetime.date(date_year, date_month, date_day)
            else:
                self.date = datetime.date.today()
        elif isinstance(self.date, datetime):
            logging.info("TodayInfo.date_str_to_datetime: Already datetime.")
        else:
            logging.error(
                "TodayInfo.date_str_to_datetime: Type self.date error.")
    
    def save_to_json(self):
        formatted_datetime = self.date.isoformat()

        dict = {
            "today_confirmed": self.today_confirmed,
            "today_domestic": self.today_domestic,
            "today_imported": self.today_imported,
            "today_deaths": self.today_deaths,
            "additional_text": self.additional_text,
            "date": formatted_datetime,
            "article_link": self.article_link,
            "error": self.error,
        }

        json_object = json.dumps(dict, indent=4, ensure_ascii=False)

        with open("TodayConfirmed.json", "w", encoding='utf8') as outfile:
            outfile.write(json_object)


# Deprecated
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
        if "ismanual" in kwargs:
            if kwargs["ismanual"]:
                self.is_same_date = True
                self.data_extractor("", kwargs["article"])
                if kwargs["save"]:
                    self.save_to_json()
                return

        if "recrawl" in kwargs:
            if kwargs["recrawl"]:
                self.web_crawler(url)
                return

        if url != 0:
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
                    self.date = datetime.date.fromisoformat(json_datetime)
                    self.article_link = today_dict["article_link"]
                    self.error = today_dict["error"]

                    self.date_compare(self.date)

                    if self.error is not False:
                        print(
                            "Error info in today confirmed info json is not false. Trying web crawler.")
                        self.web_crawler(url)
                    elif self.is_same_date is not True:
                        print("Today is a new day. Trying web crawler.")
                        self.web_crawler(url)
                    else:
                        print("Extracted today confirmed info from json.")

            except Exception as e:
                print(
                    "Unable to extract today confirmed info from json. Trying web crawler.")
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
            response = session.get(url, verify=SSLVerify)

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

            article_content = article_soup.find(
                "p", class_="con-word").get_text()
            article_date = article_soup.find(
                "div", class_="date text-right").get_text().strip()[5:]
            dates = article_date.split("/")

            self.data_extractor(target_title, article_content)

            d1 = datetime.date(int(dates[0]), int(dates[1]), int(dates[2]))
            self.date_compare(d1)
            self.date = d1

            self.error = False
            self.save_to_json()

        except requests.exceptions.HTTPError as e:
            print("HTTPError: ", e.reason)
            self.error = e

        except Exception as e:
            print("ERROR: TodayConfirmed init failed")
            print(e)
            tb_msg = traceback.format_tb(e.__traceback__)
            print(*tb_msg, sep='\n')

    def data_extractor(self, title, article_content):
        # 文章標題的確診病例、本土、境外處理
        if re.match(r'新增\d+例COVID-19\w*病例，分別為\d+例本土\w*及\d+例境外', title):
            nums = re.findall(r'\d+', title)
            self.today_confirmed = int(nums[0])
            self.today_domestic = int(nums[2])
            self.today_imported = int(nums[3])

        elif re.match(r'新增\d+例境外\w*移入COVID-19\w*病例', title):
            nums = re.findall(r'\d+', title)
            self.today_confirmed = int(nums[0])
            self.today_domestic = 0
            self.today_imported = int(nums[0])

        # 如果標題找不到境外移入、本土的病例數量的話，透過文章分析
        # 利用article_content找到 新增\d+例境外移入 並判斷本土數量
        elif re.search(r'新增\d+例COVID-19\w*病例', title):
            nums = re.findall(r'\d+', title)
            self.today_confirmed = nums[0]

            self.today_imported = self.extract_number(
                r'新增\w?\d+例境外', article_content)
            self.today_domestic = self.extract_number(
                r'新增\w?\d+例本土', article_content)

            if self.today_domestic is None and self.today_confirmed is not None and self.today_imported is not None:
                self.today_domestic = int(
                    self.today_confirmed) - int(self.today_imported)

            if self.today_imported is None and self.today_confirmed is not None and self.today_domestic is not None:
                self.today_imported = int(
                    self.today_confirmed) - int(self.today_domestic)

        # 如果不是透過爬蟲取得的文章，就不會有標題，故透過文章分析資料，並分析日期
        if title == "":
            self.today_confirmed = self.extract_number(
                r'新增\d+例COVID-19\w*病例', article_content)
            self.today_imported = self.extract_number(
                r'新增\w?\d+例境外', article_content)
            self.today_domestic = self.extract_number(
                r'新增\w?\d+例本土', article_content)

            if self.today_domestic is None and self.today_confirmed is not None and self.today_imported is not None:
                self.today_domestic = int(
                    self.today_confirmed) - int(self.today_imported)

            if self.today_imported is None and self.today_confirmed is not None and self.today_domestic is not None:
                self.today_imported = int(
                    self.today_confirmed) - int(self.today_domestic)

            # 抓日期
            date_text_match = re.search(
                r'\d{3,4}[-/]\d{1,2}[-/]\d{1,2}', article_content)
            if date_text_match is not None:
                date_text = re.findall(r'\d+', date_text_match.group(0))
                date_year = int(date_text[0])

                # 中華民國還沒死透
                if date_year < 2000:
                    date_year = date_year + 1911

                date_month = int(date_text[1])

                date_day = int(date_text[2])
                self.date = datetime.date(date_year, date_month, date_day)
            else:
                self.date = datetime.date.today()

        # 死亡分析
        regex_death = re.compile(r"新增(\d+-*\d*)例死亡")
        match_death = regex_death.search(article_content)
        if match_death is not None:
            self.today_deaths = match_death.group(1)

        if re.search(r"無新增死亡", article_content):
            self.today_deaths = 0

        if self.today_confirmed is None or self.today_domestic is None or self.today_imported is None or self.today_deaths is None:
            self.error = f"""
本日數據包含None
today_confirmed = {self.today_confirmed}
today_imported = {self.today_imported}
today_domestic = {self.today_domestic}
today_deaths = {self.today_deaths}
"""
            return

        texts = article_content.split()

        self.additional_text = texts[1] + texts[2]
        self.additional_text = self.additional_text.replace("；", "。\n")
        self.additional_text = self.additional_text.replace("指揮中心表示，", "")
        self.additional_text = self.additional_text.replace("指揮中心說明，", "")
        self.additional_text = self.additional_text.replace("，個案分佈", "\n個案分佈")
        self.additional_text = self.additional_text.replace("，個案分布", "。\n個案分布")
        self.additional_text = self.additional_text.replace(
            "，將持續進行疫情調查，以釐清感染源", "")
        self.additional_text = self.additional_text.replace(
            "，衛生單位刻正進行相關疫調及接觸者匡列", "")
        self.additional_text = self.additional_text.replace(
            "。衛生單位將持續進行疫情調查及防治，以釐清感染源", "")
        self.additional_text = self.additional_text.replace(
            "，衛生單位將持續進行疫情調查及防治，以釐清感染源", "")
        self.additional_text = self.additional_text.replace(
            "將持續進行疫情調查及防治，以釐清感染源。", "")
        self.additional_text = self.additional_text.replace(
            "衛生單位持續進行疫情調查及防治，接觸者匡列中。", "")
        self.additional_text = self.additional_text.replace("詳如新聞稿附件。", "")

        # 因應文章格式加入換行
        if self.additional_text is not None and self.additional_text != "":
            self.additional_text = "\n" + self.additional_text

            # 刪除多餘的換行
            # only remove trailing newline characters.
            self.additional_text = self.additional_text.rstrip()

    def extract_number(self, regex: str, text: str):
        text_matched = re.search(regex, text)
        if text_matched is not None:
            num_match = re.search(r'\d+', text_matched.group(0))
            return int(num_match.group(0))
        return None

    def save_to_json(self):
        formatted_datetime = self.date.isoformat()

        dict = {
            "today_confirmed": self.today_confirmed,
            "today_domestic": self.today_domestic,
            "today_imported": self.today_imported,
            "today_deaths": self.today_deaths,
            "additional_text": self.additional_text,
            "date": formatted_datetime,
            "article_link": self.article_link,
            "error": self.error,
        }

        json_object = json.dumps(dict, indent=4, ensure_ascii=False)

        with open("TodayConfirmed.json", "w", encoding='utf8') as outfile:
            outfile.write(json_object)

    def date_compare(self, article_date):
        """如果新聞稿發布日期<今日日期-12小時，會發出錯誤"""

        d2 = datetime.date.today()
        if article_date < d2:
            print(f"日期錯誤:{article_date}")
            self.is_same_date = False
        else:
            self.is_same_date = True


# for testing purpose
if __name__ == '__main__':
    TodayConfirmed(
        "https://www.cdc.gov.tw/Category/NewsPage/EmXemht4IT-IRAPrAnyG9A", recrawl="recrawl")
    # TotalTestsConducted()
