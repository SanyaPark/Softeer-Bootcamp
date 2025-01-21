# Base image
FROM python:3.10-slim AS python-base-img
FROM ubuntu:24.04

# 환경 변수 설정
ENV HADOOP_VERSION=3.3.6
ENV PYTHON_VERSION=3.10
# apt install 시에, 발생할 수 있는 예를들어 '패키시 설치 정말 하겠습니까?', '비밀번호 입력해주세요'같은거를 무시하고 진행할 수 있다고 한다
ENV DEBIAN_FRONTEND=noninteractive 
ENV HADOOP_HOME=/usr/local/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-arm64

# 사용자 환경 변수 설정
ENV HDFS_NAMENODE_USER=hdfs
ENV HDFS_DATANODE_USER=hdfs
ENV HDFS_SECONDARYNAMENODE_USER=hdfs
ENV YARN_RESOURCEMANAGER_USER=yarn
ENV YARN_NODEMANAGER_USER=yarn

# 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    openjdk-11-jdk wget ssh rsync vim  \
    && apt-get clean

# python 관련...
WORKDIR /app
RUN \
    echo 'alias python="/usr/bin/python3"' >> /root/.bashrc && \
    echo 'alias pip="/usr/bin/pip3"' >> /root/.bashrc && \
    . /root/.bashrc

ENV PYTHON="/usr/bin/python3"
ENV PIP="/usr/bin/pip3"
    
# Hadoop 다운로드 및 설치
RUN wget https://mirrors.sonic.net/apache/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz && \
    tar xvzf hadoop-$HADOOP_VERSION.tar.gz && \
    mv hadoop-$HADOOP_VERSION hadoop && \
    rm hadoop-$HADOOP_VERSION.tar.gz \
    && chown -R root:root $HADOOP_HOME

# hdfs 및 yarn 사용자 생성
RUN groupadd hadoop \
    && useradd -r -g hadoop hdfs \
    && useradd -r -g hadoop yarn \
    && mkdir -p /hadoop-data/hdfs/namenode /hadoop-data/hdfs/datanode \
    && chown -R hdfs:hadoop /hadoop-data \
    && chmod -R 750 /hadoop-data

RUN mkdir -p /usr/local/hadoop/logs \
    && chown -R hdfs:hadoop /usr/local/hadoop/logs \
    && chown -R yarn:hadoop /usr/local/hadoop/logs \
    &&chmod -R 755 /usr/local/hadoop/logs

# # SSH 설정
# Configure SSH for passwordless communication
RUN ssh-keygen -t rsa -P "" -f /root/.ssh/id_rsa && \
    cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys && \
    chmod 600 /root/.ssh/authorized_keys
# RUN \
# RUN [ ! -f /etc/ssh/ssh_host_rsa_key ] && ssh-keygen -t rsa -P "" -f /etc/ssh/ssh_host_rsa_key || true && \
#     # rm -f /etc/ssh/ssh_host_rsa_key /etc/ssh/ssh_host_rsa_key.pub && \
#     # ssh-keygen -t rsa -P "" -f /etc/ssh/ssh_host_rsa_key && \
#     rm -f /etc/ssh/ssh_host_dsa_key /etc/ssh/ssh_host_dsa_key.pub && \
#     ssh-keygen -t dsa -P "" -f /etc/ssh/ssh_host_dsa_key && \
#     echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config && \
#     echo "PermitRootLogin yes" >> /etc/ssh/sshd_config

# 존재하지 않을 경우에만 생성하게 하기

# RUN ssh-keygen -t rsa -P "" -f /etc/ssh/ssh_host_rsa_key && \
#     ssh-keygen -t dsa -P "" -f /etc/ssh/ssh_host_dsa_key && \
#     echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config && \
#     echo "PermitRootLogin yes" >> /etc/ssh/sshd_config

# Hadoop 환경설정 복사
COPY config/* $HADOOP_HOME/etc/hadoop/
# Add JAVA_HOME to hadoop-env.sh
RUN echo "export JAVA_HOME=$JAVA_HOME" >> $HADOOP_HOME/etc/hadoop/hadoop-env.sh

# 스크립트 복사
COPY entry.sh /usr/local/bin/entry.sh
RUN chmod +x /usr/local/bin/entry.sh

# 데이터 디렉토리 마운트 및 볼륨 설정
# VOLUME ["/hadoop-data"]

# 포트 노출
EXPOSE 9870 8088 9000 22

# entry.sh 실행
CMD ["/usr/local/bin/entry.sh"]
