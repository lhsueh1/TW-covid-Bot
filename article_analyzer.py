import logging
import re
import datetime

from my_exception import MyException
from web_crawler import TodayInfo


class ArticleAnalyzer():
    """
    文章分析器
    Attributes
    ----------

    Methods
    -------
    data_extractor(today: TodayInfo)
        從 today.article 分析出確診數等資訊，直接將資料改在 object 中
    __extract_number(regex: str, text: str)
        內部 function，將文字中符合 regex 的數值取出
    date_compare()
        將文章發布日期與今日比較
    """
    @staticmethod
    def data_extractor(today: TodayInfo):

        # to check today.article available
        if today.article is None or today.article == "":
            MyException("ArticleAnalyzer: today.article is empty")
        today.error = False
        logging.info("ArticleAnalyzer: extracting info from today.article")

        if today.article_title is None:
            today.article_title = today.article.split('\n', 1)[0]

        texts = filter(ArticleAnalyzer.__unwanted_text, today.article.split())

        today.article = "\n".join(texts)

        # 文章標題的確診病例、本土、境外處理
        if re.search(r'新增\d+例COVID-19\w{0,2}病例，分別為\d+例本土\w{0,2}及\d+例境外', today.article_title):
            nums = re.findall(r'\d+', today.article_title)
            today.today_confirmed = int(nums[0])
            today.today_domestic = int(nums[2])
            today.today_imported = int(nums[3])

        elif re.search(r'新增\d+例境外\w*移入COVID-19\w*病例', today.article_title):
            nums = re.findall(r'\d+', today.article_title)
            today.today_confirmed = int(nums[0])
            today.today_domestic = 0
            today.today_imported = int(nums[0])

        # 如果標題找不到境外移入、本土的病例數量的話，透過文章分析
        # 利用today.article_title找到 新增\d+例境外移入 並判斷本土數量
        elif re.search(r'新增\d+例COVID-19\w*病例', today.article_title):
            today.today_confirmed = ArticleAnalyzer.__extract_number(
                r'新增\d+例COVID-19\w*病例', today.article_title)

            today.today_imported = ArticleAnalyzer.__extract_number(
                r'新增\w?\d+例境外', today.article)
            today.today_domestic = ArticleAnalyzer.__extract_number(
                r'新增\w?\d+例本土', today.article)

            if today.today_domestic is None and today.today_confirmed is not None and today.today_imported is not None:
                today.today_domestic = int(
                    today.today_confirmed) - int(today.today_imported)

            if today.today_imported is None and today.today_confirmed is not None and today.today_domestic is not None:
                today.today_imported = int(
                    today.today_confirmed) - int(today.today_domestic)
        else:
            # 如果標題完全找不到就只能從文章找
            today.today_confirmed = ArticleAnalyzer.__extract_number(
                r'新增\d+例COVID-19\w*病例', today.article)
            today.today_imported = ArticleAnalyzer.__extract_number(
                r'\w?\d+例境外', today.article)
            today.today_domestic = ArticleAnalyzer.__extract_number(
                r'\w?\d+例本土', today.article)

            # 抓日期
            date_text_match = re.search(
                r'\d{3,4}[-/]\d{1,2}[-/]\d{1,2}', today.article)
            if date_text_match is not None:
                date_text = re.findall(r'\d+', date_text_match.group(0))
                date_year = int(date_text[0])

                # 中華民國還沒死透
                if date_year < 2000:
                    date_year = date_year + 1911

                date_month = int(date_text[1])

                date_day = int(date_text[2])
                today.date = datetime.date(date_year, date_month, date_day)
            else:
                today.date = datetime.date.today()

        # 如果境內確診沒有值，而總確診跟境外移入有值，則計算境內確診
        if today.today_domestic is None and today.today_confirmed is not None and today.today_imported is not None:
            today.today_domestic = int(
                today.today_confirmed) - int(today.today_imported)

        # 如果境外確診沒有值，而總確診跟境內有值，則計算境外確診
        if today.today_imported is None and today.today_confirmed is not None and today.today_domestic is not None:
            today.today_imported = int(
                today.today_confirmed) - int(today.today_domestic)

        # 死亡分析
        regex_death = re.compile(r"新增(\d+-*\d*)例死亡")
        match_death = regex_death.search(today.article)
        if match_death is not None:
            today.today_deaths = match_death.group(1)

        if re.search(r"無新增死亡", today.article):
            today.today_deaths = 0

        if today.today_confirmed is None or today.today_domestic is None or today.today_imported is None or today.today_deaths is None:
            today.error = f"""
本日數據包含None
today_confirmed = {today.today_confirmed}
today_imported = {today.today_imported}
today_domestic = {today.today_domestic}
today_deaths = {today.today_deaths}
"""
            return

        today.additional_text = ArticleAnalyzer.__additional_text_handler(
            today.article)

        # 因應文章格式加入換行
        if today.additional_text is not None and today.additional_text != "":
            today.additional_text = "\n" + today.additional_text

            # 刪除多餘的換行
            # only remove trailing newline characters.
            today.additional_text = today.additional_text.rstrip()

        today.check_generate_status()

    @staticmethod
    def __additional_text_handler(article: str):
        texts = article.split()[1:]

        # ref https://www.runoob.com/python/python-func-filter.html
        texts = filter(ArticleAnalyzer.__wanted_addtional_text, texts)

        additional_text = "".join(texts)

        # Without using loops:
        # * symbol is use to print the list elements in a single line with space.
        # To print all elements in new lines or separated by space use sep=”\n” or sep=”, ” respectively.
        # print(*list(test_text), sep="\n")
        # ref: https://www.geeksforgeeks.org/print-lists-in-python-4-different-ways/

        additional_text = additional_text.replace("；", "。\n")
        additional_text = additional_text.replace("指揮中心表示，", "")
        additional_text = additional_text.replace("指揮中心說明，", "")
        additional_text = additional_text.replace("指揮中心指出，", "")
        additional_text = additional_text.replace("，個案分佈", "\n個案分佈")
        additional_text = additional_text.replace("，個案分布", "。\n個案分布")
        additional_text = additional_text.replace("，將持續進行疫情調查，以釐清感染源", "")
        additional_text = additional_text.replace("，衛生單位刻正進行相關疫調及接觸者匡列", "")
        additional_text = additional_text.replace(
            "。衛生單位將持續進行疫情調查及防治，以釐清感染源", "")
        additional_text = additional_text.replace(
            "，衛生單位將持續進行疫情調查及防治，以釐清感染源", "")
        additional_text = additional_text.replace("將持續進行疫情調查及防治，以釐清感染源。", "")
        additional_text = additional_text.replace(
            "衛生單位持續進行疫情調查及防治，接觸者匡列中。", "")
        additional_text = additional_text.replace("詳如新聞稿附件。", "")
        return additional_text

    def __wanted_addtional_text(paragraph: str):

        if re.search(r'指揮中心\w{2}，*\w{0,4}新增\w{2,10}(\(案\d+\))*，*為', paragraph):
            return paragraph
        else:
            return None

    def __unwanted_text(paragraph: str):
        if re.search(r"敦睦艦隊", paragraph):
            return None
        else:
            return paragraph

    @staticmethod
    def __extract_number(regex: str, text: str):
        text_matched = re.search(regex, text)
        if text_matched is not None:
            num_match = re.search(r'\d+', text_matched.group(0))
            return int(num_match.group(0))
        return None
