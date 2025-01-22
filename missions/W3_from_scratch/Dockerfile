FROM python:3.10-slim AS base-py3.10

FROM ubuntu:24.04

# Set environment variables for Hadoop
ENV DEBIAN_FRONTEND = noninteratcive


# Install dependencies
RUN apt-get update && apt-get install -y \
openjdk-11-jdk \
wget \
ssh \
rsync \
vim \
sudo \
&& apt-get clean 

ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-arm64
ENV PATH=${PATH}:${JAVA_HOME}/bin

# 이게 있어야 ssh 정상적으로 된다? --> nono 원격용임


# Setting Hadoop ENVs
ENV HADOOP_VERSION=3.3.6
ENV HADOOP_HOME=/usr/local/hadoop
ENV HADOOP_COMMON_LIB_NATIVE_DIR=/usr/local/hadoop/lib/native
ENV PATH=${PATH}:${HADOOP_HOME}/bin:${HADOOP_HOME}/sbin

# Download and install Hadoop
RUN wget https://mirrors.sonic.net/apache/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz && \
    tar xvzf hadoop-${HADOOP_VERSION}.tar.gz && \
    mv hadoop-${HADOOP_VERSION} ${HADOOP_HOME} && \
    rm hadoop-${HADOOP_VERSION}.tar.gz

# Hadoop configuration files
COPY config/*.xml /usr/local/hadoop/etc/hadoop/

# Set up SSH and ensure /run/sshd exists
RUN apt-get update && apt-get install -y openssh-server
RUN mkdir -p /run/sshd && chmod 0755 /run/sshd

# Add JAVA_HOME to hadoop-env.sh
RUN echo "export JAVA_HOME=${JAVA_HOME}" >> ${HADOOP_HOME}/etc/hadoop/hadoop-env.sh

# USER Settings:
RUN echo 'root:0000' | chpasswd
## make home dir for hadooopuser and set Bash as base shell, set passwd, grant sudo permission
RUN useradd -m -s /bin/bash hadoopuser && \
    echo "hadoopuser:hadoopuser" | chpasswd && \
    adduser hadoopuser sudo

# Do not request password to hadoopuser
RUN echo "hadoopuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Configure SSH for passwordless communication
# /.ssh <-- for communicate without passwd
# -t ras : key_type=RSA, -P '' : no passwd, -f <dir> : save key to <dir>
# add public key to authorized_keys -> allow hadoopuser to access without passwd
RUN mkdir /home/hadoopuser/.ssh && \
    chmod 700 /home/hadoopuser/.ssh

RUN ssh-keygen -t rsa -P '' -f /home/hadoopuser/.ssh/id_rsa 

RUN cat /home/hadoopuser/.ssh/id_rsa.pub >> /home/hadoopuser/.ssh/authorized_keys && \
    chmod 600 /home/hadoopuser/.ssh/authorized_keys && \
    chown -R hadoopuser:hadoopuser /home/hadoopuser/.ssh

# also change ownership of hadoop dir and files to hadoopuser
RUN chown -R hadoopuser:hadoopuser /usr/local/hadoop


# Expose HDFS and YARN
EXPOSE 22 9870 8088 9000 9864 9866


# Add entrypoint and terminate script
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
COPY stop-by-type.sh /usr/local/bin/stop-by-type.sh 

RUN chmod +x /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/stop-by-type.sh

USER hadoopuser

# Set entrypoint script
ENTRYPOINT ["entrypoint.sh"]    