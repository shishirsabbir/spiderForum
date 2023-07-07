import re
import os
import csv
import json
import time
import httpx
import asyncio
import requests
from urllib import parse
from bs4 import BeautifulSoup
from library.output_data import exportData


# get url function
category_url = input('Enter the category URL: ')

# header list
header_list = [
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0'},
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'},
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/114.0'},
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 OPR/100.0.0.0'},
    {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}
]

active_header = header_list[0]



# get url crawler fast function
async def get_url(category_url, header):
    res = httpx.get(category_url, headers=header)
    parsed_url = parse.urlparse(category_url)

    if res.status_code == 200:
        soup = BeautifulSoup(res.text, 'lxml')
        page_num_tag = soup.select_one('div.forumdisplay__footer li.visible-mv a.last')
        page_num = page_num_tag.string
        # url_path = page_num_tag['href'] # url path is not needed
        query_list = [f"sort=lastpost&order=desc&page={page}" for page in range(1, int(page_num) + 1)]
        url_list = []
        # generating all the urls

        for custom_query in query_list:
            thread_page_url = parsed_url._replace(query=custom_query).geturl()
            # print(thread_page_url)
            url_list.append(thread_page_url)

        
        return url_list
    else:
        print('got error')


asyncio.run(get_url(category_url, active_header))