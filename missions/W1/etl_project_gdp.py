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
import pprint

# logger setting

# 테스트 로그 메시지
# logger.info("This is a test log message.")


def url_validation_check(url:str):
    '''
    URL 유효성 검증 함수
    Param: url: str
    return: html text
    '''
    response = requests.get(url)

    if response.status_code == 200:
        return response.text
    else:
        print(response.status_code)  
        return False      

def flatten(arr:list):
    '''
    중첩 리스트 평탄화 함수
    Param: arr: list
    return: list
    '''
    return[
        item
        for sublist in arr for item in (flatten(sublist) 
        if isinstance(sublist, list)else [sublist])
    ]

class Extract:
    WIKI_URL = ''
    IMF_URL = ''
    
    def __init__(self):
        self.WIKI_URL = 'https://en.wikipedia.org/wiki/List_of_countries_by_GDP_%28nominal%29'
        self.IMF_URL = 'https://www.imf.org/external/datamapper/api/v1/NGDPD'
    
    def collect_data(self, html: str):
        '''
        원본 데이터 수집 함수
        국가별 자료입니다. 형식: [[국가명, GDP, 연도, GDP, 연도, GDP, 연도] ... ] 
        Param: html: str
        return: gdp_rows: List 
        '''
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.select('table.wikitable > tbody > tr:nth-child(n+4)')#.wikitable sortable sticky-header-multi static-row-numbers jquery-tablesorter')
        # tr, td 등의 tag가 변수 취급이 가능하구나
        gdp_rows = [[td.get_text(strip=True) for td in tr.find_all('td')] for tr in table]

        return gdp_rows
    
    def data_from_IMF():
        '''
        현재 년도의 IMF의 API를 이용하여 데이터를 추출합니다.
        return: gdps: dict {country : GDP}
        '''
        year = datetime.datetime.now().strftime('%Y')
        nameURL = 'https://www.imf.org/external/datamapper/api/v1/countries'
        gdpURL = f'https://www.imf.org/external/datamapper/api/v1/NGDPD?periods={year}'

        response = requests.get(nameURL)
        names = response.text
        namedict = json.loads(names)['countries'] # 국가 코드 : 국가명 딕셔너리
        # 여기까지 2초 ~ 3초

        rspn = requests.get(gdpURL)
        gdptext = rspn.text
        gdpdict = json.loads(gdptext)['values']['NGDPD']
        # 여기까지 3초 ~ 5초

        gdps = {}
        for k, v in gdpdict.items():
            if k in namedict.keys(): # gdpdict에는 국가 이외의 대륙 분류 등이 섞여있음
                # if year in v.keys():
                gdps[namedict[k]['label']] = round(v[year], 2)
                # else:
                    # gdps[namedict[k]['label']] = -1
        return gdps
    
    def save_json(self, raws:list):
        '''
        데이터프레임을 JSON 형식으로 저장합니다.
        '''
        raw_json = {'country' : [], 
                    'forecast' : [], 
                    'year' : []
                    }
        for line in raws:
            raw_json['country'].append(line[0])
            
            if line[1] == '—':
                raw_json['forecast'].append('-')
                raw_json['year'].append('-')
            else:
                raw_json['forecast'].append(line[1])
                raw_json['year'].append(line[2])
                
        # try:
        filename = 'Countries_by_GDP.json'
        with open(filename, 'w') as f : 
            json.dump(raw_json, f, indent=4, ensure_ascii=False)
                     
        # except Exception as e:
        #     print(f"Error processing {filename}: {e}")

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
        
        return: country: List, gdp: List
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
            
    def save_GDP_to_DB(self,):
        '''
        데이터프레임을 DB에 저장합니다.
        '''
        try:
            with sqlite3.connect('World_Economies_test.db') as conn:
                print(f"Opened SQLite database with version {sqlite3.sqlite_version} successfully.")

        except sqlite3.OperationalError as e:
            print("Failed to open database:", e)
            
        self.frame.to_sql('Countries_by_GDP', conn)
    
    def save_Region_to_DB(self, region_data:dict):
        region_list = []
        for region, countries in region_data.items():
            for country in countries:
                region_list.append({"Region": region, "Country": country})
        region_df = pd.DataFrame(region_list)  
              
        try:
            with sqlite3.connect('World_Economies_test.db') as conn:
                print(f"Opened SQLite database with version {sqlite3.sqlite_version} successfully.")

        except sqlite3.OperationalError as e:
            print("Failed to open database:", e)
            
        region_df.to_sql('Region_Category', conn)        
        
def visualize_avg_GDP_by_Region(region:dict, gdp_data:dict):
    '''
    show Average of top 5 GDP of each Region
    Param: region: dict, gdp_data: dict
    return region_avg_gdp: pd.DataFrame
    '''
    
    # Step 1: region_to_country 데이터를 DataFrame으로 변환
    region_list = []
    for region, countries in region.items():
        for country in countries:
            region_list.append({"Region": region, "Country": country})
    region_df = pd.DataFrame(region_list)
    
    # Step 2: country_to_gdp 딕셔너리를 DataFrame으로 변환
    gdp_df = pd.DataFrame(list(gdp_data.items()), columns=["Country", "GDP"])

    # Step 3: 두 DataFrame 병합 (Country를 기준으로)
    merged_df = pd.merge(region_df, gdp_df, on="Country", how="inner")

    # Step 4: Region 별로 그룹화
    merged_df.GDP = merged_df.GDP.astype(int)
    top_5_by_region = (
        merged_df.sort_values(by=['Region', 'GDP'], ascending=[True, False])
        .groupby('Region')
        .head(5)
    )
    
    # Step 5: Region 별 상위 5개 GDP 평균 구하기
    region_avg_gdp = top_5_by_region.groupby("Region")["GDP"].mean().reset_index().apply(lambda x: round(x, 2))
    region_avg_gdp.columns = ["Region", "@5_GDP_Avg"]
    
    return region_avg_gdp

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

def region_categorize(html: str):
    '''
    Region : [소속 국가] 형식의 딕셔너리를 반환합니다.
    Param: html: str
    return: region: dict
    '''
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.select('div.fancy > table > tr')

    category = [[td.get_text(strip=False) for td in tr.find_all('th')] for tr in table]
    for i in range(len(category) - 1, -1, -1):  # 인덱스를 뒤에서부터 순회
        if not category[i]: del category[i] # 리스트가 비어있으면 제거
        
    nara = [[td.get_text(strip=False) for td in tr.find_all('p')] for tr in table]
    for i in range(len(nara) - 1, -1, -1):  # 인덱스를 뒤에서부터 순회
        if not nara[i]: del nara[i] # 리스트가 비어있으면 제거
        
    region_arr = []
    for c in category:
        if len(c) == 0: continue
        region_arr.append(re.sub(r'[\r\n\xa0]', '', c[0]))
        
    for i, line in enumerate(nara):
        tmp = []
        for subline in line:
            tmp.append(subline.split('\n'))
        tmp = flatten(tmp)
        
        for j in range(len(tmp)-1, -1, -1):
            text = tmp[j]
            text = re.sub(r'\r', '', text)
            # '\xa0\xa0'은 ''으로 대체하고, '\xa0' 한 개는 ' '으로 대체
            # '\xa0\xa0' 앞뒤로 문자가 붙어있으면 공백으로 대체
            text = re.sub(r'(?<=[A-Za-z])\xa0\xa0(?=[A-Za-z])', ' ', text)            
            text = re.sub(r'(?<=[A-Za-z])\.(?=[A-Za-z])', ' ', text)
            text = re.sub(r'\xa0\xa0', '', text) 
            text = re.sub(r'\xa0', ' ', text) 
            tmp[j] = text.strip()    
            
            if text == '':
                del tmp[j]
                continue
        nara[i] = tmp
        
    region = {}
    for k, v in zip(region_arr, nara):
        region[k] = v
    
    return region

def visualize_with_SQL():
    '''
    GDP 100B USD 이상인 국가들의 내림차순 정렬된 DataFrame,
    Region 별 상위 5개 국가의 GDP 평균을 담은 DataFrame을 반환합니다.
    return: df_gdp: pd.DataFrame, df_region: pd.DataFrame
    '''
    try:
        with sqlite3.connect('World_Economies_test.db') as conn:
            print(f"Opened SQLite database with version {sqlite3.sqlite_version} successfully.")
            cursor = conn.cursor()
    except sqlite3.OperationalError as e:
        print("Failed to open database:", e)

    sql_region = '''
WITH RankedCountries AS (
    SELECT 
        Countries_by_GDP.Country,
        Countries_by_GDP.GDP_USD_Bilion,
        B.Region,
        ROW_NUMBER() OVER (PARTITION BY B.Region ORDER BY GDP_USD_Bilion DESC) AS Rank
    FROM 
        Countries_by_GDP
    INNER JOIN 
        Region_Category AS B
    ON 
        Countries_by_GDP.Country = B.Country
)
SELECT 
    Region,
    ROUND(AVG(GDP_USD_Bilion), 2) AS Avg_GDP
FROM 
    RankedCountries
WHERE 
    Rank <= 5
GROUP BY 
    Region;


    '''
    df_region = pd.read_sql_query(sql_region, conn)

    sql_gdp = '''
    SELECT Country, GDP_USD_Bilion gdp
    FROM Countries_by_GDP
    WHERE gdp > 100
    ORDER BY gdp DESC
    '''

    df_gdp = pd.read_sql_query(sql_gdp, conn)
    
    return df_gdp, df_region

class Executer:
    wiki_data = []
    REFINED_DATA = None
    REGION = {}
        
    @logging_time
    def do_Extract(self,):
        
        E = Extract() 
        wiki_html = url_validation_check(E.WIKI_URL) # 웹 페이지 추출
        self.wiki_data = E.collect_data(wiki_html) # 데이터 수집
        E.save_json(self.wiki_data) # JSON 저장

    @logging_time
    def do_Transform(self, ):
        data = self.wiki_data
        T = Transform(data)
        ctry, gdp = T.refine_data()
        self.REFINED_DATA = T.make_DataFrame(ctry, gdp) # 데이터 정제 후 데이터프레임 반환
    
    @logging_time 
    def do_Load(self,):
        # dataframe = REFINED_DATA
        
        c = conn.cursor()
        tables = c.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        
        L = Load(self.REFINED_DATA)
        L.save_GDP_to_DB()
        
        if 'Region_Category' in tables:
            pass
        else:
            url = 'https://www.imf.org/external/datamapper/region.htm#sea'
            L.save_Region_to_DB(region_categorize(url_validation_check(url)))
        
#========================================================================================
if __name__ == "__main__":
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
    try:
        print("Start Code")
        with sqlite3.connect('World_Economies.db') as conn:
            print(f"Opened SQLite database with version {sqlite3.sqlite_version} successfully.")

    except sqlite3.OperationalError as e:
        print("Failed to open database:", e)    

    c = conn.cursor()

    runner = Executer()
    
    runner.do_Extract()
    print("Extracted")
    
    runner.do_Transform()
    print("Transformed")
    
    runner.do_Load()
    print("Loaded")
    
    df_gdp, df_region = visualize_with_SQL()
    print(df_gdp)
    print(df_region)