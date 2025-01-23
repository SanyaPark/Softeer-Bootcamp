#!/bin/bash

echo "Stopping Hadoop services based on NODETYPE=$NODETYPE..."

if [ "$NODETYPE" == "master" ]; then
  echo "Stopping Hadoop Distributed File System (HDFS)..."
  hadoop-daemon.sh stop namenode
  hadoop-daemon.sh stop secondarynamenode
  
  echo "Stopping YARN ResourceManager..."
  yarn-daemon.sh stop resourcemanager

elif [ "$NODETYPE" == "worker" ]; then
  echo "Stopping HDFS DataNode..."
  hadoop-daemon.sh stop datanode
  
  echo "Stopping YARN NodeManager..."
  yarn-daemon.sh stop nodemanager
else
  echo "NODETYPE not recognized. Please set NODETYPE to 'master' or 'worker'."
  exit 1
fi
