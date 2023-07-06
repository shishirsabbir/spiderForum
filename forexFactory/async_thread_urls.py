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


file_name = input('Enter the file name: ')


async def get_html(client, url):
        
        res = await client.get(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0'})
        
        if res.status_code == 200:
            return {"result": res.status_code, "url": res.url, "html_string": res.text}
        else:
            return {"result": res.status_code, "url": res.url, "html_string": None}
        


# running the main spider in concurrent mode
async def main():
    async with httpx.AsyncClient(timeout=None) as client:
        tasks = []

        # insert the range by yourself
        page_start = 1
        page_stop = 85

        # generating the url_list
        url_list = [f"https://www.forexfactory.com/forum/137-interactive-trading?sort=lastpost&order=desc&page={page}" for page in range(page_start, page_stop)]

        for url in url_list:
            tasks.append(asyncio.ensure_future(get_html(client, url)))

        async_response = await asyncio.gather(*tasks)

        print()

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
data_list = asyncio.run(main())
stop_time = time.perf_counter()

print(f"total time took: {stop_time - start_time}")
print(f"threads found: {len(data_list)}")


# exporting the data
exportData(file_name, data_list)