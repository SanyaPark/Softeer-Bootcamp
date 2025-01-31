#!/bin/bash

# Run Containers
docker-compose up -d

# 파이썬 파일은 /home/sparkuser와 volume mount 된 workspace에 있으므로
docker exec -it spark-master chown +x /home/sparkuser/pi.py
docker exec -it spark-master chown +x /home/sparkuser/pi_og.py

docker exec -it spark-master ./spark-submit.sh
# OR
# docker exec -it spark-master \
#     $SPARK_HOME/bin/spark-submit \
#     --master spark://spark-master:7077 \
#     --deploy-mode client \
#     --executor-memory 1G \
#     --total-executor-cores 2 \
#     ./pi.py
