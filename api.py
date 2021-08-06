import requests
import csv
from prettytable import PrettyTable
import numpy as np

def api(url):
    """docstring for api."""

    with requests.Session() as s:
        download = s.get(url)

        decoded_content = download.content.decode('utf-8')

        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        data_list = list(cr)
        arr = np.array(data_list)
        arr = arr.transpose()
        data_list = arr.tolist()
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


if __name__ == '__main__':
    api_url = "https://od.cdc.gov.tw/eic/covid19/covid19_tw_stats.csv"
    api(api_url)
