import logging
from git import Object
import requests
import csv
import json
from datetime import datetime
import pytz
from article_analyzer import ArticleAnalyzer
from TodayInfo import TodayInfo
from TodayInfo import TodayConfirmed
from web_crawler_cdc import WebCrawlerCDC

from web_crawler_mohw import WebCrawlerMohw

ERROR_INTERNET_CONNECTION = "ERROR_INTERNET_CONNECTION"
ERROR_OPEN_DATA_SERVICE = "ERROR_OPEN_DATA_SERVICE "
ERROR_CDC_WEBPAGE = "ERROR_CDC_WEBPAGE"
ERROR_NOT_SAME_DATE = "ERROR_NOT_SAME_DATE"

CDC_NEWS_URL = "https://www.cdc.gov.tw/Category/NewsPage/EmXemht4IT-IRAPrAnyG9A"


def get_taiwan_epidemic_status():
    url = "https://od.cdc.gov.tw/eic/covid19/covid19_tw_stats.csv"
    with requests.Session() as s:
        download = s.get(url)

        decoded_content = download.content.decode('utf-8')

        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        data_list = list(cr)
        data_list = list(map(list, zip(*data_list)))
        text = "```\n"
        # t = PrettyTable(data_list[0])
        # t.add_row(data_list[1])
        for row in data_list:
            for data in row:
                text += str(data + "　")
            text += "\n"
        # text += str(t)
        text += "```"
        # return str(f"總確診數：{data_list[1][0]}")
        print(text)
        return text
    return False


def get_taiwan_outbreak_information(
        force: bool = False,
        SSLVerify: bool = True,
        recrawl: bool = False,
        manual: bool = False,
        save_to_json: bool = True,
        article: str = None,
        today_dict: dict = None,
        mohw: bool = False,
        cdc: bool = False):
    """
    產生回傳臺灣疫情資訊站的標準格式文章。

        Arguments:
            force: 跳過疾管暑官網的爬蟲，產生其他API提供的資料，如果API接不到一樣會出現錯誤
            SSLVerify: SSL安全性認證
            recrawl: 重新爬蟲並取得資料（預設讀取 json 儲存的資料）
            manual: 手動模式，必須要填入 article
            save_to_json: 手動模式，儲存至 json，可能會 deprecated
            article: 手動模式的文章，必須要 manual = True
            today_dict: 今天的資訊的 dict
            mohw: 指定以衛福部新聞稿爬蟲
            cdc: 指定以疾管暑新聞稿爬蟲

        Returns:
            text (str): 臺灣疫情資訊站的標準格式文章或用戶可讀的錯誤訊息
            status (str): 狀態訊息以及debug用錯誤訊息，回傳"0"表示成功
            today.article_link (str): 文章連結
    """

    # 取得並判斷網路狀態，若出現錯誤會 early return
    api_status = get_API_status(SSLVerify)

    if not api_status[0]:
        text = "ERROR: 網路錯誤\n" + api_status[0]
        status = ERROR_INTERNET_CONNECTION + \
                 "\nUnable to get status from Taiwan CDC Open Data Service\n" + \
                 api_status[0] + "\n" + api_status[1]
        return (text, status, "")
    elif api_status[0] == "success":
        print("Taiwan CDC Open Data Service, connection succeed.")
        status = 0
    else:
        text = "ERROR: 政府資料開放平台無法連接\n訊息：" + api_status[0]
        status = ERROR_OPEN_DATA_SERVICE + "\n訊息：" + \
                 api_status[0] + "\n" + api_status[1]
        return (text, status, "")

    mmdd = "(????)"
    yyyymmdd = "(????/??/??)"

    epidemic = TaiwanEpidemic(SSLVerify=SSLVerify)
    global_stats = GlobalStats(SSLVerify=SSLVerify)

    # 手動 > json > 衛福部 > CDC
    # 如果手動模式有開，則直接透過手動模式獲得資料
    if manual is True:
        today = __manual_generate_data(
            article=article, today_dict=today_dict)

    # 若非手動
    else:
        # 預設從 json 讀取資料
        # 如果沒有要重新爬蟲，就從json讀取
        if recrawl is not True:
            today = TodayInfo.from_json()
        else:
            # 創造空的 TodayInfo Object
            today = TodayInfo.create_empty()

        # 若尚未從json取得資料(手動失敗失敗或是是recrawl)，執行取得資料的步驟
        if not today.check_generate_status() and cdc is False:
            logging.info(
                "api.get_taiwan_outbreak_information: TodayInfo.from_json not generated. Starting crawl_from_mohw")
            # 啟動衛福部新聞的爬蟲
            try:
                crawl_from_mohw(today)
            except Exception as e:
                return ("衛福部爬蟲錯誤，請詢問開發者", "crawl_from_mohw(today) " + str(e), "")

            # 爬蟲成功後資料分析
            ArticleAnalyzer().data_extractor(today)

        # 若尚未從json取得資料(衛福部新聞的爬蟲失敗)，執行取得資料的步驟
        if not today.check_generate_status() and mohw is False:
            # 啟動疾管暑新聞爬蟲
            logging.info("api.get_taiwan_outbreak_information: mohw no data. Starting crawl_from_cdc.")
            try:
                crawl_from_cdc(today)
            except Exception as e:
                return ("疾管暑爬蟲錯誤，請詢問開發者", "crawl_from_cdc(today) " + str(e), "")

            # 爬蟲成功後資料分析
            ArticleAnalyzer().data_extractor(today)

    logging.info(f"today: {today}")

    # 有錯誤出現時會 early return
    # 錯誤訊息會回傳至主控
    if today.error is not False and not force:
        text = "無法連上CDC官網或是爬蟲出現錯誤"
        status = ERROR_CDC_WEBPAGE
        return (text, f"ERROR_CDC_WEBPAGE\n{today}", "")

    if not today.is_same_date and not force:
        text = "ERROR: 日期錯誤。本日衛福部新聞稿尚未更新？"
        status = ERROR_NOT_SAME_DATE
        return (text, ERROR_NOT_SAME_DATE + str(today), "")

    # 強制執行，且 today 無法取得時的處理
    if force and (today.error or not today.is_same_date):
        # 製作一個沒有爬蟲的TodayConfirmed object，讓文章的資料被填入None
        today = TodayConfirmed(0)
        yyyymmdd = "ERROR: 無法取得衛福部的新聞稿資訊"

    if today.date is not None:
        mmdd = today.date.strftime("%m%d")
        yyyymmdd = today.date.strftime("%Y/%m/%d")

    death_rate = (int(epidemic.deaths.replace(",", "")) /
                  int(epidemic.confirmed.replace(",", ""))) * 100
    death_rate = "{:.2f}".format(death_rate)

    text = f"""《臺灣疫情資訊站{mmdd}資訊報》

【今日新增】
今日新增：{today.today_confirmed}例（{today.today_domestic}本土,{today.today_imported}境外）
今日死亡：{today.today_deaths}例{today.additional_text}
——————————————————————————
【昨日更新】
昨日送檢：{epidemic.yesterday_reported}件
昨日排除：{epidemic.yesterday_excluded}件
昨日確診：{epidemic.yesterday_confirmed}人
——————————————————————————
【累計統計】
已送檢：{epidemic.reported}人
已排除：{epidemic.excluded}人
已確診：{epidemic.confirmed}人
已死亡：{epidemic.deaths}人
死亡率：{death_rate}%
——————————————————————————
【國際疫情狀況】
全球確診數：{global_stats.confirmed}人
全球死亡病例：{global_stats.deaths}人
全球致死率：{global_stats.cfr}
已有確診病例國家：{global_stats.countries}國
——————————————————————————
統計數字如果有誤，請於群組告知，我們會立刻更正，謝謝。
——————————————————————————
本日資訊取用於：
疾管署新聞稿及政府資料開放平臺
——————————————————————————
-臺灣疫情資訊站
Taiwan Outbreak Information

{yyyymmdd}
"""
    # 能走到這步應該意味著(除了強制以外)已經成功取得資料可以儲存了吧
    if save_to_json:
        today.save_to_json()

    return text, status, today.article_link


def __manual_generate_data(article: str, today_dict: dict):
    logging.info(
        "get_taiwan_outbreak_information(): 手動模式 Manual mode is True, 啟動手動模式 activating manual mode.")
    if article is not None:
        logging.info(
            "get_taiwan_outbreak_information(): 透過文章取得資料 Getting data from article")
        # 透過 article 取得資料（最好要有標題）
        today = TodayInfo.from_article(article=article)
        ArticleAnalyzer.data_extractor(today)
        return today
    elif today_dict is not None:
        # 透過 today dict 取得資料
        logging.info(
            "get_taiwan_outbreak_information(): 透過 today dict 取得資料 Getting data from today_dict")
        today = TodayInfo(
            today_confirmed=today_dict["confirmed"],
            today_domestic=today_dict["domestic"],
            today_imported=today_dict["imported"],
            today_deaths=today_dict["deaths"],
            additional_text=today_dict["additional_text"])
        return today
    else:
        logging.info(
            "get_taiwan_outbreak_information(): 手動模式必須提供文章或本日疫情資訊 Manual mode requires article or today_dict")
        logging.error(
            "get_taiwan_outbreak_information() manual is True, but article and today_dict are both None.")
        return ("手動模式必須提供文章或本日疫情資訊",
                "get_taiwan_outbreak_information() manual is True, but article and today_dict are both None.", "")


def get_epidemic_status_by_country(country: str):
    with requests.Session() as s:
        url = "https://od.cdc.gov.tw/eic/covid19/covid19_global_cases_and_deaths.csv"
        download = s.get(url, verify=False)

        decoded_content = download.content.decode('utf-8')
        csv_file = csv.reader(decoded_content.splitlines(), delimiter=',')

        for row in csv_file:
            # Searched by Chinese
            if country in row[0]:
                print(row)
                text = f"""{row[0]}的疫情狀況：
累積確診數：{row[2]}
累計死亡數：{row[3]}
                """
                return text
            # Searched by English
            if country.lower() in row[1].lower():
                print(row)
                text = f"""Covid19 in {row[1]}:
Confirmed: {row[2]}
Deaths: {row[3]}"""
                return text

        # for fun
        if country.lower() == "today_death_rate" or country.lower() == "todaydeathrate":
            today = TodayConfirmed(CDC_NEWS_URL)
            return "{:.2f}%".format(float(
                int(str(today.today_deaths).replace(",", "")) / int(str(today.today_confirmed).replace(",", "")) * 100))

        if country.lower() == "rate_death_today" or country.lower() == "ratedeathtoday":
            today = TodayConfirmed(CDC_NEWS_URL)
            return "{:.2f}% lol".format(float(
                int(str(today.today_confirmed).replace(",", "")) / int(str(today.today_deaths).replace(",", "")) * 100))
    return None


def get_API_status(SSLVerify=True):
    try:
        url = "https://od.cdc.gov.tw/"
        s = requests.get(url, verify=SSLVerify)
        api_status_dict = s.json()
        return (api_status_dict["state"], "")
    except requests.exceptions.Timeout as e:
        return ("請求超時", str(e))
    except requests.exceptions.SSLError as e:
        return ("SSL錯誤", str(e))
    except Exception as e:
        return (False, str(e))


class TaiwanEpidemic(object):
    """透過政府資料公開API取得台灣統計的疫情資訊"""
    confirmed = None
    deaths = None
    reported = None
    excluded = None
    yesterday_confirmed = None
    yesterday_excluded = None
    yesterday_reported = None

    full_text = None

    def __init__(self, SSLVerify=True):
        with requests.Session() as s:
            url = "https://od.cdc.gov.tw/eic/covid19/covid19_tw_stats.csv"

            download = s.get(url, verify=SSLVerify)

            decoded_content = download.content.decode('utf-8')

            cr = csv.reader(decoded_content.splitlines(), delimiter=',')
            data_list = list(cr)

            # return str(f"總確診數：{data_list[1][0]}")
            self.confirmed = data_list[1][0]
            self.deaths = data_list[1][1]
            self.reported = data_list[1][2]
            self.excluded = data_list[1][3]
            self.yesterday_confirmed = data_list[1][4]
            self.yesterday_excluded = data_list[1][5]
            self.yesterday_reported = data_list[1][6]

            data_list_transpose = list(map(list, zip(*data_list)))
            text = "```\n"
            # t = PrettyTable(data_list[0])
            # t.add_row(data_list[1])
            for row in data_list_transpose:
                for data in row:
                    text += str(data + " ")
                text += "\n"
            # text += str(t)
            text += "```"
            self.full_text = text

    def __str__(self):
        if self.full_text:
            return self.full_text
        else:
            return "ERROR: TaiwanEpidemic init failed"


class GlobalStats(object):
    """透過政府資料公開API取得全球疫情統計資訊"""
    confirmed = None
    deaths = None
    cfr = None
    countries = None

    full_text = None

    def __init__(self, SSLVerify=True):
        with requests.Session() as s:
            url = "https://od.cdc.gov.tw/eic/covid19/covid19_global_stats.csv"

            download = s.get(url, verify=SSLVerify)

            decoded_content = download.content.decode('utf-8')

            cr = csv.reader(decoded_content.splitlines(), delimiter=',')
            data_list = list(cr)

            self.confirmed = data_list[1][0]
            self.deaths = data_list[1][1]
            self.cfr = data_list[1][2]
            self.countries = data_list[1][3]

            data_list_transpose = list(map(list, zip(*data_list)))
            text = "```\n"
            # t = PrettyTable(data_list[0])
            # t.add_row(data_list[1])
            for row in data_list_transpose:
                for data in row:
                    text += str(data + "　")
                text += "\n"
            # text += str(t)
            text += "```"
            # return str(f"總確診數：{data_list[1][0]}")
            self.full_text = text

    def __str__(self):
        if self.full_text:
            return self.full_text
        else:
            return "ERROR: GlobalStats init failed"


def crawl_from_mohw(today: TodayInfo):
    # 創造 crawler 爬蟲物件
    crawler = WebCrawlerMohw()

    crawl(crawler=crawler, today=today)


def crawl_from_cdc(today: TodayInfo):
    # 創造 crawler 爬蟲物件
    crawler = WebCrawlerCDC()

    crawl(crawler=crawler, today=today)


def crawl(crawler: Object, today: TodayInfo):
    # 啟動爬蟲
    # 爬蟲如果出錯會直接用炸的 (raise exception)
    crawler.crawl()

    # 存入資料
    today.article_link = crawler.article_url
    today.article = crawler.article
    today.date = crawler.article_date
    today.article_title = crawler.title

    # 將爬蟲下來的 date string 轉換為 datetime 物件
    today.date_str_to_datetime()


# For testing purpose
if __name__ == '__main__':
    logging.basicConfig(filename="bot_test.log", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        level=logging.INFO)
    test_article = """
中央流行疫情指揮中心今(25)日公布國內新增38例COVID-19確定病例，分別為13例本土個案及25例境外移入；另確診個案中無新增死亡。

指揮中心表示，今日新增本土個案為4例男性、9例女性，年齡介於未滿5歲至70多歲；詳如新聞稿附件。

指揮中心說明，今日新增境外移入個案為8例男性、17例女性，年齡介於10多歲至70多歲，分別自加拿大(5例)、美國、泰國及印度(各3例)、日本(2例)、奈及利亞、瑞典及中國(各1例)移入；另6例調查中。入境日介於今(2022)年1月11日至1月24日；詳如新聞稿附件。

指揮中心統計，截至目前國內累計5,501,288例新型冠狀病毒肺炎相關通報(含5,482,563例排除)，其中18,411例確診，分別為3,429例境外移入，14,928例本土病例，36例敦睦艦隊、3例航空器感染、1例不明及14例調查中；新增3例空號病例(案18216-18218，再次採檢為陰性，改判排除)，累計122例移除為空號。2020年起累計851例COVID-19死亡病例，其中838例本土，個案居住縣市分布為新北市413例、臺北市322例、基隆市29例、桃園市27例、彰化縣15例、新竹縣13例、臺中市5例、苗栗縣3例、宜蘭縣及花蓮縣各2例，新竹市、南投縣、雲林縣、臺南市、高雄市、屏東縣及臺東縣各1例；另13例為境外移入。

指揮中心再次呼籲，民眾應落實手部衛生、咳嗽禮節及佩戴口罩等個人防護措施，減少不必要移動、活動或集會，避免出入人多擁擠的場所，或高感染傳播風險場域，並主動積極配合各項防疫措施，共同嚴守社區防線。
    """
    list = get_taiwan_outbreak_information(recrawl=True)
    print(*list, sep="\n")
