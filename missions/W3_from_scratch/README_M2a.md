# W3M2a - Hadoop Multi-Node Cluster on Docker

## Folder Structure:
```

```
## 도커 이미지 빌드 및 컨테이너 실행

**Image Build**
```bash
docker build -t vs501kr/softeer:hadoop_scratch_v1.0 .
```

**Docker Compose**
```bash
docker-compose up -d
``` 
---
## HDFS & MapReduce 작업 수행
docker-compose 파일로부터 호스트의 ```./workspace```와 
볼륨 마운트 된 NameNode의 ```/home/hadoopuser``` 폴더에 작업에 필요한 파일 준비

**마스터노드 터미널에 접속**
```bash
docker exec -it namenode /bin/bash
```

### 로컬 파일 시스템에서 HDFS로 샘플 파일 업로드 및 확인
```bash
# 샘플 파일이 있는 디렉토리
cd /home/hadoopuser

# HDFS 디렉토리 생성
hdfs dfs -mkdir /sample_dir

# 샘플 파일을 HDFS에 업로드
hdfs dfs -put lorem_ipusm.txt /sample_dir/

# HDFS에서 업로드 된 샘플 파일 확인
hdfs dfs -ls /sample_dir
```
### MapReduce 작업 수행
```bash
# MapReduce 결과물 반환 디렉토리가 미리 존재하면 안됨. 
hdfs dfs -rm /sample_dir/output

# MapReduce 작업 실행
hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-*.jar wordcount /sample_dir /sample_dir/output
```

**터미널에 작업 결과물 출력**
```bash
hdfs dfs -cat /sample_dir/output/part-r-00000
```
