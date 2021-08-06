import requests
import csv

def api(url):
    """docstring for api."""

    with requests.Session() as s:
        download = s.get(url)

        decoded_content = download.content.decode('utf-8')

        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        my_list = list(cr)
        for row in my_list:
            print(row)

        print(f"確診數：{my_list[1][0]}")


if __name__ == '__main__':
    api_url = "https://od.cdc.gov.tw/eic/covid19/covid19_tw_stats.csv"
    api(api_url)
