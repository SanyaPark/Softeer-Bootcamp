#!/bin/bash

# NameNode 초기화 확인 및 포맷 - 기존 NameNode 초기화 방지
if [ ! -d "/hadoop_data/dfs/namenode" ]; then
    echo "Formatting HDFS NameNode..."
    $HADOOP_HOME/bin/hdfs namenode -format
else
    echo "NameNode already formatted. Skipping format step."
fi

# Start HDFS services
start-dfs.sh

# Wait for NameNode to be ready
sleep 5

# HDFS 디렉토리 생성 및 초기화
hdfs dfs -mkdir -p /user/root
hdfs dfs -mkdir -p /example
hdfs dfs -put /usr/local/hadoop/etc/hadoop/core-site.xml /example/

# Tail to keep the container running
tail -f /dev/null
