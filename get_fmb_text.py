import time
import random
from bs4 import BeautifulSoup
import requests
import datetime
import os

# Fetch the webpage, re-encode it using 'euc-jp', and pass it to BeautifulSoup.
def get_webpage_encoding_soup(weblink):
    # send a GET request to fetch the webpage of list
    response = requests.get(weblink)
    response.encoding = response.apparent_encoding

    # parse the HTML using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

def get_links_dict(start_month):
    index_link = 'http://www6.airnet.ne.jp/kosaka/kinki/radio/ongakuhon/sfs6_diary/sfs6_diary/'

    index_link_soup = get_webpage_encoding_soup(index_link)

    # Find the <a name="lists"> element.
    # Locate the tag with the name "lists".
    list_element = index_link_soup.find("a", {"name": "lists"})

    # # Save the HTML as a backup HTML file.
    # with open('fmb_index_list.html', 'w', encoding='utf-8') as file:
    #     file.write(index_link_soup.prettify())

    # Initialize the result dictionary.
    links_dict = {}

    for child in list_element.descendants:
        if child.name == "a" and child.has_attr("href"):
            # 获取 href 属性的字符串形式，即为获取每月网址
            href_str = str(child["href"])

            # 使用切片操作获取从倒数第二个 '/' 字符到结尾的子字符串
            # 在 href_str 这个字符串中，数字部分位于最后的 / 字符之前。你可以使用切片来获取从倒数第二个 / 字符到结尾的子字符串，然后使用 .split('/') 方法将其拆分，并获取倒数第二个元素，即数字部分。
            month_str = href_str.split('/')[-1].split('.')[0]
            month = datetime.datetime.strptime(month_str, "%Y%m")

            if month.year > start_month.year or (month.year == start_month.year and month.month >= start_month.month):
                # 将 href 字符串作为值，以键作为键存储到字典中
                links_dict[month_str] = href_str

    return links_dict

def save_text(start_date: str, path: str):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    # e.g. start_date: 20240101

    start_date = datetime.datetime.strptime(start_date, "%Y%m%d")
    links_dict = get_links_dict(start_date)

    for value in links_dict.values():
        # 生成 3 到 6 秒之间的随机间隔时间
        interval = random.uniform(3, 5)
        # 等待随机间隔时间
        time.sleep(interval)

        one_month_soup = get_webpage_encoding_soup(value)

        # 找到所有包含 "続きを読む" 文字的 <a> 标签
        days_links = one_month_soup.find_all("a", string="続きを読む")

        # 提取这些 <a> 标签的 href 属性，保存到 days_links_list 数组中
        days_links_list = []
        for day_link in days_links:
            days_links_list.append(day_link["href"])

        for day_web_link in days_links_list:
            fmb_day_soup = get_webpage_encoding_soup(day_web_link)
            
            # 获取日期
            # 找到包含日期信息的 <td> 元素，找第一个就可以
            tds = fmb_day_soup.find("td", align="right")

            # 找到 <font> 元素，并检查其 color 和 size 属性
            font_element = tds.find("font", color="Gray", size="2")

            # 获取 <font> 元素内部的文本内容
            date_content = font_element.get_text(strip=True)

            # 提取日期信息，转换格式
            date_info = date_content.replace("/", "")

            # 获取期数
            # 找到包含数字的 <font> 元素
            font_issue_number_element = fmb_day_soup.find("font", attrs={"color": "#6e8f99", "size": "2"})

            # 如果找到了符合条件的 <font> 元素
            issue_number_info = font_issue_number_element.text.strip('#＃')

            # 找到满足条件的 <table> 元素
            table_text_element = fmb_day_soup.find("table", cellpadding="5", width="100%", border="0")

            # 获取 <table> 元素内部的特定文本内容
            text_content = table_text_element.find("font").get_text(separator="\n")

            # 如果文件夹不存在，则创建它
            if not os.path.exists(path):
                os.makedirs(path)
            
            # 文件名 e.g. 20240101_790
            file_name = f'{date_info}_{issue_number_info}'
            
            # 拼接文件的完整路径
            file_path = os.path.join(path, f'{file_name}.txt')

            # 将文本内容写入文件
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(text_content)

            print(f'save as {file_name}.txt')