import re
import os
import csv
import json
import requests
from urllib import parse
from bs4 import BeautifulSoup
from locals.output_data import exportData
from locals.date_scrape import getDate, lastStamp, searchDate
from locals.automate import By, Keys, EC, Action, wait_for, genBrowser, driverWait


# setting up user agent

header_1 = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0'
}

header_2 = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}

header_3 = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/114.0'
}

header_4 = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 OPR/100.0.0.0'
}


def get_data(html, data_list, base_url):
    soup = BeautifulSoup(html, 'lxml')
    page_content = soup.select_one('section.content')

    category = page_content.select_one('div.head span[itemprop="name"]').string
    topic_name = page_content.select_one('div.showthread__title h1').get_text(strip=True)

    posts = page_content.select('div#posts div.showthread')

    for post in posts:
        try:
            time_n_date = post.select_one('div.threadpost-header__controls li.threadpost-header__controllink--nolink span.visible-mv').get_text(strip=True)
        except:
            exc_time_tag = post.select_one('div.threadpost-header__controls li.threadpost-header__controllink--nolink span.visible-mv')
            print('\n')
            print(exc_time_tag)
            print('\n')
            continue

        has_files = post.select_one('div.threadpost-content div.threadpost-content__attachments')
        if has_files:
            post_details_tag = post.select_one('div.threadpost-header div.threadpost-header__controls a[title="Post Permalink"]')
            post_url = parse.urljoin(base_url, post_details_tag['href'])
            post_count = post_details_tag['data-postnum']
            
            attach_files = has_files.select('div.attachinfo')

            for file in attach_files:
                file_url = parse.urljoin(base_url, file.a['href'])
                file_name = file.a.string
                try:
                    ext_pattern = r"\b(?:zip|rar|ex4|mq4|ex5|mq5|tpl|MQ5|MQ4|EX4|ZIP|RAR|EX5|TPL)\b"
                    extension = re.search(ext_pattern, file_name).group()
                    file_name_only = file_name.replace(extension, '').replace('.', '')
                except:
                    # print(f"\n{file_name}\n")
                    continue

                info_text = file.select_one('span.info').get_text(strip=True)
                download_text = re.search(r"\b\|[0-9\,]+\sdownloads\b", info_text).group()
                downloads = download_text.replace('|', '').replace('downloads', '').replace(',', '').strip()

                data_dict = {
                    "name": file_name_only,
                    "format": extension,
                    "download_url": file_url,
                    "downloads": downloads,
                    "date_text": time_n_date,
                    "topic_name": topic_name,
                    "category": category,
                    "post_url": post_url,
                    "post#": post_count
                }

                data_list.append(data_dict)
                # print(data_dict)     
        else:
            continue



# data to be collected
def main():
    error_url_list = []
    data_list = []

    session = requests.Session()
    pages = [page for page in range(1, 85)]

    for page in pages:
        print(f"crawling page: {page}")
        base_url = 'https://www.forexfactory.com'
        extend_url = f'/thread/594890-indicator-bank?page={page}'
        target_url = parse.urljoin(base_url, extend_url)

        res = session.get(target_url, headers=header_1)

        if res.status_code == 200:
            html = res.text
            
            try:
                get_data(html, data_list, base_url)
            except:
                break
        else:
            print(f'Bad Response- {res.status_code}')
            error_url_list.append(target_url)
    
    return (error_url_list, data_list)



if __name__ == "__main__":
    error_list, data_list = main()
    exportData('forex_factory', data_list)
    print(error_list)

