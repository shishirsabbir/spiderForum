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



# header list
header_list = [
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0'},
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'},
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/114.0'},
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 OPR/100.0.0.0'},
    {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}
]

active_header = header_list[0]



# all user inputs here
file_name = input('Enter the file name: ')
category_url = input('Enter the category URL: ')


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
        print(f"Bad Response: {res.status_code}")
        print(f"Got error from page {res.url}")



# get html function
async def get_html(client, url, header):
        
        res = await client.get(url, headers=header)
        
        if res.status_code == 200:
            return {"result": res.status_code, "url": res.url, "html_string": res.text}
        else:
            return {"result": res.status_code, "url": res.url, "html_string": None}
        


# running the main spider in concurrent mode
async def fast_spider(header):
    async with httpx.AsyncClient(timeout=None) as client:
        tasks = []

        # generating the url_list
        url_list = await get_url(category_url, header)

        for url in url_list:
            tasks.append(asyncio.ensure_future(get_html(client, url, header)))

        # printing the number of requests
        print(f"total number of request send: {len(url_list)}")

        # waiting to collect all the response
        async_response = await asyncio.gather(*tasks)

        # getting the thead_list data

        thread_url_list = []

        for response in async_response:
            if response['result'] == 200:
                soup = BeautifulSoup(response['html_string'], 'lxml')
                thread_tags = soup.select('table#threadslist tr.threadlist__row div.threadlist__title-wrapper')

                for thread in thread_tags:
                    thread_name = thread.get_text(strip=True)
                    thread_url = thread.a['href']

                    thread_dict = {
                        "thread_name": thread_name,
                        "thread_url": thread_url
                    }

                    thread_url_list.append(thread_dict)

        
        return thread_url_list



# running the concurrent
start_time = time.perf_counter()
data_list = asyncio.run(fast_spider(active_header)) # running the crawler
stop_time = time.perf_counter()

print(f"total time took: {stop_time - start_time}")
print(f"threads found: {len(data_list)}")


# exporting the data
exportData(file_name, data_list)