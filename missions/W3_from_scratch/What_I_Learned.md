# Dockerfile 

**Dockerfile의 중요한 사항들**
루트 계정과 Hadoop 사용자를 분리하고 권한을 세팅하는데 초점을 맞췄다.
```dockerfile
# ⬇️ USER Settings ⬇️: 루트 유저와 하둡 유저를 분리하는 과정

# hadooopuser 홈 디렉토리 생성 및 Bash를 기본 쉘로 설정, passwd=hadoopuser, sudo permission 부여
RUN useradd -m -s /bin/bash hadoopuser && \
    echo "hadoopuser:hadoopuser" | chpasswd && \
    adduser hadoopuser sudo

# hadoopuser에게 패스워드 묻지 않음
RUN echo "hadoopuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# ⬇️ 패스워드 없는 통신을 위한 SSH 설정 ⬇️
# /.ssh ➡️ 패스워드 없는 통신을 위한 ssh key가 들어갈 폴더 생성 및 권한 부여
RUN mkdir /home/hadoopuser/.ssh && \
    chmod 700 /home/hadoopuser/.ssh

# 옵션 설명: -t ras ➡️ key_type=RSA | -P '' ➡️ no passwd | -f <dir> ➡️ save key to <dir>
RUN ssh-keygen -t rsa -P '' -f /home/hadoopuser/.ssh/id_rsa 

# 공개키를 authorized_keys에 등록 ➡️ hadoopuser가 패스워드 없이 접근 가능하게 됨
RUN cat /home/hadoopuser/.ssh/id_rsa.pub >> /home/hadoopuser/.ssh/authorized_keys && \
    chmod 600 /home/hadoopuser/.ssh/authorized_keys && \
    chown -R hadoopuser:hadoopuser /home/hadoopuser/.ssh

# hadoopuser에게 /usr/local/hadoop 이하 폴더의 권한 부여
RUN chown -R hadoopuser:hadoopuser /usr/local/hadoop

# hadoopuser 계정으로 진입 및 작업 폴더 설정
USER hadoopuser
WORKDIR /home/hadooopuser
```

---
# Docker Compose

```yaml
# hostname을 지정해두면 ContainerID 대신 이 이름을 사용할 수 있다.
hostname: namenode

# 네임노드의 /home/hadoopuser 폴더를 호스트 작업공간과 마운트하여 작업 및 HDFS로의 전송을 간편하게 한다.
volumes:
    - ./workspace:/home/hadoopuser

# NODETYPE을 미리 지정하여 마스터 / 워커 노드 관리를 간편하게 할 수도 있다.    
# 필수는 아니지만, 유저를 명확히 지정해 환경 구성 시 혼란을 줄이고 멀티 노드 환경에서도 일관성을 유지할 수 있다.
environment:
    HDFS_NAMENODE_USER: hadoopuser
    HDFS_SECONDARYNAMENODE_USER: hadoopuser
    NODETYPE: master

# 컨테이너 간 종속성 표현: <container_name>을 실행시키고 나서 이 컨테이너가 실행됨. 종료 시 그 반대.
depends_on:
    - <container_name>

# 설명
networks:
    - hadoop-network

# driver: bridge는 Docker의 기본 네트워크 드라이버로, 컨테이너 간 통신을 가능하게 한다.
# 서비스가 동일한 네트워크에 연결되어 서로 통신 가능.
# 동일 네트워크에 속하지 않은 다른 컨테이너와 격리됨.
networks:
  hadoop-network:
    driver: bridge
```

---
# Hadoop

### ```namenode -format```의 중복 실행 방지
Dockerfile이 실행하는 ```entrypoint.sh```에 조건 추가 / 포맷된 NameNode 존재 여부 확인
```bash
if [ ! -f /usr/local/hadoop/tmp/dfs/name/current/VERSION ]; then
    $HADOOP_HOME/bin/hdfs namenode -format -force
fi
```

### Hadoop 서비스 관련 포트
|포트 번호  |서비스     |설명       |
|---        |---        |---        |
|9870       |HDFS web UI| 브라우저에서 http://<컨테이너 IP>:9870로 파일 시스템을 모니터링 가능. |
|8088       |ResourceManager Web UI  |브라우저에서 http://<컨테이너 IP>:8088로 파일 시스템을 모니터링 가능           |

```start-dfs.sh``` ? 
Hadoop이 기본적으로 제공하는 스크립트.
start-dfs.sh, stop-dfs.sh, start-yarn.sh, stop-yarn.sh가 있다.
위치: ```$HADOOP_HOME/sbin/start-dfs.sh```
역할: HDFS의 주요 서비스(데몬)를 시작합니다.

---
# 기타 질문/답변 및 코드 조각 모음

**실행 중인 컨테이너에 접속하기**
```bash
docker exec -it <hostname | container_ID> /bin/bash
```

**entrypoint.sh** 끝에 ```tail -f /dev/null``` 추가:
이 명령어는 컨테이너가 계속 **실행 상태를 유지**하도록 만들어 줍니다. 

실수로 생긴 고아 컨테이너 제거:
```bash
docker-compose up -d --remove-orphans
```

컨테이너 종료 시 마운트 된 볼륨도 함께 제거:
```bash
docker-compose down -v
```

## HDFS user와 root
Hadoop을 Docker로 구성할 때, **HDFS 유저를 별도로 생성하는 것이 더 일반적**이며, 보안 및 권한 관리 측면에서 권장되는 방식입니다.

**이유**:
보안, 권한 관리 및 실제 운영 환경 측면에서 권장됨


**Question**
``` yaml
volumes: # Host 1.
    - namenode-data:/hadoop-data
volumes: # Host 2.
    - datanode-data:/hadoop-data
```
이렇게 hadoop-data에 두 폴더가 매핑될 수 있어? 둘이 충돌하지 않아?

**결과**
* 충돌하지 않습니다.
* 두 컨테이너는 각각의 볼륨을 /hadoop-data로 독립적으로 매핑하므로, 서로 격리된 상태에서 작동합니다.
* 이 설정은 네트워크를 통해 서로 통신하므로, 충돌 없이 동작 가능합니다.

**특정 노드의 포트 확인**
```bash
docker exec <hostname> netstat -tuln | grep 9000
```

**컨테이너 이름 확인**
```bash
# hostname_1 컨테이너에서 hostname_2라는 이름으로 hostname_2에 접근할 수 있는지 확인합니다:
# (두 컨테이너의 container_name은 각자의 hostname과 동일하다고 가정)
docker exec <hostname_1> ping <hostname_2>
```

**최종 연결 테스트:**
```bash
$HADOOP_HOME/bin/hdfs dfsadmin -report
```

**컨테이너 로그 확인:**
```bash
docker logs namenode
```

**포트 충돌 문제**
```yaml
services:
  datanode1:
    ports:
      - "9864:9864"  # 호스트의 9864 포트를 datanode1의 9864에 매핑
      - "9865:9866"  # 호스트의 9865 포트를 datanode1의 9866에 매핑

  datanode2:
    ports:
      - "9867:9864"  # 호스트의 9867 포트를 datanode2의 9864에 매핑
      - "9868:9866"  # 호스트의 9868 포트를 datanode2의 9866에 매핑
```
* expose 키워드는 컨테이너 내부에서 지정된 포트를 노출하고, 같은 네트워크에 속한 다른 컨테이너가 해당 포트에 접근할 수 있도록 합니다.
  <br>
* networks 설정에 의해 hadoop-network 내부에서 모든 컨테이너가 서로의 포트를 직접 접근 가능하게 됩니다.

## 컨테이너간 SSH 연결이 필요한가??
