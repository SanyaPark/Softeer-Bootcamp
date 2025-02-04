from pyspark.sql import SparkSession
# from pyspark.sql.functions import to_date, col, count, sum
from functools import reduce # <-- 여러 DataFrame을 합칠 때 사용
import datetime, json
import pandas as pd

def is_valid_2024(row):
    try:
        dt_val = row['tpep_pickup_datetime']
        if isinstance(dt_val, str):
            dt = datetime.strptime(dt_val, "%Y-%m-%d %H:%M:%S")
        else:
            dt = dt_val
        return dt.year==2024
    except Exception as e:
        return False
    
# SparkSession
spark = SparkSession.builder \
        .appName('TLC 2024') \
        .getOrCreate()
        
tlc_path = "TLC/2024/"

rdd_list = []

# 2024 데이터는 12월이 없음
for month in range(1, 12):
    month_str = f"{month:02d}"
    file_path = f"{tlc_path}yellow_tripdata_2024-{month_str}.parquet"
    
    df_month = spark.read.parquet(file_path)
    
    rdd = df_month.rdd
    rdd_list.append(rdd)

    print(f"Loaded data for month {month_str} from {file_path}")
    
# 모든 달의 RDD를 하나로 합치기 (스키마가 동일해야만 union 사용 가능)
if rdd_list:
    combined_rdd = reduce(lambda rdd1, rdd2: rdd1.union(rdd2), rdd_list)
    print("All monthly data combined Successfully")
else:
    print("Something's wrong with combining data")
    
# 요금 0 및 2024년 데이터가 아닌 것들 필터링
filtered_rdd = combined_rdd.filter(lambda row: row['fare_amount'] is not None and row['fare_amount'] > 0)
filtered_rdd = filtered_rdd.filter(is_valid_2024)    

# 총 여행 횟수, 수익과 평균 여행 거리 계산
fare_dist_total = filtered_rdd.map(lambda row: (row['fare_amount'], row['trip_distance'], 1)) \
            .reduce(lambda a, b: (a[0] + b[0], a[1] + b[1], a[2] + b[2]))
            
total_fare, total_dist, total_trips = fare_dist_total
avg_dist = total_dist / total_trips if total_trips else 0

print("총 여행 횟수: ", total_trips)
print("총 수익: ", round(total_fare, 2))
print("평균 여행 거리", round(avg_dist, 2))

# 위 데이터를 .json으로 저장
total_data = {
    "Total trips" : total_trips,
    "Total fare"  : total_fare,
    "Avg trip distance" : avg_dist
}
with open('2024_total_trip_data.json', 'w') as f:
    json.dump(total_data, f, indent=4)
    
# 일자 별 데이터로 그룹화 및 일별 요금, 여행 횟수 집계    
daily_rdd = filtered_rdd.map(lambda row: (
    row['tpep_pickup_datetime'].strftime("%Y-%m-%d"), # --> key (datetime)
    (row['fare_amount'], 1)) # --> value (fare, count)
)

daily_metrics_rdd = daily_rdd.reduceByKey(lambda a, b: (
                    a[0] + b[0], # fare amount 합계
                    a[1] + b[1], # trip count 합계
)).sortByKey()

daily_records = {
    "Date":[],
    "Trips":[],
    "Daily Fare":[]
}
for date, (total_fare, total_count) in daily_metrics_rdd.collect():
    daily_records['Date'].append(date)
    daily_records['Trips'].append(total_count)
    daily_records['Daily Fare'].append(total_fare)

# 날짜별 기록을 spark DataFrame으로 변환 및 csv로 저장
pydf = pd.DataFrame(daily_records)
spark_df = spark.createDataFrame(pydf)
spark_df.printSchema()    

spark_df.coalesce(1).write.mode("overwrite").csv("./output/2024_daily_data")

# 스파크 종료
spark.stop()