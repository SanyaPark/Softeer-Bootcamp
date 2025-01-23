# W3M1 - Hadoop Single-Node Cluster on Docker

---
## Docker
**Docker 이미지 빌드**
```bash
docker build -t vs501kr/softeer:hadoop_v1.3 .
```

**컨테이너 실행**
```bash
docker-compose up -d
```

**실행중인 컨테이너 터미널에 접속**
```bash
docker exec -it hadoop-single-node-cluster /bin/bash
```
---
## HDFS 작업
**HDFS에 디렉토리 생성**
```bash
hdfs dfs -mkdir /sample_dir
```

**로컬에 파일 생성 → HDFS의 디렉토리에 업로드 및 검색**
```bash
# 파일 생성
echo "hello world" >> hi.txt

# HDFS에 업로드
hdfs dfs -put hi.txt /sample_dir/

# 업로드 된 파일 검색
hdfs dfs -ls /sample_dir/
```

**웹 UI에서 상태 확인**
브라우저 → ```localhost:9870```에 접속