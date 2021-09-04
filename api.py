#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import csv
import json
from datetime import datetime
import pytz
import web_crawler
from requests.packages import urllib3
import pic

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

    today = web_crawler.TodayConfirmed(CDC_NEWS_URL, SSLVerify=isSSLVerify)

    if today.error is not False and not isForce:
        text = "無法連上CDC官網"
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
    text = get_taiwan_outbreak_information("")
    for t in text:
        print(str(t)+"\n")
    #pic.pic("0904", "1", "0", "1", "0", "16013", "837")
