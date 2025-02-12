#!/bin/bash

# Format HDFS if namenode
if [ "$HOSTNAME" == "namenode" ]; then
    if [ ! -f /usr/local/hadoop/tmp/dfs/name/current/VERSION ]; then
         echo "[INFO] Formatting HDFS NameNode..."
        $HADOOP_HOME/bin/hdfs namenode -format -force
        echo "[INFO] HDFS NameNode formatted successfully."
    else
        echo "[INFO] HDFS NameNode already formatted. Skipping."
    fi
fi

# Start SSH service
echo "[INFO] Starting SSH service..."
service ssh start

# Start Hadoop services based on hostname
echo "[INFO] Starting Hadoop services for $HOSTNAME..."
if [ "$HOSTNAME" == "namenode" ]; then
    echo "[INFO] Starting HDFS NameNode..."
    hdfs namenode
elif [[ "$HOSTNAME" == datanode* ]]; then
    echo "[INFO] Starting HDFS DataNode..."
    hdfs datanode
elif [ "$HOSTNAME" == "resourcemanager" ]; then
    echo "[INFO] Starting YARN ResourceManager..."
    yarn resourcemanager
elif [[ "$HOSTNAME" == nodemanager* ]]; then
    echo "[INFO] Starting YARN NodeManager..."
    yarn nodemanager
else
    echo "[WARNING] Unknown hostname $HOSTNAME. No services started."
fi

# Keep the container running
echo "[INFO] Container setup complete. Tailing logs to keep container running..."
tail -f /dev/null