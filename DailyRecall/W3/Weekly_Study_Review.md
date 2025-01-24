# Dockerfile 

**Dockerfile의 중요한 사항들**
루트 계정과 Hadoop 사용자를 분리하고 권한을 세팅하는데 초점을 맞췄다.
```dockerfile
# ⬇️ USER Settings ⬇️: 루트 유저와 하둡 유저를 분리하는 과정

# hadooopuser 홈 디렉토리 생성 및 Bash를 기본 쉘로 설정, passwd=hadoopuser, sudo permission 부여
RUN useradd -m -s /bin/bash hadoopuser && \
    echo "hadoopuser:hadoopuser" | chpasswd && \
    adduser hadoopuser sudo

# 권한 확인 (디렉토리: /home, 로그인: hadoopuser): 권한 분리 확인
# drwxr-xr-x 8 hadoopuser hadoopuser  256 Jan 23 04:25 hadoopuser
# drwxr-x--- 2 ubuntu     ubuntu     4096 Nov 19 09:50 ubuntu

# hadoopuser에게 패스워드 묻지 않음
RUN echo "hadoopuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# ⬇️ 컨테이너 간 패스워드 없는 통신을 위한 SSH 설정 ⬇️
# /.ssh ➡️ 패스워드 없는 통신을 위한 ssh key가 들어갈 폴더 생성 및 권한 부여
RUN mkdir /home/hadoopuser/.ssh && \
    chmod 700 /home/hadoopuser/.ssh

# 옵션 설명: -t ras ➡️ key_type=RSA | -P '' ➡️ no passwd | -f <dir> ➡️ save key to <dir>
RUN ssh-keygen -t rsa -P '' -f /home/hadoopuser/.ssh/id_rsa 

# 각 컨테이너가 자신의 공개키를 authorized_keys에 등록 ➡️ hadoopuser가 패스워드 없이 접근 가능하게 됨 → 컨테이너 간 동일한 SSH key를 공유하지 않아도 됨.
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
```docker-compose.yaml```의 주요 사항들
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

## 코드 조각 모음
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
>이렇게 hadoop-data에 두 폴더가 매핑될 수 있어? 둘이 충돌하지 않아?
``` yaml
volumes: # Host 1.
    - namenode-data:/hadoop-data
volumes: # Host 2.
    - datanode-data:/hadoop-data
```

**결과**
* 충돌하지 않습니다.
* 두 컨테이너는 각각의 볼륨을 /hadoop-data로 독립적으로 매핑하므로, 서로 격리된 상태에서 작동합니다.
* 이 설정은 네트워크를 통해 서로 통신하므로, 충돌 없이 동작 가능합니다.

**특정 노드의 포트 확인**
```bash
docker exec <hostname> netstat -tuln | grep <포트번호>
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
아래와 같이 포트를 살짝 다르게 해 중복 포트로 충돌하는 문제 회피
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
* ```expose``` 키워드는 컨테이너 내부에서 지정된 포트를 노출하고, 같은 네트워크에 속한 다른 컨테이너가 해당 포트에 접근할 수 있도록 합니다.
  <br>
* ```networks``` 설정에 의해 hadoop-network 내부에서 모든 컨테이너가 서로의 포트를 직접 접근 가능하게 됩니다.

## 컨테이너간 SSH 연결이 필요한가??
1. 멀티 노드 클러스터에서 SSH 필요성
Hadoop의 클래식 설정 방식에서는 여러 노드 간 통신 및 명령 실행에 SSH가 필수적이었습니다. 예를 들어:
   - NameNode가 DataNode 또는 ResourceManager에서 명령을 실행하려면 SSH를 통해 원격으로 접속해 스크립트를 실행해야 했습니다.
   - 특정 명령 (```start-dfs.sh```, ```start-yarn.sh```)이 내부적으로 SSH를 사용해 클러스터의 모든 노드에서 데몬을 시작합니다.
<br>

2. SSH를 설정하는 주요 이유
    (a) 노드 간 명령 전달
Hadoop이 SSH를 요구하는 이유는 멀티노드 환경에서 **노드 간 통신 및 데몬 관리** 때문입니다.
Hadoop은 기본적으로 각 노드에서 로컬 스크립트를 실행하는 데 SSH를 사용합니다. 
따라서 다음과 같은 작업이 필요한 경우 SSH 설정이 요구됩니다:

   - 분산 모드에서 NameNode가 DataNode를 관리할 때.
   - 클러스터 노드에 수동으로 명령을 전달할 때.<br>

    (b) 사용자 편의
Hadoop의 초기 설정은 기본적으로 SSH 연결을 요구합니다. 
사용자가 SSH를 통해 클러스터의 각 노드에 접속하여 직접 작업하거나 상태를 확인하기 쉽게 만들어줍니다.

    (c) 전통적 Hadoop 설정
많은 블로그와 자료는 Hadoop의 초기 버전을 기반으로 작성되었으며, 당시에는 SSH가 기본적인 요구 사항으로 간주되었습니다.
<br>

3. 현대적인 컨테이너 환경에서는 SSH가 꼭 필요한가?
    (a) Docker Networking과 대체 통신
Docker의 네트워킹 기능(bridge, overlay)을 활용하면 SSH 없이도 노드 간 통신이 가능합니다. Hadoop 데몬 간의 RPC 통신은 별도의 SSH 연결 없이도 작동합니다.

    (b) 컨테이너 환경에서 SSH의 대안
클러스터 관리 스크립트(start-dfs.sh, start-yarn.sh)는 도커 네트워크와 docker exec 명령으로 충분히 대체할 수 있습니다.
SSH 대신 컨테이너 간 호스트네임과 포트로 Hadoop 노드 간 통신을 설정하는 방식이 더 간단합니다.

**특히 단일 노드 테스트 환경에서는 SSH는 거의 필요 없습니다.**
Single Node 환경에서 모든 데몬이 하나의 노드에서 실행되므로 ```localhost```로 데몬 간 직접 통신이 가능합니다.

Docker Compose에서 각 컨테이너에 ```tty: true```와 ```stdin_open: true```를 설정하면 컨테이너 내부에 바로 접근할 수 있어 SSH 없이도 디버깅과 모니터링이 가능합니다.

---

### SSH 없이 멀티노드 구성이 가능한 이유

1. Docker 네트워크 사용:
   * Docker Compose는 hadoop-network라는 사용자 정의 네트워크를 설정하여 서비스 간 통신을 제공합니다.
   * Docker 컨테이너 간 통신은 내부 DNS(예: namenode, datanode1)를 통해 이루어지며, 별도의 SSH 설정 없이 RPC(원격 프로시저 호출)를 처리합니다.
<br>

2. Hadoop 데몬 통신:
   * Hadoop의 데몬(NameNode, DataNode, ResourceManager 등)은 내부적으로 RPC와 HTTP 프로토콜을 통해 통신하며, Docker 네트워크로 충분히 연결 가능합니다.
   * **싱글노드 클러스터와 멀티노드 클러스터의 본질적인 통신 방식은 동일**합니다. 차이는 노드 수와 물리적 분산 여부일 뿐입니다.
<br>

3. 포트 매핑:
   * 필요한 UI와 데몬의 포트를 Docker Compose 파일에서 명시적으로 매핑하여 외부에서 접근 가능하도록 구성되었습니다.
   * 예: NameNode(9870), DataNode(9864), ResourceManager(8088).

**이 방식의 한계와 제약**

1. 자동 스케일링 및 복잡한 노드 관리:
   * SSH는 노드 간 명령을 전달하거나 스크립트를 실행할 때 필요할 수 있습니다. 예를 들어, 클러스터 동적으로 확장 시에는 SSH가 유용합니다.
   * 그러나 현재 Compose 파일처럼 컨테이너를 정적으로 정의하면 SSH 없이도 문제가 없습니다.
<br>

2. Hadoop 스크립트와 SSH 의존성:
   * Hadoop은 멀티노드 환경에서 start-dfs.sh, stop-dfs.sh 같은 스크립트를 통해 NameNode에서 다른 노드들을 시작/중지합니다.
   * 이 스크립트들은 내부적으로 SSH를 사용합니다.
   * **대안**: Docker Compose로 각 컨테이너를 독립적으로 실행 및 제어하므로 이 제약을 우회할 수 있습니다.

#### 정리하자면:

1. 정적 노드 구성 (현재 제공된 Compose 파일)

   * 노드의 수가 고정되어 있고, 각 노드가 미리 정의된 상태에서 실행됩니다.
   * **SSH는 필요 없습니다.** Docker Compose의 네트워크와 포트 매핑으로 데몬 간 통신이 가능하니까요.
<br>

2. 동적 노드 구성 (노드 추가/제거)

   * 실행 중인 클러스터에 노드를 추가하거나 제거할 필요가 있을 때, SSH가 필요합니다.
   * Hadoop의 ```start-dfs.sh```나 ```start-yarn.sh``` 스크립트는 SSH로 각 노드에 접속하여 데몬을 시작/중지합니다.
   * 이 경우 **SSH가 필수적**이며, Hadoop 설정 파일(```slaves``` 또는 ```workers```)에도 새로운 노드를 추가해야 합니다.


#### 결론: 정적으로 정의된 노드 구성에서 SSH의 역할

1. SSH가 필요 없는 경우

각 컨테이너에서 직접 하둡 데몬을 실행하거나 Compose의 ```entry.sh```에 포함시켜 컨테이너 시작 시 자동으로 실행하도록 구성할 때.

2. SSH가 필요한 경우

```start-dfs.sh``` 또는 ```stop-dfs.sh```와 같은 하둡 관리 스크립트를 사용하려면 SSH 설정이 필수입니다.
NameNode가 다른 노드(DataNode, Secondary NameNode 등)를 제어하기 위해 SSH를 이용합니다.

---
### SSH key를 volume을 통해 호스트와 공유시켜야 할까?

* **컨테이너를 삭제 후 재배포하면 SSH 키가 변경되므로, 기존 통신이 끊어질 가능성이 있습니다.**
* 이를 방지하려면 **SSH 키를 호스트와 공유하거나 미리 정의된 키를 사용**하도록 설정해야 합니다.
* 데이터 노드의 단순 재시작(docker-compose restart)에서는 문제가 발생하지 않습니다

SSH 키를 호스트와 공유하기:
```yaml
volumes: # 컨테이너가 재배포되더라도 동일한 키를 사용합니다.
  - ./ssh-keys:/home/hadoopuser/.ssh
```
키를 고정된 값으로 설정:
```dockerfile
#컨테이너 실행 시 항상 동일한 SSH 키를 사용하도록 Dockerfile을 수정:
COPY ./predefined-keys/id_rsa /home/hadoopuser/.ssh/id_rsa
COPY ./predefined-keys/id_rsa.pub /home/hadoopuser/.ssh/authorized_keys
```
통합 자동화 스크립트 추가:
아래 스크립트를 ```entry.sh```에 추가하여 새로운 DataNode 키를 자동으로 등록하도록 만듭니다.
```bash
# NameNode가 재시작된 노드의 새 키를 자동으로 받아들이도록 스크립트를 추가
ssh-keyscan -H datanode1 >> /home/hadoopuser/.ssh/known_hosts
ssh-keyscan -H datanode2 >> /home/hadoopuser/.ssh/known_hosts
```