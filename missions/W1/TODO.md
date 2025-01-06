# ETL Pipeline
-------------------
Region? 제공된 위키 사이트 하단에 있는 Region을 사용해야 하는지
이 [Region](https://en.wikipedia.org/wiki/United_Nations_Regional_Groups)을 사용해야 하는지...

## 기본 사항
- 주석 달기
- 함수화
- 필요한 모든 작업을 수행하는 '**etl_project_gdp.py**' 코드를 작성하세요.
- 해당 코드는 재사용이 가능해야 함 
- GDP 단위는 1B USD, 소수점 2자리 까지만 표기 ✔

## 팀 활동 요구사항
- IMF 홈페이지에서 직접 데이터를 가져오는 방법은 없을까요? 어떻게 하면 될까요?

- 만약 데이터가 갱신되면 과거의 데이터는 어떻게 되어야 할까요? <br>
  과거의 데이터를 조회하는 게 필요하다면 ETL 프로세스를 어떻게 변경해야 할까요?

## Logging
- ETL 각 프로세스 별 시작 / 끝을 로그에 기록
- 로그는 기존 파일에 append
- log format: Y-MMM-D-H-M-S
- etl_project_log.txt 파일에 저장
  

## Extract
- 사이트 연결 확인 ✔
- GDP 테이블 추출 ✔
  - Wiki / IMF 사이트 별 추출 함수 제작 ✔
- <팀> 추출 시 마지막 로그 확인 후 갱신 주기가 지났을 경우 추출 
  

## Transform
- 결측치 및 하이퍼링크 등 불필요한 정보 제거 ✔
- GDP 내림차순 정렬 ✔
- 단위 재조정 (1M -> 1B $) ✔
- 100B USD 기준 컷 ✔
- 아래의 항목은 화면 출력으로 넘겨도 될 듯? 
  - Region 별 분류
  - top 5 평균 구하기 


## Load
- Transform된 데이터프레임 저장 (JSON type) ✔
- <팀> 과거 데이터 조회가 가능하도록 하려면?
  - 테이블 명이 지정되었으므로 과거 데이터를 저장하려면 Country, GDP_USD_billion 컬럼을 포함하는 상위 컬럼 '날짜'? 항목을 추가한다 
  - 