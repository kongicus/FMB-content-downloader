import time
import random
from bs4 import BeautifulSoup
import requests
import datetime
import os
import logging


logger = logging.getLogger(__name__)


ENCODING = None


# Fetch the webpage, re-encode it using 'euc-jp', and pass it to BeautifulSoup.
def get_webpage_encoding_soup(weblink):
    global ENCODING

    # send a GET request to fetch the webpage of list
    response = requests.get(weblink)

    if ENCODING is None:
        ENCODING = response.apparent_encoding
    response.encoding = ENCODING

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
            # Get the string representation of the href attribute, which is the URL for each month.
            href_str = str(child["href"])

            # Use slicing to get the substring from the second-to-last '/' character to the end
            # In the string href_str, the numeric part is before the last '/' character. You can use slicing to get the substring from the second-to-last '/' character to the end, and then use the .split('/') method to split it, and get the second-to-last element, which is the numeric part.
            month_str = href_str.split('/')[-1].split('.')[0]
            month = datetime.datetime.strptime(month_str, "%Y%m")

            # Filter out the URLs of the text content for dates after the input date
            if month.year > start_month.year or (month.year == start_month.year and month.month >= start_month.month):
                # Store the href string as the value, with the key as the key-value pair, in the dictionary
                links_dict[month_str] = href_str

    return links_dict


def save_text(start_date: str, path: str):
    if not os.path.exists(path):
        logger.info(f"creating download dir {path}")
        os.makedirs(path, exist_ok=True)
    # e.g. start_date: 20240101

    start_date = datetime.datetime.strptime(start_date, "%Y%m%d")

    logger.info("getting page index")
    links_dict = get_links_dict(start_date)

    for value in links_dict.values():
        # Generate a random interval between 3 and 6 seconds
        interval = random.uniform(3, 5)
        # Wait for the random interval
        time.sleep(interval)

        one_month_soup = get_webpage_encoding_soup(value)

        # Find all <a> tags containing the text "続きを読む"
        days_links = one_month_soup.find_all("a", string="続きを読む")

        # Extract the href attributes of these <a> tags and save them to the days_links_list array
        days_links_list = []
        for day_link in days_links:
            days_links_list.append(day_link["href"])

        for day_web_link in days_links_list:
            fmb_day_soup = get_webpage_encoding_soup(day_web_link)
            
            # Get the date
            # Find the <td> element containing the date information, the first one is enough
            tds = fmb_day_soup.find("td", align="right")

            # Find the <font> element and check its color and size attributes
            font_element = tds.find("font", color="Gray", size="2")

            # Get the text content inside the <font> element
            date_content = font_element.get_text(strip=True)

            # Extract the date information and convert its format
            date_info = date_content.replace("/", "")

            # Get the issue number
            # Find the <font> element containing the numbers
            font_issue_number_element = fmb_day_soup.find("font", attrs={"color": "#6e8f99", "size": "2"})

            # Find the <font> element that meets the condition
            issue_number_info = font_issue_number_element.text.strip('#＃')

            # Find the <table> element that meets the condition
            table_text_element = fmb_day_soup.find("table", cellpadding="5", width="100%", border="0")

            # Get the FMB text content inside the <table> element
            text_content = table_text_element.find("font").get_text(separator="\n")

            # If the folder does not exist, create it
            if not os.path.exists(path):
                os.makedirs(path)
            
            # File name, e.g., 20240101_790
            file_name = f'{date_info}_{issue_number_info}'
            
            # Concatenate the complete path of the file
            file_path = os.path.join(path, f'{file_name}.txt')

            # Write the text content into the file
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(text_content)

            logger.info(f'save as {file_name}.txt')
