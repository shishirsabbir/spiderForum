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



# get url crawler fast function
async def get_url(thread_url, header):
    res = httpx.get(thread_url, headers=header)
    parsed_url = parse.urlparse(thread_url)

    if res.status_code == 200:
        soup = BeautifulSoup(res.text, 'lxml')
        page_num_tag = soup.select_one('div.forumdisplay__footer li.visible-mv a.last')
        page_num = page_num_tag.string
        # url_path = page_num_tag['href'] # url path is not needed
        query_list = [f"page={page}" for page in range(1, int(page_num) + 1)]
        url_list = []
        # generating all the urls

        for custom_query in query_list:
            post_url = parsed_url._replace(query=custom_query).geturl()
            # print(post_url)
            url_list.append(post_url)

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
async def fast_spider(header, thread_url):
    async with httpx.AsyncClient(timeout=None) as client:
        tasks = []

        # generating the url_list
        url_list = await get_url(thread_url, header)

        for url in url_list:
            tasks.append(asyncio.ensure_future(get_html(client, url, header)))

        # printing the number of requests
        print(f"total number of request send: {len(url_list)}")

        # waiting to collect all the response
        async_response = await asyncio.gather(*tasks)

        # getting the list data
        html_list = []
        error_response_list = []

        for response in async_response:
            if response['result'] == 200:
                html_list.append(response['html_string'])
            else:
                error_response_list.append(response)

        
        print(f"total html_string collected: {len(html_list)}")
        return html_list





# reading files from local directory
# file_path: data/json/interactive_trading.json,
# file_path: data/json/commercial_content.json,
# file_path: data/json/trading_journals.json,
# file_path: data/json/platform_tech.json,
# file_path: data/json/trading_systems.json,
# file_path: data/json/rookie_talk.json,
# file_path: data/json/broker_discussion.json,
# file_path: data/json/trading_discussion.json


file_dir = input('Enter file directory: ')

# getting the complete url list
with open(file_dir, mode='r') as json_file:
    json_data = json_file.read()
    url_list = json.loads(json_data)
    print(f"total number of threads: {len(url_list)}")


# running the concurrent

# old html_list
main_html_list = []


for url in url_list:
    start_time = time.perf_counter()
    new_html_list = asyncio.run(fast_spider(active_header)) # running the crawler
    stop_time = time.perf_counter()

    # collection all html and taking them in single list
    main_html_list.extend(new_html_list)

    print(f"total time took: {stop_time - start_time}")
    print(f"post found: {len(new_html_list)}")


# exporting the data
# exportData(file_name, data_list)