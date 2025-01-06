import requests
from bs4 import BeautifulSoup# 크롤링
import pandas as pd # 데이터 처리
import json # to json file
import datetime # logging
import sqlite3 # DB
import re
import time, datetime
import logging
from functools import wraps

class Extract:
    WIKI_URL = ''
    IMF_URL = ''
    
    def __init__(self):
        self.WIKI_URL = 'https://en.wikipedia.org/wiki/List_of_countries_by_GDP_%28nominal%29'
        self.IMF_URL = 'https://www.imf.org/external/datamapper/api/v1/NGDPD'
    
    def url_validation_check(self, url:str):
        '''
        URL 유효성 검증
        Param: url: str
        return: html text
        '''
        response = requests.get(url)

        if response.status_code == 200:
            return response.text
        else:
            print(response.status_code)  
            return False      
    
    def collect_data(self, html: str):
        '''
        원본 데이터 수집
        Param: html: str
        return: gdp_rows: List 
        # 국가별 자료입니다. 형식: [[국가명, GDP, 연도, GDP, 연도, GDP, 연도] ... ] 
        '''
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.select('table.wikitable > tbody > tr:nth-child(n+4)')#.wikitable sortable sticky-header-multi static-row-numbers jquery-tablesorter')
        # tr, td 등의 tag가 변수 취급이 가능하구나
        gdp_rows = [[td.get_text(strip=True) for td in tr.find_all('td')] for tr in table]

        return gdp_rows

    def save_json(self,):
        '''
        데이터프레임을 JSON 형식으로 저장합니다.
        '''
        try:
            filename = 'Countries_by_GDP.json'
            self.frame.to_json(filename, indent=4)
            print(f"Updated: {filename}")
        
        except Exception as e:
            print(f"Error processing {filename}: {e}")

class Transform:
    raw_data = []
    def __init__(self, raw_data:list):
        '''
        데이터를 가공하기 위해 원본 데이터를 가져옵니다.
        '''
        self.raw_data = raw_data
    
    def refine_data(self):
        '''
        데이터를 정제합니다.
        링크를 지우고 문자열로 된 숫자를 정수로 변환합니다.
        '-'로 표기된 데이터는 -1 을 기입합니다.
        
        return: country: List, gdp: List, year: List
        '''
        country = []
        gdp = []
        # year = []
        
        no_juseok = lambda s: re.sub(r'\[.*?\]', '', s)
        str_to_num = lambda s: int(re.sub(r',', '', s))
        
        for i, row in enumerate(self.raw_data):

            if len(row) < 2: 
                print(f"Data Error in line {i}")
                
            country.append(no_juseok(row[0]))
            
            if row[1] == '—': 
                gdp.append(-1)
            else: 
                gdp.append(str_to_num(no_juseok(row[1])))
        
        return country, gdp
        
    def make_DataFrame(self, country:list, gdp:list):
        '''
        가공된 데이터로 데이터프레임을 생성합니다.
        GDP에 대해 내림차순 정렬되어 있고 GDP가 $100B 이상인 국가만 포함됩니다.

        Param: country: List, gdp: List, year: List
        return: GDP_data: pd.DataFrame
        '''
        GDP_data = pd.DataFrame({'Country': country, 'GDP_USD_Bilion': gdp})
        GDP_data.sort_values('GDP_USD_Bilion', ascending=False, inplace=True)
           
        GDP_data['GDP_USD_Bilion'] = GDP_data['GDP_USD_Bilion'].apply(lambda x: round(x / 1000, 2))
        
        
        return GDP_data[GDP_data['GDP_USD_Bilion'] >= 100]
    
class Load:
    frame = None
    def __init__(self, frame:pd.DataFrame):
        '''
        데이터프레임을 저장하기 위해 불러옵니다.
        '''
        self.frame = frame
    
            
    def save_db(self,):
        '''
        데이터프레임을 DB에 저장합니다.
        '''
        try:
            with sqlite3.connect('World_Economies.db') as conn:
                print(f"Opened SQLite database with version {sqlite3.sqlite_version} successfully.")

        except sqlite3.OperationalError as e:
            print("Failed to open database:", e)
            
        self.frame.to_sql('Countries_by_GDP', conn)
        
def visualize():
    # show top 5 countries of each Region
    REGION = {
        'Africa':[],
        'North Africa':[],
        'Sub-Saharan Africa':[],
        'Asia and Pacific':[],
        'Australia and New Zealand':[],
        'Central Asia and the Caucasus':[],
        'East Asia':[],
        'Pacific Islands':[],
        'South Asia':[],
        'Southeast Asia':[],
        'Europe':[],
        'Eastern Europe':[],
        'Western Europe':[],
        'Middle East':[],
        'Western Hemisphere':[],
        'Caribbean':[],
        'Central America':[],
        'North America':[],
        'South America':[]
    }

logger = logging.getLogger()
if not logger.handlers:
    # 사용자 정의 Formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s, %(message)s',
        datefmt='%Y-%B-%d-%H-%M-%S'  # 원하는 날짜 포맷
    )

    # 핸들러 생성 및 설정
    handler = logging.FileHandler('etl_project_log.txt')
    handler.setFormatter(formatter)

    # 로거 설정
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

# 테스트 로그 메시지
logger.info("This is a test log message.")

def logging_time(func):
    '''
    @logging_time을 로깅하고 싶은 함수 윗줄에 작성한다.
    '''    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # start_time = datetime.datetime.now()
        # formatted_start = start_time.strftime("%Y-%B-%d-%H-%M-%S")

        logging.info(f"Started '{func.__name__}'")
        
        result = func(*args, **kwargs)
        
        # end_time = datetime.datetime.now()
        # formatted_end = end_time.strftime("%Y-%B-%d-%H-%M-%S")

        logging.info(f"Finished '{func.__name__}'")
        # logging.info(f"Execution time for '{func.__name__}': {end_time - start_time}")
        return result
    return wrapper