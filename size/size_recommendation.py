'''
* 사이즈 추천 알고리즘
    - 사용자가 키, 몸무게 정보 입력 시 size_data.csv 파일에서 키와 몸무게가 가장 유사한 행을 찾아 신체 치수(총장, 어깨너비, 가슴단면 반환)
    - 일반핏 선호 시 사용자의 치수에 맞는 의류 사이즈 추천
    - 루즈핏 선호 시 사용자의 치수에 맞는 의류 기준 한 사이즈 up 

* 예외 처리
1. 사용자의 신체 치수에 맞는 사이즈가 없을 경우 - 'None-size' 반환
2. 무신사 페이지에 사이즈 정보가 없을 경우 - 'None-info' 반환
### 이외의 경우는 무신사 특정 의류 페이지에서 제공하는 사이즈명(S, M, L, small, large, 1, 2 등)과 일치하는 사이즈 추천 결과값 반환
'''
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

import pandas as pd
import time

# 사용자 신체 치수 리턴 함수
def return_size(target_height, target_weight, data_path = 'size/size_data.csv'
) :
    from scipy.spatial.distance import cdist
    
    data = pd.read_csv(data_path)
    # 유클리디안 거리 계산
    distances = cdist(data[['키', '몸무게']], [[target_height, target_weight]], metric='euclidean')

    # 근사값이 가장 작은 행 선택
    closest_row_index = distances.argmin()
    closest_row = data.iloc[closest_row_index].to_dict()
    return closest_row

# 크롤링 
def crawling(url) :
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')  # Headless 모드로 실행
    chrome_options.add_argument('--disable-gpu')  # GPU 가속 비활성화
    chrome_options.add_argument('--no-sandbox')  # 보안 기능 비활성화 (필요한 경우)
    chrome_options.add_argument('--remote-debugging-port=9222')  # 원격 디버깅 포트 설정    # 크롬 브라우저 열기
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
def size(height, weight, imageUrl, loosefit_condition) :
    try :
        # 사용자 사이즈 반환
        user_size = return_size(height, weight)
        # 크롤링 정보 반환
        crawling_dict = crawling(imageUrl)
        for idx, sizes in enumerate(crawling_dict) :
            for key, value in crawling_dict[sizes].items() :
                if user_size[key] > float(value) :
                    break
            else :
                if loosefit_condition == '오버핏' and idx+1 < len(crawling_dict) : loosefit_condition = '';
                else : return sizes, user_size
        else :
            return 'None-size'
    except : return 'None-info'


#print(size(185, 74, 'https://www.musinsa.com/app/goods/983339', ''))