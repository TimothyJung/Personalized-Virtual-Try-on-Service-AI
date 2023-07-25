from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

import pandas as pd
import time

# 크롤링 
def crawling(url) :
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--remote-debugging-port=9222')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    driver.get(url)
    time.sleep(3)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', id='size_table', class_ = 'table_th_grey')
    rows = table.find_all('tr')
    data_dict = {}
    indexs = [th.get_text(strip=True) for th in soup.find_all('th', class_='item_val') if th.get_text(strip=True) != '소매길이']

    for row in rows:
        th = row.find("th")
        if th is None:
            continue

        key = th.text.strip()

        td_values = [td.text for td in row.find_all("td", class_="goods_size_val")]
        if td_values:
            for idx, size_key  in enumerate(indexs) :
                try :
                    update_info = {size_key : td_values[idx]}
                    data_dict[key].update(update_info)
                except : 
                    data_dict[key] = {size_key : td_values[idx]}
    return data_dict

# 사이즈 추천
def cloth_size(length, shoulderWidth, chestWidth, imageUrl, overfit) :
    try :
        # 사용자 사이즈 반환
        user_size = {'총장':length, '어깨너비':shoulderWidth, '가슴단면':chestWidth}
        # 크롤링 정보 반환
        crawling_dict = crawling(imageUrl)
        for idx, sizes in enumerate(crawling_dict) :
            for key, value in crawling_dict[sizes].items() :
                if user_size[key] > float(value) :
                    break
            else :
                if overfit and idx+1 < len(crawling_dict) : overfit = False;
                else : return sizes
        else :
            return 'None-size'
    except : return 'None-info'

#print(cloth_size(55, 37, 45.5, 'https://www.musinsa.com/app/goods/903340', False))