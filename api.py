import requests
import csv
from datetime import datetime
import pytz
import web_crawler

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

def get_taiwan_outbreak_information():
    # today = datetime.now(pytz.timezone('Asia/Taipei'))

    epidemic = TaiwanEpidemic()
    global_stats = GlobalStats()
    today = web_crawler.TodayConfirmed()

    mmdd = today.date.strftime("%m%d")
    yyyymmdd = today.date.strftime("%Y/%m/%d")

    total_tests_conducted = "4,070,641"


    text = f"""《臺灣疫情資訊站{mmdd}資訊報》

【目前資訊】
已送檢：{epidemic.reported}人
已排除：{epidemic.excluded}人
已確診：{epidemic.confirmed}人
已死亡：{epidemic.deaths}人
今日新增：{today.today_confirmed}例（{today.today_imported}境外,{today.today_domestic}本土）
今日死亡：{today.today_deaths}例
——————————————————————————
【昨日更新】
昨日送檢：{epidemic.yesterday_reported}件
昨日排除：{epidemic.yesterday_excluded}件
昨日確診：{epidemic.yesterday_confirmed}人{today.additional_text}
——————————————————————————
【國際疫情狀況】
全球確診數：{global_stats.confirmed}人
全球死亡病例：{global_stats.deaths}人
全球致死率：{global_stats.cfr}
已有確診病例國家：{global_stats.countries}國
——————————————————————————
統計數字如果有誤，請於[群組](https://t.me/joinchat/VXSevGfKN560hTWH)告知，我們會立刻更正，謝謝。
——————————————————————————
本日資訊取用於：
疾管署及政府資料開放平臺
——————————————————————————
-臺灣疫情資訊站
Taiwan Outbreak Information

{yyyymmdd}
"""
    return (text, today.is_same_date)

def get_epidemic_status_by_country(country: str):
    return False

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

    def __init__(self):
        with requests.Session() as s:
            url = "https://od.cdc.gov.tw/eic/covid19/covid19_tw_stats.csv"

            download = s.get(url)

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

    def __init__(self):
        with requests.Session() as s:
            url = "https://od.cdc.gov.tw/eic/covid19/covid19_global_stats.csv"

            download = s.get(url)

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
    text = get_taiwan_outbreak_information()
    print(text[0])
