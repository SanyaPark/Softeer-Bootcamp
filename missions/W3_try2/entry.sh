#!/bin/bash

# SSH 서비스 시작
service ssh start


# HDFS 네임노드 초기화 확인 및 포맷
# if [ ! -f $HADOOP_HOME/hadoop-data/hdfs/namenode/current/VERSION ]; then
if [ ! -f /usr/local/hadoop/tmp/dfs/name/current/VERSION ]; then

    echo "Formatting HDFS NameNode..."
    # su -c "$HADOOP_HOME/bin/hdfs namenode -format -force" hdfs
    $HADOOP_HOME/bin/hdfs namenode -format -force
else
    echo "HDFS NameNode already formatted."
fi

# HDFS 및 YARN 서비스 시작
echo "Starting HDFS services..."
# su -c "$HADOOP_HOME/sbin/start-dfs.sh" hdfs
$HADOOP_HOME/sbin/start-dfs.sh

# 컨테이너 실행 유지
echo "Hadoop is up and running!"
tail -f /dev/null
