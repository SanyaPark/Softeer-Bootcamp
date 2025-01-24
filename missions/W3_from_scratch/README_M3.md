# W3M3 - Word Count using MapReduce

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

### 로컬 파일 시스템에서 HDFS로 전자책 파일 업로드 및 확인
```bash
# 전자책 파일이 있는 디렉토리
cd /home/hadoopuser

# HDFS 디렉토리 생성
hdfs dfs -mkdir /M3

# 전자책 파일을 HDFS에 업로드
hdfs dfs -put 1984.txt /M3

# HDFS에서 업로드 된 전자책 파일 확인
hdfs dfs -ls /M3
```

### MapReduce 작업 수행
```bash
# MapReduce 결과물 반환 디렉토리가 미리 존재하면 안됨. 
hdfs dfs -rm /M3/output

# MapReduce 작업 실행
hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-*.jar wordcount /M3/1984.txt /M3/output

# 결과물 확인: part-r-00000 파일이 생성됨
hdfs dfs -ls /M3/output
```

**터미널에 작업 결과물 출력**
```bash
hdfs dfs -cat /M3/output/part-r-00000
```

**출력 마지막 부분**
``` sh
...
youthful	5
youthfulness	1
youths	4
yp	1
zeal,	1
zealot	1
zealous	1
zig-zagging	1
zip	1
zipper	1
zoom	1
```
---
### 결과물이 .txt가 아니네요??
당황하지 마세요! ```part-r-00000``` 같은 출력 파일은 사실 **텍스트 파일** 형식입니다. 다만 이름에 .txt 확장자가 없을 뿐, 내용을 확인하면 텍스트 데이터로 이루어져 있습니다.

**확장자가 없지만 텍스트 파일인 이유**
* **HDFS에서 생성된 출력 파일**은 단순히 확장자가 없는 **텍스트 파일**입니다.
* 파일 내용을 확인할 수 있는 ```cat``` 명령어가 동작한다면, 확장자 여부는 중요하지 않습니다. ```.txt``` 확장자를 추가하는 것은 가독성과 관리 용이성을 위한 선택일 뿐입니다.
#### +
출력 파일을 로컬로 복사 및 이름 변경(→ result.txt)
```bash
hdfs dfs -get /M3/output/part-r-00000 ./result.txt
```
hdfs 내에서 파일 이름 변경(→ result.txt)
```bash
hdfs dfs -mv /M3/output/part-r-00000 /M3/output/result.txt
```