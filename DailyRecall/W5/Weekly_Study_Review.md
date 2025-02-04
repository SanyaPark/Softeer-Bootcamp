# Spark

## Transformation vs Action

### Transformation
**특징**
* Lazy Evaluation:
 Transformation은 호출해도 즉시 실행되지 않고, 새로운 RDD의 **계산 그래프(DAG)**를 생성하는 역할만 합니다.
<br>

* 새 RDD 생성: 
기존 RDD를 바탕으로 새 RDD를 만듧니다.
<br>

* 재사용 가능: 
여러 Transformation을 연쇄해서 호출할 수 있으며, 실제 데이터 처리(계산)는 Action이 호출될 때 수행됩니다.
<br>

* 예시)
  * `map()`, `filter()`, `groupByKey()`, `sortByKey()`, `union()`, `reduceByKey()` 
  (주의: reduceByKey는 내부적으로 key별 집계를 하지만, 결과는 새로운 RDD이므로 Transformation입니다)

### Action
**특징**
* 즉시 실행:
Action은 호출되면, 그때까지 누적된 Transformation 연산들을 실행하여 실제 결과를 드라이버로 반환하거나 외부 저장소에 저장합니다.
<br>

* 최종 결과 반환: 
보통 최종 결과 값(숫자, 리스트 파일 등)을 리턴합니다.
<br>

* 예시)
`collect()`, `reduce()`, `count()`, `take(n)` 등
---


## RDD vs spark DataFrame

### RDD (Resilient Distributed Dataset)
* low-level 추상화
RDD는 분산 데이터를 다루기 위한 기본 단위로, 데이터의 불변성을 보장하며 분산 시스템에서의 장애 복구 능력을 갖추고 있습니다.
<br>

* 함수형 프로그래밍 스타일
`map`, `filter`, `reduce` 등 함수형 연산이 제공되어, 데이터 처리 로직을 세밀하게 제어할 수 있습니다.
<br>

* 최적화 부족
Catalyst 옵티마이저가 없기 때문에, 복잡한 쿼리나 조인, 집계 연산에서 DataFrame보다 성능 최적화가 어려울 수 있습니다.

### spark DataFrame
* high-level 추상화
SQL 테이블과 유사한 구조(스키마)를 가지며, 명시적인 스키마 정의와 열 단위의 연산이 가능하여 데이터 처리 과정을 더 직관적으로 이해할 수 있습니다.
<br>

* Catalyst Optimizer 활용
Spark SQL의 Catalyst 옵티마이저를 활용해 쿼리 실행 계획을 최적화하기 때문에, 복잡한 연산에서도 성능 면에서 우위를 가집니다.
<br>

* 내장 함수 지원
다양한 집계, 변환, 조인 등의 내장 함수들이 있어 코드가 간결해지고 유지보수가 쉬워집니다.
<br>

* 편의성
SQL과 유사한 문법을 사용할 수 있고, DataFrame API를 통해 시각적, 분석적인 작업에 매우 적합합니다.

---

## M1 관련
<br>

### 파일 읽기 및 확인과 병합
`spark.read.parquet(file_path)`를 사용해 Parquet 파일을 **DataFrame**으로 읽습니다.
`functools.reduce` 함수와 `union()` 메서드를 활용하여 리스트에 있는 DataFrame들을 순차적으로 병합합니다.
스키마가 동일해야 union이 문제 없이 작동합니다.
`printSchema()`와 `show()` 메서드를 통해 데이터의 스키마와 일부 데이터를 확인합니다.


### 고려하면 좋을 것들:
**파티셔닝 고려:**
합쳐진 DataFrame에 대해 데이터를 파티셔닝하면, 특히 날짜별 분석(예: daily metrics)이나 대용량 데이터 처리 시 병렬 처리 성능이 향상됩니다.
```python
# 예시: 날짜 컬럼을 기준으로 파티셔닝
combined_df = combined_df.repartition("pickup_date")
```

**캐시 사용 (RDD & DataFrame):**
데이터 클리닝 및 여러 번의 집계 연산을 수행할 때, 중간 결과를 캐시하여 불필요한 재연산을 줄일 수 있습니다.
만약 동일한 RDD에 대해 여러 Action(예: `count()`, `collect()`, `saveAsTextFile()`)을 수행하는 두 개의 별도 작업(job)이 있다면, 캐싱을 해두면 처음 한 번의 계산 후에 RDD 결과를 메모리에 보관하게 됩니다. 
이후의 Action들은 캐시된 데이터를 사용하게 되어 재계산을 피할 수 있습니다.
```python
combined_df.cache()  # 이후 여러 번 사용할 때 성능 향상에 도움
```

**DataFrame에서 SQL 표현 사용:**
복잡한 집계나 조인을 SQL 표현으로 풀어내면 가독성이 좋아지고, Catalyst 옵티마이저의 혜택을 극대화할 수 있습니다.
```python
combined_df.createOrReplaceTempView("trips")
daily_revenue = spark.sql("""
    SQL QUERY ~~~
""")
daily_revenue.show()
```

### 12달치 데이터를 어떻게 처리하는게 좋을까?
1. 전체 데이터를 합친 후 집계 작업 수행
* 장점:
집계, 그룹바이(groupBy) 등의 작업을 한 번에 전체 데이터에 대해 수행할 수 있음.
전체 데이터를 대상으로 작업하기 때문에 전역적인 집계 결과를 쉽게 계산할 수 있음.
<br>

* 방법:
12달치 각 Parquet 파일을 읽어서 DataFrame으로 만든 뒤, RDD로 변환한 후에 union(합치기)합니다.
합쳐진 RDD에서 필요한 전처리 및 집계 작업을 수행합니다.
<br>

2. 개별 파일에 대해 전처리 후 집계 결과를 합치는 방식
* 장점:
파일별로 독립적인 전처리 작업을 수행한 후, 파일 단위의 집계 결과를 계산할 수 있습니다.
각 파일의 데이터량이 매우 클 경우, 중간에 부분 집계를 미리 계산해놓고 나중에 전체 집계 결과를 합치는 방식으로 네트워크 I/O나 메모리 사용을 최적화할 수 있습니다.
<br>

* 방법:
각 월별 RDD에 대해 필요한 클리닝, 변환 작업을 수행한 후, 해당 RDD에서 집계 결과(예: 총 fare와 총 건수)를 계산합니다.
이후 각 월별 집계 결과를 다시 리듀스(예: reduce 함수)하여 전체 집계 결과를 도출합니다.

### map 연산에 대한 설명
```python
mapped_rdd = fare_filtered_rdd.map(lambda row: (row['fare_amount'], 1))
```
* 변환 내용:
  * lambda row: (row['fare_amount'], 1) 부분은 각 행에서 'fare_amount' 컬럼의 값을 추출하고, 그 값과 숫자 1을 튜플로 만드는 역할을 합니다.
  * 결과적으로, 각 행은 (fare_amount, 1) 형태의 튜플로 변환됩니다.
  * 예를 들어, 만약 한 행의 'fare_amount' 값이 15.50이라면, 해당 행은 (15.50, 1)로 변환됩니다.
<br>

* 왜 이런 변환을 하나요?
  * 보통 이와 같이 변환하는 이유는 나중에 reduce나 reduceByKey 같은 연산을 통해 **총 수익(sum of fare_amount)**과 **총 트립 수(count)**를 쉽게 계산하기 위함입니다.

  * (fare_amount, 1) 튜플을 여러 개 합치면, 첫 번째 요소는 총 요금의 합, 두 번째 요소는 총 건수를 나타내게 됩니다.

### 분산 처리와 태스크(task) 개수에 대한 설명
`mapped_rdd.count()` 실행 시 11개 stage와 110개의 task가 진행되었다고 하셨는데, 이에 대해 아래와 같이 설명할 수 있습니다.

* 분산 처리 여부:
Spark에서는 RDD나 DataFrame이 이미 클러스터의 여러 파티션(partition)으로 분산되어 있습니다.

  * mapped_rdd가 생성될 때, 이 RDD는 기본 파티셔닝을 따르게 됩니다.
  * 작업(action)이 실행되면, 각 파티션에 대해 병렬로 task가 실행됩니다.

* 명시적인 parallelize가 필요한가?

  * 필요 없음:
  이미 데이터가 파일로부터 로드되거나, DataFrame에서 RDD로 변환될 때 기본 파티셔닝이 설정되므로, 별도로 `sc.parallelize()`를 사용하여 데이터를 분산시키지 않아도 Spark는 자동으로 데이터를 여러 파티션에 나눕니다.

  * `parallelize`는 일반적으로 로컬 리스트나 컬렉션을 분산 처리할 때 사용하는 메서드입니다.
    파일로부터 로드한 데이터의 경우, Spark가 기본적으로 분산 처리를 수행합니다.

### .reduce 함수의 작동 과정
reduce 함수는 RDD의 모든 요소를 하나로 합치는 작업을 수행합니다. 
이 과정에서 `lambda a, b: (a[0] + b[0], a[1] + b[1])` 람다 함수가 두 개의 요소를 받아서 합치는 역할을 합니다.

**reduce 함수와 lambda 함수의 동작 원리**
reduce 함수는 RDD의 모든 요소를 **이진 연산(binary operation)**을 사용해서 하나의 값으로 축소합니다. 
이때 람다 함수의 인자 a와 b는 RDD에서 꺼낸 **두 개의 요소 또는 누적 결과**와 **다음 요소**를 의미합니다.

* a와 b의 의미:
처음에는 각각 RDD의 두 개의 개별 (fare_amount, 1) 튜플입니다.
이후에는 a가 누적 결과(지금까지의 총 수익과 총 트립 수)이고, b는 RDD에서 다음에 나오는 (fare_amount, 1) 튜플입니다.

### Key를 명시하지 않아도 되는 이유
이 코드에서 reduceByKey를 호출하기 전에 이미 (key, value) 형태로 데이터를 만들었기 때문이야.
Spark는 (key, value) 형태의 RDD에서 reduceByKey를 호출하면 자동으로 key를 기준으로 그룹화한 후, 그룹 내에서 reduce 연산을 수행해.

**정리:**
* reduceByKey는 항상 (key, value) 구조를 가진 RDD에서 동작해.
* key는 첫 번째 요소(위 예제에서는 날짜)이며, 같은 key를 가진 값들을 그룹화해서 연산해.
* 별도로 key를 명시하지 않아도 Spark가 첫 번째 요소를 key로 인식해 처리해줘.

### 질문 사항 
`.reduce(lambda a, b: (a[0] + b[0], a[1] + b[1], a[2] + b[2]))`를 
`from operator import add`를 이용해서
`.reduce(add)` 이렇게 해도 문제가 없을까?

> `.reduce(add)`를 사용하면, 두 개의 튜플이 연결(concatenation)되어 의도한 결과가 나오지 않습니다.


`.write().parquet("path")`으로 저장했더니 폴더와 함께 여러 파일로 쪼개져서 저장되었어.
> `.coalesce(1)`는 기존 파티션을 하나로 줄여주는 Transformation입니다. 데이터가 아주 많지 않은 경우에 적합합니다.
> 만약 데이터가 크고 여러 파일로 저장되는 것이 문제가 아니라면, 여러 .part 파일을 후처리 도구(예: Hadoop FileUtil, cat 명령어 등)를 이용해 하나의 파일로 합치는 것도 고려해볼 수 있습니다.

### Fancy 한 필터링 코드
```python
# --- Fancy한 필터링 코드 시작 ---
# 검사할 컬럼 리스트 (실제 작업에서는 필요한 컬럼들만 지정)
numeric_columns = ["int_col", "double_col", "long_col"]

# 각 컬럼에 대해 "null이 아니고" 그리고 "값이 0 이상"인 조건을 생성합니다.
conditions = [ (col(c).isNotNull()) & (col(c) >= 0) for c in numeric_columns ]

# 모든 조건을 AND(&)로 결합합니다.
combined_condition = reduce(lambda a, b: a & b, conditions)

# 조건을 만족하는 행만 남깁니다.
clean_df = df.filter(combined_condition)
```

**reduce의 동작:** <br>
`reduce`는 리스트의 첫 번째와 두 번째 요소를 받아서 lambda 함수에 전달합니다.
예를 들어, 첫 번째 조건과 두 번째 조건을 받아 `a & b` 연산을 수행합니다.
여기서 a는 첫 번째 조건, b는 두 번째 조건입니다.
`a & b`는 Spark의 Column 객체에서 제공하는 논리 연산자로, 두 조건을 AND 연산하여 결합한 새로운 조건을 반환합니다.
이후, 이 결합된 조건과 세 번째 조건이 다시 lambda 함수에 전달되어 `( (조건1 & 조건2) & 조건3 )` 형태의 하나의 조건으로 결합됩니다.
즉, reduce의 lambda 함수는 리스트의 모든 조건을 순차적으로 AND 연산으로 결합하여, **모든 조건을 동시에 만족하는 행만 남길 수 있는 단일 조건**을 만들어냅니다.

#### Timestamp 형식의 컬럼 필터링
```python
from pyspark.sql.functions import year, col

# Timestamp 컬럼 필터 조건 생성
timestamp_conditions = [
    year(col("timestamp_col1")) == 2024,
    year(col("timestamp_col2")) == 2024
]
```

### 컬럼 내림차순 보기
```python
df.orderBy(col("numeric_col").desc()).show()
```
