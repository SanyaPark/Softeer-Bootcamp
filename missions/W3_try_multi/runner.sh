#!bin/bash
# cd "$(dirname "$0")" || exit
docker exec namenode mkdir -p /code
docker cp code/. namenode:/code/
docker cp 1984.txt namenode:/data/
# 필요한 라이브러리 설치
# docker exec master pip install -r /code/require.txt

# # 데이터 가져오기
# docker exec master python /code/get_data.py

# # 데이터 hdfs에 저장
# docker exec master hdfs dfs -mkdir /data
# docker exec master hdfs dfs -put /code/data.json /data
docker exec namenode chmod 755 /code/hi.py
docker exec namenode python3 /code/hi.py
# mapreduce 수행
docker exec namenode chmod 755 /code/mapper.py
docker exec namenode chmod 755 /code/reducer.py

docker exec namenode hdfs dfs -rm -r /output
docker exec namenode hadoop jar /usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.6.jar \
    -input /data \
    -output /output \
    -mapper mapper.py \
    -reducer reducer.py \
    -file /code/mapper.py \
    -file /code/reducer.py

# 결과 가져오기
docker exec namenode hdfs dfs -ls /
docker exec namenode mkdir -p /res
docker exec namenode hdfs dfs -get /output /res
docker exec namenode rm -r /res/output
docker cp namenode:/res/output/. res/