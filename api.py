#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import csv
import json
from datetime import datetime
import pytz
import web_crawler
from requests.packages import urllib3
#import pic

import certifi

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
                text += str(data+"　")
            text += "\n"
        #text += str(t)
        text += "```"
        # return str(f"總確診數：{data_list[1][0]}")
        print(text)
        return text
    return False

def get_taiwan_outbreak_information(*arg: str):
    '''
    產生回傳臺灣疫情資訊站的標準格式文章。

        Arguments:
            force: 跳過衛福部官網的爬蟲，產生其他API提供的資料
            IgnoreSSL: 忽略SSL安全性認證

        Returns:
            text (str): 臺灣疫情資訊站的標準格式文章或用戶可讀的錯誤訊息
            status (str): 狀態訊息以及debug用錯誤訊息，回傳"0"表示成功
            today.article_link (str): 文章連結
    '''

    # force 只能通過CDC，如果API接不到一樣會出現錯誤
    print(f"args:{arg}")

    force_texts = ["force", "f", "-f", "-force"]
    if any(x in force_texts for x in arg):
        print("Force mode")
        isForce = True
    else:
        isForce = False

    ignoressl_texts = ["IgnoreSSL", "ignoressl", "ignoreSSL", "Ignoressl"]
    if any(x in ignoressl_texts for x in arg):
        print("IgnoreSSL")
        isSSLVerify = False
    else:
        isSSLVerify = True

    manual_texts = ["manual", "manual"]
    if any(x in manual_texts for x in arg):
        print("ismanual")
        ismanual = True
        article = arg[0]
    else:
        ismanual = False
        article = None

    if "save" in arg:
        print("save to json in manual mode")
        save_to_json_in_maual_mode = True
    else:
        save_to_json_in_maual_mode = False

    isrecrawl = ("recrawl" in arg)

    api_status = get_API_status(isSSLVerify)

    if not api_status[0]:
        text = "ERROR: 網路錯誤\n" + api_status[0]
        status = ERROR_INTERNET_CONNECTION + "\nUnable to get status from Taiwan CDC Open Data Service\n" + api_status[0] + "\n" + api_status[1]
        return (text, status, "")
    elif api_status[0] == "success":
        print("Taiwan CDC Open Data Service, connection succeed.")
        status = 0
    else:
        text = "ERROR: 政府資料開放平台無法連接\n訊息：" + api_status[0]
        status = ERROR_OPEN_DATA_SERVICE + "\n訊息：" + api_status[0] + "\n" + api_status[1]
        return (text, status, "")

    mmdd = "(????)"
    yyyymmdd = "(????/??/??)"

    epidemic = TaiwanEpidemic(SSLVerify=isSSLVerify)
    global_stats = GlobalStats(SSLVerify=isSSLVerify)

    today = web_crawler.TodayConfirmed(CDC_NEWS_URL, SSLVerify=isSSLVerify, recrawl = isrecrawl, ismanual = ismanual, article = article, save = save_to_json_in_maual_mode)

    if today.error is not False and not isForce:
        text = "無法連上CDC官網或是爬蟲出現錯誤"
        status = ERROR_CDC_WEBPAGE
        return (text, f"ERROR_CDC_WEBPAGE\n{today.error}", "")

    if not today.is_same_date and not isForce:
        text = "ERROR: 日期錯誤。本日衛福部新聞稿尚未更新？"
        status = ERROR_NOT_SAME_DATE
        return (text, ERROR_NOT_SAME_DATE + str(today.date), "")

    # 強制執行，且 today 無法取得時的處理
    if isForce and (today.error or not today.is_same_date):
        # 製作一個沒有爬蟲的TodayConfirmed object，讓文章的資料被填入None
        today = web_crawler.TodayConfirmed(0)
        yyyymmdd = "ERROR: 無法取得衛福部的新聞稿資訊"

    if today.date is not None:
        mmdd = today.date.strftime("%m%d")
        yyyymmdd = today.date.strftime("%Y/%m/%d")

    death_rate = (int(epidemic.deaths.replace(",", "")) / int(epidemic.confirmed.replace(",", ""))) * 100
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
    return (text, status, today.article_link)

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
            today = web_crawler.TodayConfirmed(CDC_NEWS_URL)
            return "{:.2f}%".format(float(int(str(today.today_deaths).replace(",", "")) / int(str(today.today_confirmed).replace(",", "")) * 100))


        if country.lower() == "rate_death_today" or country.lower() == "ratedeathtoday":
            today = web_crawler.TodayConfirmed(CDC_NEWS_URL)
            return "{:.2f}% lol".format(float(int(str(today.today_confirmed).replace(",", "")) / int(str(today.today_deaths).replace(",", "")) * 100))
    return None

def get_API_status(SSLVerify = True):
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
    """docstring for TaiwanEpidemic."""
    confirmed = None
    deaths = None
    reported = None
    excluded = None
    yesterday_confirmed = None
    yesterday_excluded = None
    yesterday_reported = None

    full_text = None

    def __init__(self, SSLVerify = True):
        with requests.Session() as s:
            url = "https://od.cdc.gov.tw/eic/covid19/covid19_tw_stats.csv"

            download = s.get(url, verify = SSLVerify)

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
                    text += str(data+"　")
                text += "\n"
            #text += str(t)
            text += "```"
            self.full_text = text

    def __str__(self):
        if self.full_text:
            return self.full_text
        else:
            return "ERROR: TaiwanEpidemic init failed"

class GlobalStats(object):
    confirmed = None
    deaths = None
    cfr = None
    countries = None

    full_text = None

    def __init__(self, SSLVerify = True):
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
                    text += str(data+"　")
                text += "\n"
            #text += str(t)
            text += "```"
            # return str(f"總確診數：{data_list[1][0]}")
            self.full_text = text

    def __str__(self):
        if self.full_text:
            return self.full_text
        else:
            return "ERROR: GlobalStats init failed"


if __name__ == '__main__':
    # t=get_epidemic_status_by_country("Canada")
    # print(t)
    s = """
    新增5例境外移入COVID-19確定病例
  資料來源：疾病管制署
  建檔日期：110-10-01
  更新時間：110-10-01
中央流行疫情指揮中心今(6)日公佈國內新增5例COVID-19確定病例，均為境外移入；另確診個案中無新增死亡。

指揮中心說明，今日新增5例境外移入個案，為1例男性、4例女性，年齡介於20多歲至40多歲，其中4例分別自美國(3例，案16373、案16374、案16376)、南非(案16375)入境，餘1例調查中(案16377)，入境日介於今(2021)年9月14日至9月26日；詳如新聞稿附件。

指揮中心統計，截至目前國內累計3,507,972例新型冠狀病毒肺炎相關通報(含3,490,728例排除)，其中16,267例確診，分別為1,632例境外移入，14,581例本土病例，36例敦睦艦隊、3例航空器感染、1例不明及14例調查中；另累計110例移除為空號。2020年起累計844例COVID-19死亡病例，其中832例本土，個案居住縣市分佈為新北市412例、臺北市319例、基隆市29例、桃園市26例、彰化縣15例、新竹縣13例、臺中市5例、苗栗縣3例、宜蘭縣及花蓮縣各2例，臺東縣、雲林縣、臺南市、南投縣、高雄市及屏東縣各1例；另12例為境外移入。

指揮中心再次呼籲，民眾應落實手部衛生、咳嗽禮節及佩戴口罩等個人防護措施，減少不必要移動、活動或集會，避免出入人多擁擠的場所，或高感染傳播風險場域，並主動積極配合各項防疫措施，共同嚴守社區防線。
"""
    text = get_taiwan_outbreak_information("manual", s)
    for t in text:
        print(str(t)+"\n")
    #pic.pic("0904", "1", "0", "1", "0", "16013", "837")
