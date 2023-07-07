import re
import os
import csv
import json
import requests
from urllib import parse
from bs4 import BeautifulSoup
from library.output_data import exportData
from library.automate import By, Keys, EC, Action, wait_for, genBrowser, driverWait



# custom header list

header_list = [
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0'},
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'},
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/114.0'},
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 OPR/100.0.0.0'},
    {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}
]



# can change the header from here

active_header = header_list[0]



# instructions that needs to be printed
print('''
        This is crawler code, it will ask multiple user input during the run time.
        Here are some-

        At first it's gonna ask for the category url. In forexfactory website we have
        8 catergories of threads. We have provide those category of threads urls. As
        example: # https://www.forexfactory.com/forum/137-interactive-trading

        And Every time it's gonna ask you for the file name to save the CSV and JSON.
        For the above interactive page the file name will be: "interactive_trading".
    ''')



# one session and base url

base_url = "https://www.forexfactory.com"
session = requests.Session()



# all the lists that will store the scraped data

thread_url_list = []
error_response_urls = []



# user input forum category url

category_url = input("Enter Category Url: ")

res = session.get(category_url, headers=active_header)

if res.status_code == 200:
    soup = BeautifulSoup(res.text, 'lxml')
    page_num_tag = soup.select_one('div.forumdisplay__footer li.visible-mv a.last')
    page_num = page_num_tag.string
    url_path = page_num_tag['href']
    thread_page_url = parse.urljoin(base_url, url_path)
    
else:
    print(f"Bad Response of Forum Pages: {res.status_code}")



forum_page_num = int(page_num) + 1
forum_pages = [page for page in range(1, forum_page_num)]
print(f"total number of pages: {len(forum_pages)}")

for page in forum_pages:
    url_obj = parse.urlparse(thread_page_url)
    url_dict = url_obj._asdict()
    base_url = base_url = "https://www.forexfactory.com"
    path = url_dict['path']

    new_url = base_url + path + f"?sort=lastpost&order=desc&page={page}"
    
    res = session.get(new_url, headers=active_header)

    if res.status_code == 200:
        print(f"Crawling from page: {page}")
        soup = BeautifulSoup(res.text, 'lxml')

        thread_tags = soup.select('table#threadslist tr.threadlist__row div.threadlist__title-wrapper')

        for thread in thread_tags:
            thread_name = thread.get_text(strip=True)
            thread_url = thread.a['href']

            thread_dict = {
                "thread_name": thread_name,
                "thread_url": thread_url
            }

            thread_url_list.append(thread_dict)
    else:
        print(f"Bad Response: {res.status_code}")
        error_response_urls.append({'response': res.status_code, 'url': res.url})


# printing the number of thread found in the category

print(f"threads found: {len(thread_url_list)}")



# exporting the data to csv and json

file_name = input('Enter the file name: ')
exportData(file_name, thread_url_list)




# exporting the error urls
output_file = f"./cached_data/{file_name}_error_urls.json"
with open(output_file, mode='w') as json_file:
    json_data = json.dumps(error_response_urls)
    json_file.write(json_data)
    print("error response urls are saved in cached_data/ folder")








# end of the file