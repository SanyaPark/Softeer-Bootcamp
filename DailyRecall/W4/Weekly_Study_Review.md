# Spark 🌠

### spark-submit 실행 스크립트 작성
🔹 작성된 `spark-submit.sh` (`/home/sparkuser/spark-submit.sh`)
```bash
#!/bin/bash

# Spark 애플리케이션 실행
$SPARK_HOME/bin/spark-submit \
    --master spark://spark-master:7077 \
    --deploy-mode client \
    --executor-memory 1G \
    --total-executor-cores 2 \
    /home/sparkuser/pi.py
```

✅ 코드 설명
* --master spark://spark-master:7077 <br>→ Spark Standalone 클러스터의 마스터 URL, 7077은 master-worker 소통 창구
  * `--master` 플래그는 접속할 클러스터의 주소를 지정해 주는데, 여기서 쓴 `spark://URL`은 스파크의 단독 모드를 사용한 클러스터를 의미한다.    
* --deploy-mode client → 로컬에서 실행 (client mode)
* --executor-memory 1G → 실행할 때 1GB 메모리 할당
* --total-executor-cores 2 → 2개의 실행 코어 사용
* /home/sparkuser/pi.py → 실행할 Python 코드

`spark://host:port`
spark 단독 클러스터의 지정한 포트로 접속한다. 기본적으로 spark 단독 마스터들은 7077 포트를 쓴다.

`yarn`
YARN 클러스터에 접속한다. YARN에서 실행할 때는 클러스터 정보를 갖고 있는 하둡 설정 디렉토리를 HADOOP_CONF_DIR 환경 변수에 설정해 주어야 한다.
<br>

### Spark가 CSV 파일 대신 폴더를 생성하는 이유!
Spark의 `df.write.csv("경로")` 방식은 단일 파일이 아니라 여러 개의 파티션 파일을 포함하는 폴더를 생성하는 구조.
👉 즉, Spark는 `pi_result.csv`라는 폴더를 만들고 그 안에 여러 개의 CSV 파일을 저장한 것.

📌 이렇게 만들어진 폴더 내부에 있는 파일들 설명:
`_SUCCESS` → Spark 작업이 정상적으로 완료되었음을 나타내는 빈 파일
`.crc` 파일들 → HDFS(혹은 로컬 파일 시스템)의 데이터 무결성 체크용

<br>

### 단일 CSV 파일로 저장하는 방법
Spark에서 단일 파일로 저장하려면 `.coalesce(1)`을 사용!
``` python
    # ✅ 단일 CSV 파일로 저장
    df.coalesce(1).write.mode("overwrite").option("header", "true").csv(output_dir)
```
---
## 새로운 자료구조: PARQUET?
### 1️⃣ PARQUET 데이터 타입이란?
Apache Parquet은 컬럼 지향(columnar) 저장 형식의 데이터 파일 포맷이야.
주로 **분산 데이터 처리 (예: Apache Spark, Hadoop, Presto, Hive)**에서 효율적으로 사용돼.

Parquet은 JSON, CSV 같은 기존 포맷과 다르게, 컬럼 단위로 데이터를 저장해.
즉, 데이터를 **행(row)**이 아니라 컬럼(column) 단위로 정렬하고 압축하는 방식이야.

### 2️⃣ PARQUET이 왜 등장했을까?
기존의 CSV, JSON, Avro 같은 행 지향(row-oriented) 포맷은 빅데이터 처리에서 비효율적이었어.
이런 문제를 해결하기 위해 Google의 Dremel 논문(2010)을 기반으로 Parquet이 개발됐어.

**기존 포맷의 문제점:**
1. 필요 없는 데이터까지 읽어야 함 → 속도가 느림 ❌
2. 압축 효율이 낮음 → 디스크 사용량 증가 ❌
3. 대량의 데이터에서 특정 컬럼만 읽고 싶어도 전체 스캔이 필요함 ❌
<br>

**Parquet의 해결책:**

    ✅ 컬럼 단위 저장 → 필요한 컬럼만 읽을 수 있음 (IO 비용 감소)
    ✅ 같은 데이터 유형이 연속적으로 저장됨 → 압축률 증가
    ✅ 효율적인 인덱싱 → 쿼리 속도 향상
    ✅ 분산 시스템 최적화 → 파일을 분할하여 병렬처리 용이
    ✅ Schema 지원 → Schema 정보를 포함하고 있어 데이터 타입 유지가 가능
<br>

### 3️⃣ 기존 데이터 포맷과 Parquet 비교
|포맷	|저장 방식	|장점	|단점   |
|---    |---        |---    |---    |
|CSV	|행(row) 기반	|텍스트 기반으로 간단	|크기 큼, 느림, Schema 없음|
|JSON	|행(row) 기반	|구조적 데이터 저장 가능	|크기 큼, 느림, 쿼리 비효율|
|Parquet|	컬럼(column) 기반	|빠른 쿼리, 고압축률	|작은 데이터셋에는 부적합|

<br>

### 4️⃣ 결론: 언제 Parquet을 써야 할까?
    ✅ 빅데이터 분석 & 쿼리 최적화가 필요할 때
    ✅ Spark, Hadoop, Presto 같은 분산 시스템에서 사용할 때
    ✅ 압축률을 높여 저장 공간을 절약하고 싶을 때
    ❌ 작은 데이터(1MB 미만)에서는 CSV보다 효율적이지 않을 수도 있음!

---
## PySpark와 Jupyter notebook
호스트-컨테이너의 폴더가 볼륨 마운트 되었고, vscode의 DEV-CONTAINERS 확장이 설치되었다면<br> 컨테이너 내부에서 8888포트 개방 없이 바로 작업 가능
<br>

### Dockerfile에서 pip3 install로 PySpark 설치가 안돼요
⚠️`externally-managed-environment` 오류
이 오류는 **Debian 계열(Ubuntu 포함)에서 최신 버전의 Python(특히 Python 3.12 이후)** 을 사용할 때 발생하는 문제.

📌 **오류의 원인**
Debian/Ubuntu에서는 기본 Python 환경을 보호하기 위해 `pip install`을 막아둠.
`pip install`을 실행하려 하면 "This environment is externally managed" 라는 메시지가 뜨면서 패키지 설치가 안 됨.

**📌 왜 이런 변화가 생겼나?**
Debian 12 (bookworm) 이후부터 시스템 Python 패키지와 pip 패키지가 충돌하는 걸 방지하기 위해 기본 Python 환경을 관리형(Externally Managed)으로 설정했어.
그래서 `pip install`을 사용하려면 가상 환경(venv)이나 `pipx`를 이용해야 함.
<br>

#### 해결 방법
✅ 1️⃣ (추천) `--break-system-packages` 옵션 추가하기 (간단함)
→ Debian의 기본 보호 정책을 우회해서 패키지를 설치한다.
```dockerfile
RUN pip3 install --break-system-packages --no-cache-dir pyspark findspark jupyter
```
✅ 2️⃣ (추천) venv를 사용해서 가상환경 내에서 설치하기 (안정적)
✅ 3️⃣ pipx를 이용해서 패키지 설치하기 (공식 Debian 정책)
⎿ 💡 이 방법은 공식적으로 권장되지만, PySpark가 정상적으로 동작하는지 추가 테스트가 필요함.
