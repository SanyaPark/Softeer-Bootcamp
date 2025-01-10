import requests, re, datetime, logging, os, json # to json file
import sqlite3 # DB
import pandas as pd # 데이터 처리
from io import StringIO
from bs4 import BeautifulSoup# 크롤링
from functools import wraps
from itertools import islice
import dask.dataframe as dd

# logger setting
current_dir = os.path.dirname(os.path.abspath(__file__))

log_file = 'etl_project_log.txt'
log_file_path = os.path.join(current_dir, log_file)

raw_json = 'Countries_by_GDP.json'
raw_json_file_path = os.path.join(current_dir, raw_json)

db_name = 'World_Economies.db'
db_path = os.path.join(current_dir, db_name)

logger = logging.getLogger()

#========================================================================================

def is_within_5_months(past_year:int, past_month:int, latest_year:int, latest_month:int):
    '''연도와 월을 기준으로 총 차이가 5개월 이내인지 계산'''
    total_months_past = past_year * 12 + past_month
    total_months_latest = latest_year * 12 + latest_month
    
    return (total_months_latest - total_months_past) <= 5

#========================================================================================

def save_Region_to_DB(conn: sqlite3.Connection, region_data:dict):
    '''
    Region data를 DB에 'Region_Category' 테이블로 저장합니다.
    Args: 
        region_data (dict)
    '''
    region_list = []
    for region, countries in region_data.items():
        for country in countries:
            region_list.append({"Region": region, "Country": country})
    region_df = pd.DataFrame(region_list)  
            
    try:            
        region_df.to_sql('Region_Category', conn, if_exists='faiil')  

    except ValueError as e:
        print("Region Category already exists .")
        pass
        
    except sqlite3.OperationalError as e:
        # "database is locked"와 같은 OperationalError 처리
        if "database is locked" in str(e):
            print(f"Error: Database is locked while trying to drop table .")
        else:
            print(f"OperationalError: {e}")
    
    except sqlite3.DatabaseError as e:
        # 일반적인 데이터베이스 오류 처리
        print(f"DatabaseError: {e}")
    
    except Exception as e:
        # 다른 예외 처리
        print(f"Unexpected error: {e}")
    conn.commit()     


def get_last_valid_log_with_position(file_path, start_pos=None):
    with open(file_path, 'rb') as f:
        if start_pos is not None:
            f.seek(start_pos)  # 주어진 위치에서 시작

        f.seek(0, 2)  # 파일 끝으로 이동
        file_size = f.tell()  # 파일 크기 확인

        # 만약 파일이 비어 있지 않다면 마지막 줄이 빈 라인인지 체크
        last_pos = file_size
        if file_size > 0:
            f.seek(file_size - 1)  # 마지막 바이트로 이동

            # 파일이 마지막 줄에서 \n으로 끝나는지 확인
            last_byte = f.read(1)
            if last_byte == b'\n':  # 마지막 줄이 빈 라인이라면
                last_pos = f.tell() - 1  # 커서를 한 줄 위로 옮김

        return last_pos  # 새로운 커서 위치 반환
# def get_latest_log_with_pandas(file_path:str, seeker:int = -1):
#     """
#     Pandas를 사용해 로그 파일의 마지막 로그를 가져옵니다.
#     로그 파일의 크기가 작다면 이쪽이 더 효율적입니다.
#     로그는 '년도, 작업_성공_여부, 작업' 형태로 구조화되어 있어야 합니다.
    
#     Args:
#         file_path (str): 로그 파일 경로 (CSV 형식).
#         seeker (int): 읽을 로그 인덱스
#     Returns:
#         str: "년도 (int), 작업_성공_여부 (str), 작업 (str)"
#         int: 읽어온 로그의 직전 로그 인덱스
#     """
#     # 파일이 비어 있는지 확인
#     with open(file_path, 'r') as file:
#         file.seek(0, os.SEEK_END)
#         isempty = file.tell() == 0
#         file.seek(0)    # 파일 되감기
#         if isempty: 
#             return '', 0
        
    
#     # 로그 파일을 Pandas DataFrame으로 읽기
#     df = pd.read_csv(file_path, header=None, names=['year', 'status', 'task'])
#     df = df.dropna(how='all').reset_index(drop=True)

#     # 마지막 로그 가져오기
#     # 로그가 불완전할 경우 끝까지 읽다 터지는 것 방지
#     try:
#         last_log = df.iloc[seeker] if not df.empty else None
#         if last_log is None or last_log.isnull().all():
#         # 마지막 로그가 공백일 경우, 이전 로그 찾기
#             last_log = df.iloc[-2] if len(df) > 1 else None
            
#     except IndexError as e:
#         print("마지막 로그까지 읽었습니다. 잘못된 로그가 있을 가능성이 높습니다.")
#         # 공백 로그를 확인하고 이전 로그를 가져오기
#         if seeker == -1:
#             seeker -= 1
#             last_log = df.iloc[seeker] if len(df) > abs(seeker) else None
#             print(f"대체된 마지막 로그: {last_log}")
#             return ",".join([last_log['year'], last_log['status'], last_log['task']]), seeker
#         return '', 0 # <-- 로그가 잘못되었으니 일단 데이터를 새로 갱신 시도
    
#     return ",".join([last_log['year'], last_log['status'], last_log['task']]), seeker-1

#========================================================================================

def get_latest_log(file_path, start_position=None): 
    """
    가장 최근 기록된 로그를 가져오거나, 주어진 시작 위치에서 이전 로그를 탐색합니다.

    Args:
        file_path (str): 로그 파일 경로.
        start_position (int, optional): 탐색을 시작할 파일 포인터 위치. 기본값은 None(파일 끝).

    Returns:
        tuple: (buffer (str): 가장 최근 로그, file_position (int): 현재 파일 포인터 위치)
    """
    with open(file_path, 'rb') as file:
        # 파일 끝에서부터 탐색 시작
        if start_position is None:
            file.seek(0, 2)  # 파일 끝으로 이동
            file_position = file.tell()
        else:
            file.seek(start_position)
            file_position = start_position

        if file_position == 0:  # 파일이 비어 있거나 시작 위치가 파일 시작이라면
            return '', 0

        buffer = bytearray()
        while file_position > 0:
            file_position -= 1
            file.seek(file_position)
            byte = file.read(1)

            if byte == b'\n':  # 줄바꿈 문자를 만남
                if buffer:  # 버퍼에 내용이 있다면 최신 로그 반환
                    return buffer[::-1].decode('utf-8'), file_position
            else:
                buffer.append(byte[0])

        # 파일이 줄바꿈 없이 단일 라인인 경우
        if buffer:
            return buffer[::-1].decode('utf-8'), file_position

    return '', 0  # 비어 있는 파일

#========================================================================================
      
def is_DB_Latest(log: str):
    '''
    ### !! IMF는 4, 10월에 데이터를 갱신 !!
    로그 기반으로 데이터 최신화 필요성을 검증합니다.
    마지막 데이터 저장 이후 5개월 초과 | 마지막 로그에 문제가 있었을 경우 False를 반환합니다.
    Args: log: str
    return: bool
    '''
    
    if len(log) == 0: return False
    now = datetime.datetime.now().strftime("%Y-%m")
    now_Y, now_m = map(int, now.split('-')[:2])
    
    log_year, log_month = log.split('-')[:2]
    log_year = int(log_year)
    log_month = int(datetime.datetime.strptime(log_month, '%B').month)

    return is_within_5_months(log_year, log_month, now_Y, now_m)

#========================================================================================

def check_columns_exist(conn:sqlite3.Connection, db_path:str, columns_to_check:str, table_name:str ='Gdp_past'):
    # 데이터베이스 연결
    conn = conn
    cursor = conn.cursor()
    
    # PRAGMA table_info()로 컬럼 정보 가져오기
    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        table_info = cursor.fetchall()
    except:
        print("Data NOT Exists")
        return False
    
    # 컬럼 이름만 추출
    column_names = [column[1] for column in table_info]  # column[1]은 컬럼 이름
    
    # 확인하려는 컬럼이 존재하는지 검사
    result = columns_to_check in column_names
    
    # 연결 종료
    cursor.close()
    
    return result

# # 사용 예시
# db_path = "example.db"  # SQLite 데이터베이스 파일 경로
# table_name = "my_table"  # 확인하려는 테이블 이름
# columns_to_check = ['yyyy', 'yyyy-1']  # 확인하려는 컬럼 이름들

# result = check_columns_exist(db_path, table_name, columns_to_check)
# print(result) >>> {'yyyy': True, 'yyyy-1': False}

#========================================================================================
  
def url_validation_check(url:str):
    '''
    URL 유효성 검증 함수
    Args: url: str
    return: html text
    '''
    response = requests.get(url)

    if response.status_code == 200:
        return response.text
    else:
        print(response.status_code)  
        return False      

#========================================================================================

def flatten(arr:list):
    '''
    중첩 리스트 평탄화 함수
    Args: arr: list
    return: list
    '''
    return[
        item
        for sublist in arr for item in (flatten(sublist) 
        if isinstance(sublist, list)else [sublist])
    ]

#========================================================================================

class Extract:
    WIKI_URL = ''
    IMF_URL = ''
    now_year = int(datetime.datetime.now().strftime('%Y'))
    def __init__(self):
        self.WIKI_URL = 'https://en.wikipedia.org/wiki/List_of_countries_by_GDP_%28nominal%29'
        self.IMF_URL = 'https://www.imf.org/external/datamapper/api/v1/NGDPD'
    
    def data_from_IMF(self, year = now_year):
        '''
        현재 년도의 IMF의 API를 이용하여 데이터를 추출합니다.
        
        Args: 
            year: int (현재년도)
        
        Returns:
            gdps (pd.DataFrame {country | GDP})
        '''
        year = year
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
        gdps = pd.DataFrame({'Country': list(gdps.keys()), 'GDP_USD_bilion': list(gdps.values())})
        # print(gdps)
        return gdps
    
    def save_json(self, url: str):
        '''
        웹 상의 테이블 데이터 '원본'을 JSON 형식으로 저장합니다.
        
        Args: 
            url (str)
        '''
        # 첫 번째 테이블을 가져옵니다 (여러 테이블이 있을 수 있으므로 인덱스로 선택)
        df = pd.read_html(StringIO(url), attrs={"class": "wikitable"})[0]
         
        # MultiIndex 생성
        columns = [
            ["Country"] + ["IMF"] * 2 + ["WB"] * 2 + ["UN"] * 2,
            [   ""    ] + ["Forecast", "Year"] * 3  # 하위 컬럼: Forecast와 Year 반복
        ]

        # MultiIndex로 설정
        df.columns = pd.MultiIndex.from_arrays(columns)
                        
        try:
            df.to_json(raw_json_file_path, force_ascii=False, indent=4)
        except Exception as e:
            print("Error Occured While Saving Raw Data:", e)

#========================================================================================

class Transform:
    '''
    수정 완료 사항:
    타 클래스 의존성을 배제하여 원본 데이터 json 파일만 있다면 단독으로 동작 가능합니다.
    '''
    country = []
    gdp = []
    
    def __init__(self,):
        self.country = []
        self.gdp = []
        
    def refine_data(self, ):
        '''
        데이터를 정제합니다.
        링크를 지우고 문자열로 된 숫자를 정수로 변환합니다.
        '-'로 표기된 데이터는 None 을 기입합니다.
        
        Returns: 
            country (list)
            gdp (list)
        '''
        og_data = pd.read_json(raw_json_file_path)
        columns = [
            ["Country"] + ["IMF"] * 2 + ["WB"] * 2 + ["UN"] * 2,
            [""] + ["Forecast", "Year"] * 3  # 하위 컬럼: Forecast와 Year 반복
        ]
        og_data.columns = pd.MultiIndex.from_arrays(columns)     
        
        country = []
        gdp = []
        # year = []
        
        # to refine messy texts like link ... etc
        no_juseok = lambda s: re.sub(r'\[.*?\]', '', s)
        str_to_num = lambda s: int(re.sub(r',', '', s))
        
        for i, d in islice(enumerate(zip(og_data['Country'], og_data['IMF']['Forecast'])), 1, None):
            ctry, forecast = d[0], d[1]
            if ctry == None or forecast == None: 
                print(f"Data Error in line {i}")
                
            country.append(no_juseok(ctry))
            
            if forecast == '—':  # 결측치 처리
                gdp.append(None) # NULL value
            else: 
                gdp.append(str_to_num(no_juseok(forecast)))
        
        self.country = country 
        self.gdp = gdp
        
    def make_DataFrame(self, country:list, gdp:list):
        '''
        가공된 데이터로 데이터프레임을 생성합니다.
        GDP에 대해 내림차순 정렬되어 있고, 단위는 1B USD, 소수점 두자리까지 출력됩니다.
        
        Args: 
        country (list[str])
        gdp (list[int | None])
        
        Returns 
            GDP_data (pd.DataFrame)
        '''
        country = self.country
        gdp = self.gdp
        GDP_data = pd.DataFrame({'Country':country, 'GDP_USD_bilion':gdp})
        
        # GDP 내림차순 정렬
        GDP_data.sort_values(by=('GDP_USD_bilion'), ascending=False, inplace=True)
        
        # 소수점 둘째자리까지 보이기   
        GDP_data['GDP_USD_bilion'] = (GDP_data['GDP_USD_bilion'] / 1000).round(2)
        # 메모리에 못 올릴 정도로 대규모 데이터일 경우 : dask를 이용한 분산처리 
        # ddf = dd.from_pandas(df, npartitions=4)  # 데이터프레임을 분할
        # ddf['column_name'] = (ddf['column_name'] / 1000).round(2)
        # df = ddf.compute()  # 결과를 다시 pandas로 변환
        return GDP_data      

#========================================================================================

class Load:
    frame = None
    conn = None
    request_year = ''
    log = ''
    def __init__(self, frame:pd.DataFrame, conn:sqlite3.Connection, request_old_data:str = '', log:str = ''):
        '''
        데이터프레임을 저장하기 위해 가공된 데이터프레임을 불러옵니다.
        Args: 
            frame (pd.DataFrame)
            conn (sqlite3.Connection)
            rq_date (str)
            log (str)
        '''
        self.frame = frame    
        self.conn = conn    
        self.request_year = request_old_data
        self.log = log
    #========================================================================================

    def save_GDP_to_DB(self,):
        '''
        데이터프레임을 DB에 저장합니다.
        '''
        # 먼저 오래된 데이터 따로 빼기
        
        
        try:
            self.frame = self.frame.sort_values(by='Country')
            self.frame.to_sql('Countries_by_GDP', self.conn, if_exists='replace')
        except Exception as e:
            print("Something Wrong With Saving Data to DB: ", e)
        
        self.conn.commit()
        
    #====================================================================================
    
    def latest_data_backup(self, conn:sqlite3.Connection):
        '''
        DB 갱신 시 현 최신 데이터를 과거 데이터 테이블로 백업합니다.
        백업된 데이터는 Past_Data table에 
        Country | Year-2 | Year-1 | ... 형식으로 저장됩니다. 
        (1,2는 상/하반기)
        Args: 
            conn (sqlite3.Connection)
        '''
        saved_date = self.log
        cursor = conn.cursor()
        
        # 4 / 10월 데이터 판단
        saved_date = datetime.datetime.strptime(saved_date, "%Y-%B-%d-%H-%M-%S")
        saved_y = saved_date.year
        saved_m = saved_date.month
        
        if saved_m <= 4:          
            saved_y -= 1
            saved_m = 2 # past year 11 ~ now 4
        elif 4 < saved_m <= 10:
            saved_m = 1 # now 5 ~ 10
        else:
            saved_m = 2 # now 11 ~ 12
                
        
        # 'gdp_past' 테이블이 없는 경우 생성
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS Gdp_past (
            Country TEXT PRIMARY KEY
        )
        """)

        # 'gdp_past' 테이블에 현재 날짜 컬럼 추가 (없는 경우)
        alter_query = f"ALTER TABLE Gdp_past ADD COLUMN GDP_{saved_y}_{saved_m} REAL"
        try:
            cursor.execute(alter_query)
        except sqlite3.OperationalError:
            # 컬럼이 이미 존재할 경우 예외를 무시
            pass
        
        
        
        
        # wiki데이터가 null인 국가를 imf api로 저장한 과거데이터에 넣을 시 대처법 생각하기
        # 'gdp_now'에만 있는 country를 'gdp_past'에 NULL 값으로 추가
        cursor.execute("""
        INSERT INTO Gdp_past (Country)
        SELECT Country
        FROM Countries_by_GDP
        WHERE NOT EXISTS (SELECT 1 FROM Gdp_past WHERE Gdp_past.Country = Countries_by_GDP.Country)
        """)

        print("여기까진 된다??")    
        
        # 'gdp_now' 데이터를 'gdp_past'에 삽입 (horizontal 저장)
        cursor.execute(f"""
        INSERT INTO Gdp_past (Country, GDP_{saved_y}_{saved_m})
        SELECT Country, GDP_USD_bilion
        FROM Countries_by_GDP
        ON CONFLICT(Country) DO UPDATE 
        SET GDP_{saved_y}_{saved_m} = excluded.GDP_USD_bilion;
        """)
        
        print(f"{saved_y}_{saved_m} data stored in backup table")

    #====================================================================================
    
    #====================================================================================
    
    def add_past_data(self, conn:sqlite3.Connection):
        cursor = conn.cursor()
        saved_y = self.request_year.split('-')[0]
        
        # 'gdp_past' 테이블이 없는 경우 생성
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS Gdp_past (
            Country TEXT PRIMARY KEY
        )
        """)

        # 'gdp_past' 테이블에 현재 날짜 컬럼 추가 (없는 경우)
        alter_query = f"ALTER TABLE Gdp_past ADD COLUMN GDP_{saved_y} REAL"
        try:
            cursor.execute(alter_query)
        except sqlite3.OperationalError:
            # 컬럼이 이미 존재할 경우 예외를 무시
            pass

        # wiki데이터가 null인 국가를 imf api로 저장한 과거데이터에 넣을 시 대처법 생각하기
        # 'gdp_now'에만 있는 country를 'gdp_past'에 NULL 값으로 추가
        # cursor.execute("""
        # INSERT INTO Gdp_past (Country)
        # SELECT Country
        # FROM Countries_by_GDP
        # WHERE Country NOT IN (SELECT Country FROM Gdp_past)
        # """)
                
        # 백업용 데이터베이스 테이블에서 'Country' 컬럼 가져오기
        db_table = 'Gdp_past'
        db_data = pd.read_sql_query(f"SELECT * FROM {db_table} ORDER BY Country ASC", conn)

        # 데이터프레임 가져오기
        df = self.frame

        
        
        # 데이터프레임과 데이터베이스 매칭
        db_data = db_data.merge(df, on='Country', how='left') # 없는 값들은 NULL로 채움
        print(db_data)

        # 데이터베이스 테이블 업데이트
        for _, row in db_data.iterrows():
            cursor.execute(f"""
                UPDATE {db_table}
                SET GDP_{saved_y} = ?
                WHERE Country = ?
            """, (row[f'GDP_{saved_y}'], row['Country']))
    
    #====================================================================================
        
    # def save_Region_to_DB(self, region_data:dict):
    #     '''
    #     Region data를 DB에 'Region_Category' 테이블로 저장합니다.
    #     Args: 
    #         region_data (dict)
    #     '''
    #     region_list = []
    #     for region, countries in region_data.items():
    #         for country in countries:
    #             region_list.append({"Region": region, "Country": country})
    #     region_df = pd.DataFrame(region_list)  
              
    #     try:            
    #         region_df.to_sql('Region_Category', self.conn, if_exists='faiil')  

    #     except ValueError as e:
    #         print("Region Category already exists .")
    #         pass
            
    #     except sqlite3.OperationalError as e:
    #         # "database is locked"와 같은 OperationalError 처리
    #         if "database is locked" in str(e):
    #             print(f"Error: Database is locked while trying to drop table .")
    #         else:
    #             print(f"OperationalError: {e}")
        
    #     except sqlite3.DatabaseError as e:
    #         # 일반적인 데이터베이스 오류 처리
    #         print(f"DatabaseError: {e}")
        
    #     except Exception as e:
    #         # 다른 예외 처리
    #         print(f"Unexpected error: {e}")
    #     self.conn.commit()     

#========================================================================================
         
def region_categorize(html: str):
    '''
    Region : [소속 국가] 형식의 딕셔너리를 반환합니다.
    Args: 
        html (str)
    Returns: 
        region (dict)
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

#========================================================================================

def visualze_GDP_DESC_Over_100(gdp_data: dict):
    '''
    SQL을 사용하지 않고 GDP >= 100B USD인 데이터프레임을 출력합니다.
    Args: 
        gdp_data (dict)
    '''
    df = pd.DataFrame(gdp_data)
    df.sort_values('GDP_USD_bilion', ascending=False, inplace=True)
    df = df[df['GDP_USD_bilion'] >= 100]
    df['GDP_USD_bilion'] = (df['GDP_USD_bilion'] / 1000).round(2)
    # 메모리에 못 올릴 정도로 대규모 데이터일 경우 : dask를 이용한 분산처리 
    # ddf = dd.from_pandas(df, npartitions=4)  # 데이터프레임을 분할
    # ddf['column_name'] = (ddf['column_name'] / 1000).round(2)
    # df = ddf.compute()  # 결과를 다시 pandas로 변환    
    print(df)

#========================================================================================
    
def visualize_avg_GDP_by_Region(gdp_data:dict):
    '''
    SQL을 사용하지 않고 Region 별 상위 5개 국가의 평균 GDP를 기록한 데이터프레임을 출력합니다.
    Args: 
        region (dict) 
        gdp_data (dict)
    '''
    region = region_categorize(url_validation_check('https://www.imf.org/external/datamapper/region.htm#sea'))

    # Step 1: region_to_country 데이터를 DataFrame으로 변환
    region_list = []
    for region, countries in region.items():
        for country in countries:
            region_list.append({"Region": region, "Country": country})
    region_df = pd.DataFrame(region_list)

     # Step 2: country_to_gdp 딕셔너리를 DataFrame으로 변환
    gdp_df = pd.DataFrame(gdp_data)
    # TODO --> None 값 -1로 수정해야 아래 코드가 돌아감
    gdp_df['GDP_USD_bilion'] = gdp_df['GDP_USD_bilion'].fillna(0)

    # Step 3: 두 DataFrame 병합 (Country를 기준으로)
    merged_df = pd.merge(region_df, gdp_df, on="Country", how="inner")

    
    # Step 4: Region 별로 그룹화
    merged_df.GDP_USD_bilion = merged_df.GDP_USD_bilion.astype(float)
    top_5_by_region = (
        merged_df.sort_values(by=['Region', 'GDP_USD_bilion'], ascending=[True, False])
        .groupby('Region')
        .head(5)
    )
    
    # Step 5: Region 별 상위 5개 GDP 평균 구하기
    region_avg_gdp = top_5_by_region.groupby("Region")["GDP_USD_bilion"].mean().reset_index().round(2)
    # 메모리에 못 올릴 정도로 대규모 데이터일 경우 : dask를 이용한 분산처리 
    # ddf = dd.from_pandas(df, npartitions=4)  # 데이터프레임을 분할
    # ddf['column_name'] = (ddf['column_name'] / 1000).round(2)
    # df = ddf.compute()  # 결과를 다시 pandas로 변환    
    region_avg_gdp.columns = ["Region", "@5_GDP_Avg"]
    
    print(region_avg_gdp)

#========================================================================================

def logging_time(func):
    '''
    @logging_time을 로깅하고 싶은 함수 윗줄에 작성한다.
    '''    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # start_time = datetime.datetime.now()
        # formatted_start = start_time.strftime("%Y-%B-%d-%H-%M-%S")

        logging.info(f"Started, {func.__name__}")
        
        result = func(*args, **kwargs)
        
        # end_time = datetime.datetime.now()
        # formatted_end = end_time.strftime("%Y-%B-%d-%H-%M-%S")

        logging.info(f"Finished, {func.__name__}")
        # logging.info(f"Execution time for '{func.__name__}': {end_time - start_time}")
        return result
    return wrapper

#========================================================================================

def visualize_with_SQL(connection:sqlite3.Connection):
    '''
    GDP 100B USD 이상인 국가들의 내림차순 정렬된 DataFrame과
    Region 별 상위 5개 국가의 GDP 평균을 담은 DataFrame을 반환합니다.
    Args:
        connection (sqlite3.Connection)
    Returns: 
        df_gdp (pd.DataFrame)
        df_region (pd.DataFrame)
    '''
    conn = connection
    # try:
    #     with sqlite3.connect(db_path) as conn:
    #         print(f"Opened SQLite database with version {sqlite3.sqlite_version} successfully.")
    #         cursor = conn.cursor()
    # except sqlite3.OperationalError as e:
    #     print("Failed to open database:", e)

    sql_region = '''
    WITH RankedCountries AS (
        SELECT 
            Countries_by_GDP.Country,
            Countries_by_GDP.GDP_USD_bilion,
            B.Region,
            ROW_NUMBER() OVER (PARTITION BY B.Region ORDER BY GDP_USD_bilion DESC) AS Rank
        FROM 
            Countries_by_GDP
        INNER JOIN 
            Region_Category AS B
        ON 
            Countries_by_GDP.Country = B.Country
    )
    SELECT 
        Region,
        ROUND(AVG(GDP_USD_bilion), 2) AS Avg_GDP
    FROM 
        RankedCountries
    WHERE 
        Rank <= 5
    GROUP BY 
        Region;
    '''
    df_region = pd.read_sql_query(sql_region, conn)

    sql_gdp = '''
    SELECT Country, GDP_USD_bilion 
    FROM Countries_by_GDP
    WHERE GDP_USD_bilion > 100
    ORDER BY GDP_USD_bilion DESC
    '''

    df_gdp = pd.read_sql_query(sql_gdp, conn)
    
    print(f"{'GDP Over 100B USD':-^34}")
    print()
    print(df_gdp)
    print()
    print(f"{'Average GDP of Each Region':-^44}")
    print()
    print(df_region)

#========================================================================================

class Executer:
    conn = None
    old_data_request = ''
    REFINED_DATA = None
    old_data = None
    
    def __init__(self, conn:sqlite3.Connection, old_data_request:str = ''):
        self.conn = conn
        self.old_data_request = old_data_request
        self.REFINED_DATA = None
        self.old_data = None
        
    #====================================================================================        
    
    @logging_time
    def do_Extract(self,):
        if self.old_data_request: # db에 없는 데이터를 요청 시
            print(f"Fetching {self.old_data_request.split('-')[0]} Data From IMF API ...")
            E = Extract()
            # API로 받은 데이터는 정제된 정제된 데이터 형식과 일치하므로 바로 Load로 보낸다.
            self.old_data = E.data_from_IMF(self.old_data_request.split('-')[0])

        else:
            E = Extract() 
            wiki_html = url_validation_check(E.WIKI_URL) # 웹 페이지 추출
            # self.wiki_data = E.collect_data(wiki_html) # 데이터 수집
            E.save_json(wiki_html) # JSON 저장
        
    #====================================================================================
    
    @logging_time
    def do_Transform(self, ):
        
        T = Transform()
        T.refine_data()
        self.REFINED_DATA = T.make_DataFrame(T.country, T.gdp) # 데이터 정제 후 데이터프레임 반환
        
    #====================================================================================    
    
    @logging_time 
    def do_Load(self, latest_log:str = ''):
        # dataframe = REFINED_DATA
        latest_log = latest_log
        c = self.conn.cursor()
        # tables = c.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        
        
                
        if not self.old_data_request:
        # 1. 최신 데이터를 백업하는 상황
            print("최신 데이터를 백업")
            L = Load(self.REFINED_DATA, self.conn, log=latest_log)
            # if 'Region_Category' not in tables:
                # url = 'https://www.imf.org/external/datamapper/region.htm#sea'
                # L.save_Region_to_DB(region_categorize(url_validation_check(url)))
            L.latest_data_backup(conn=self.conn)
            L.save_GDP_to_DB()
        
        else:
        # 2. 과거 데이터를 추가하는 상황
            print("과거 데이터를 추가")
            L = Load(self.REFINED_DATA, self.conn, self.old_data_request)
            L.frame = self.old_data
            # if 'Region_Category' not in tables:
            #     url = 'https://www.imf.org/external/datamapper/region.htm#sea'
            #     L.save_Region_to_DB(region_categorize(url_validation_check(url)))            
            L.add_past_data(self.conn)
        
#========================================================================================
'''
TODO: 
    : 갱신 시 오래된 데이터 따로 빼기
'''
if __name__ == "__main__":
    
    pattern = r'^\d{4}(-[1-2])?$'
    while True: # 과거 데이터 출력 여부
        print("최신 데이터를 원하시면 엔터를,")
        print("과거 데이터를 원하시면 해당 년도(1980 ~ )와 상/하반기 구분을 입력하세요 yyyy-1 | yyyy-2")
        print("해당 년도의 데이터가 1건 뿐인 경우 그것을 출력합니다.")
        needs = input("입력: ")
        if needs == '' or bool(re.match(pattern, needs)):
            break
    
    if not logger.handlers:
        # 사용자 정의 Formatter
        formatter = logging.Formatter(
            fmt='%(asctime)s, %(message)s',
            datefmt='%Y-%B-%d-%H-%M-%S'  # 원하는 날짜 포맷
        )

        # 핸들러 생성 및 설정
        handler = logging.FileHandler(log_file_path)
        handler.setFormatter(formatter)

        # 로거 설정
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
    fp = get_last_valid_log_with_position(log_file_path)

    buffer, fp = get_latest_log(log_file_path, fp)

    while True: # 가장 마지막으로 수행 완료된 Load 프로세스 로그 탐색
        if buffer == '':  # 로그가 비어 있으면 종료
            print("버퍼가 비었다.")
            # print("로그 끝에 도달했지만 조건에 맞는 항목을 찾지 못했습니다.")
            break

        # 최신 로그에서 `마지막으로 수행된 프로세스`와 `프로세스 완료 여부` 추출
        try:
            completion, process = buffer.split(',')[-2:]  # 로그가 예상 형식일 경우
        except ValueError:
            print(f"잘못된 로그 형식: {buffer}")
            break

        # 조건 충족 시 종료
        if completion == 'Finished' and process == 'do_Load':
            print(f"조건을 충족하는 로그 발견: {buffer}")
            break

        # 이전 로그 탐색
        buffer, fp = get_latest_log(log_file_path, fp)
        
    try:    # check DB Connection
        print("Connect DB ...")
        
        with sqlite3.connect('World_Economies.db') as conn:
            print(f"Opened SQLite database with version {sqlite3.sqlite_version} successfully.")
            c = conn.cursor()

    except sqlite3.OperationalError as e:
        print("Failed to open database:", e) 
          
    save_Region_to_DB(conn, region_categorize(url_validation_check('https://www.imf.org/external/datamapper/region.htm#sea')))      

    # 과거 데이터 요청 시
    if needs != '':
        # DB에 있는지 먼저 확인
        print("Checking Past Data ...")
        
        # 없다면?
        if not check_columns_exist(conn, db_path, needs, ): 
            print("Fetching Past Data ...")
            runner = Executer(conn=conn, old_data_request=needs)
            runner.do_Extract()
            runner.do_Load()
            conn.commit()
            conn.close()
            #  시각화
        
        # 있다면
        # 시각화
        
              
    # 최신 데이터 요청 시          
        # 오래된 데이터 -> 갱신 필요  
    elif needs == '' and not is_DB_Latest(buffer):  
        print("DB is outdated: Start Update ...")

        runner = Executer(conn = None) # Load process 전 까진 DB 연결할 일이 없다.
        runner.do_Extract()
        # print("Extracted")
        runner.do_Transform()
        # print("Transformed")
        
        runner.conn = conn
        runner.do_Load(latest_log=str(datetime.datetime.now().strftime("%Y-%B-%d-%H-%M-%S"))) # back-up & update
        # print("Loaded")
        
        visualize_with_SQL(conn)
        
        conn.commit()
        conn.close()
        
        # 최신 데이터 -> 갱신 과정 없이 데이터 제공
    else: 
        print("You're looking latest DB")

        visualize_with_SQL(conn)
    
        
    
  