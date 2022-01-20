import re
import datetime
#from web_crawler import TodayInfo


class ArticleAnalyzer():
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

            self.today_imported = self.extract_number(r'新增\w?\d+例境外', article_content)
            self.today_domestic = self.extract_number(r'新增\w?\d+例本土', article_content)

            if self.today_domestic is None and self.today_confirmed is not None and self.today_imported is not None:
                self.today_domestic = int(self.today_confirmed) - int(self.today_imported)

            if self.today_imported is None and self.today_confirmed is not None and self.today_domestic is not None:
                self.today_imported = int(self.today_confirmed) - int(self.today_domestic)

        # 如果不是透過爬蟲取得的文章，就不會有標題，故透過文章分析資料，並分析日期
        if title == "":
            self.today_confirmed = self.extract_number(r'新增\d+例COVID-19\w*病例', article_content)
            self.today_imported = self.extract_number(r'新增\w?\d+例境外', article_content)
            self.today_domestic = self.extract_number(r'新增\w?\d+例本土', article_content)

            if self.today_domestic is None and self.today_confirmed is not None and self.today_imported is not None:
                self.today_domestic = int(self.today_confirmed) - int(self.today_imported)

            if self.today_imported is None and self.today_confirmed is not None and self.today_domestic is not None:
                self.today_imported = int(self.today_confirmed) - int(self.today_domestic)

            # 抓日期
            date_text_match = re.search(r'\d{3,4}[-/]\d{1,2}[-/]\d{1,2}', article_content)
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

        self.additional_text = texts[1]
        self.additional_text = self.additional_text.replace("；", "。\n")
        self.additional_text = self.additional_text.replace("指揮中心表示，", "")
        self.additional_text = self.additional_text.replace("指揮中心說明，", "")
        self.additional_text = self.additional_text.replace("，個案分佈", "\n個案分佈")
        self.additional_text = self.additional_text.replace("，個案分布", "。\n個案分布")
        self.additional_text = self.additional_text.replace("，將持續進行疫情調查，以釐清感染源", "")
        self.additional_text = self.additional_text.replace("，衛生單位刻正進行相關疫調及接觸者匡列", "")
        self.additional_text = self.additional_text.replace("。衛生單位將持續進行疫情調查及防治，以釐清感染源", "")
        self.additional_text = self.additional_text.replace("，衛生單位將持續進行疫情調查及防治，以釐清感染源", "")
        self.additional_text = self.additional_text.replace("將持續進行疫情調查及防治，以釐清感染源。", "")
        self.additional_text = self.additional_text.replace("衛生單位持續進行疫情調查及防治，接觸者匡列中。", "")
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


    @staticmethod
    def date_compare(article_date):
        """如果新聞稿發布日期<今日日期-12小時，會發出錯誤"""

        d2 = datetime.date.today()
        if article_date < d2:
            print(f"日期錯誤:{article_date}")
            return False
        else:
            return True