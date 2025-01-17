# Python Multiprocessing

```import multiprocessing```

## Pool과 Process의 차이?

| 특징 | Pool | Process |
| --- | --- | --- |
| 용도          |작업을 작업자(worker) 풀(pool)에 분배하여 병렬 처리 | 각 작업마다 별도의 프로세스를 생성하여 독립적으로 실행|
| 유연성         | 동일한 함수에 대해 반복 작업을 처리하는 데 적합	| 작업의 개별적 실행과 프로세스 제어가 필요한 경우 적합|
| 구현          | 상대적으로 간단 (맵핑 함수 사용)	|더 복잡 (각 프로세스를 직접 생성 및 관리)|
| 프로세스 수 관리 | 내부적으로 프로세스 풀 크기를 관리	| 사용자가 생성한 프로세스 개수를 직접 관리|
| 상태 공유       | 상태 공유가 어렵지만 워커 간에 작업이 자동으로 배분됨	| 프로세스 간 상태 공유는 어렵지만 독립적으로 실행 가능|

---
### Pool
선언: 
```python
with Pool(processes=process_num) as pool:
    pool.map(function_name, tasks:**iterable**)
```        

#### 언제, 왜 쓰나요?
**반복적, 대량의 작업**을 병렬 처리시 적합
예시
- 배치 처리
- 맵리듀스 스타일의 작업 (데이터를 작은 조각으로 나누고 각각에 동일한 함수 적용 시)
- 작업 수 제한이 필요할 때
- 리소스 최적화 및 작업 분배 자동화 : Pool.apply_async(), Pool.map()

```python
예시:
tasks = {
    "작업1": 3,
    "작업2": 5,
    "작업3": 2,
    "작업4": 4,
}

# dict를 (key, value) 형태의 리스트로 변환
task_list = list(tasks.items())

# 프로세스 풀 생성, 리스트의 각 요소에 대해 worl_log 함수를 병렬로 호출
with Pool(processes=2) as pool:
    pool.map(work_log, task_list)
```        

**Pool.map의 작업 분배 원리**
Pool.map은 작업 리스트의 각 요소를 입력 함수의 파라미터로 전달하여 병렬적으로 처리한다.

동작 방식:
  1. 작업 분할:
    * Pool.map은 입력 리스트를 균등하게 나누어 각 프로세스에 전달하려고 시도한다.
    * 리스트의 요소를 순서대로 분배하므로, 작업이 **항상 "최적의 시간 분배"가 되지는 않는다**. (예: [5초, 4초]와 [2초, 3초]로 나뉠 수 있음.) <br>→ 기본적으로 입력 리스트를 순서대로 분배하기 때문 
  <br>
  2. 병렬 실행:
    * 각 프로세스는 할당된 작업을 독립적으로 처리한다.
    * 작업이 종료된 프로세스는 다른 프로세스를 **기다리지 않고 다음 작업을 받는다**. 
  <br>
  1. 결과 반환:
    * 모든 작업이 완료된 후 map은 **결과를 원래 리스트 순서에 맞게 반환한다**.
    * Pool.map은 입력 리스트의 순서를 기준으로 결과를 정렬합니다. <br>각 프로세스가 작업을 완료한 뒤, 해당 결과를 입력 데이터의 인덱스에 따라 정렬해서 반환합니다.

왜 순서를 보장할 수 있을까?
- Pool.map 내부적으로는 **입력 데이터의 인덱스를 기억합니다**. 각 작업이 완료된 결과는 이 인덱스를 기준으로 원래 리스트와 같은 순서로 재배치됩니다.

최적화가 필요한 경우:
  - 작업 시간이 균등하지 않다면 `imap`이나 `apply_async` 같은 동적 작업 분배 방법을 사용하는 것이 효율적이다.

---

### Process

선언: `Process(target=function_name, args=(arg1, ...))`

#### 언제, 왜 쓰나요?

개별 **작업의 독립성**이 중요하거나, 각 작업이 **서로 다른 작업** 수행 시.
예시
- **다양한 작업 병렬 실행** : ETL 과정이 동시에 실행되어야 하는 경우
- **프로세스 간 통신** : Queue, Pipe를 이용해 프로세스 간 데이터 전송이 필요 시
- 작업 관리 : 각 프로세스의 작업 완료 여부나 상태를 독립적으로 추적할 때
- **병렬 처리가 아닌 I/O bound 작업이라면?**
→ 멀티스레딩을 고려하거나 asyncio 사용
<br>

#### 중요 메서드
`Process.start()` → 프로세스 실행

`Process.join()` → 모든 프로세스가 종료될 때까지 대기 (부모 프로세스 block됨)
* `join()`을 깜빡하면?
  * 부모 프로세스가 먼저 종료될 수 있음
  * 출력 순서 예측 불가 (부모-자식이 독맂벅 실행됨)
  * 좀비 프로세스 발생 가능
  * 데이터 일관성 문제


`Process(daemon=True)` → 부모 프로세스가 종료되면 **함께 종료**되도록 설정
* 언제 사용할까?
  1. 부모 프로세스와 생명 주기를 맞출 때
  2. 백그라운드 작업이 메인 흐름에 중요하지 않을 때 (ex. logging, caching, ...)
  3. 간단한 보조 작업 처리 (상태 확인, 주기적 백업, 리소스 정리 등 ...)
<br> 

* 중요 특징
  * 부모 프로세스 종료 시 데몬 프로세스도 **강제 종료**
    * 따라서 중요한(반드시 완료되어야 하는) 작업에 적합하지 않음
  * 따라서 `join()` 호출 불가
<br>

* 로그만 기록하는 별도 데몬 프로세스를 만드는 이유?
  1. 로그 처리가 메인 작업을 방해하지 않기 위해
     * 파일에 로그를 쓰는건 I/O 연산이라 작업이 느려질 수 있음 (병목)
     * 메인 프로세스는 로그를 Queue에 넣고 실제 쓰기는 로그 프로세스가 처리 (비동기 처리)  
  2. 다양한 작업의 로그를 중앙에서 관리하기 위해.
     * 여러 작업이 개별적으로 로그 기록 시 관리가 복잡해짐
  3. 실시간 분석이나 전송(→ 병목)이 필요한 경우

<br>

### Pool / Process의 실무 활용 예

**ETL 파이프라인 예시**
  1. 데이터 파티셔닝 및 병렬 변환: Pool
        여러 데이터 파티션을 병렬로 변환 처리.
  2. 추출-변환-적재 단계 병렬 실행: Process
        데이터 추출, 변환, 적재를 동시에 실행.

**ML 데이터 준비 예시**
- 이미지 데이터 증강: Pool 사용.
- 독립적 모델 학습 및 평가: Process 사용.



---

## 기타 멀티프로세싱 관련:

### multiprocessing.Queue
`Queue.close()`와 `.join_thread()`는 **모든 작업이 완료된 후 호출**해야 합니다.<br>
작업이 완료되기 전에 큐를 닫으면 남은 작업이 처리되지 않거나 누락될 수 있기 때문에, `join_thread()`는 모든 프로세스가 완료된 후 호출해야 합니다.

**큐가 비어있을 경우**, queue.Empty 예외가 발생하며, 작업을 가져갈 수 있는 프로세스는 큐에서 남은 작업을 처리하고, 비어 있으면 기다리거나 종료됩니다.

`close()`: "주문 마감!"
→  이제 새로운 주문(데이터 추가)을 받지 않고, 주방(큐)이 기존 주문을 모두 처리하도록 함.

`join_thread()`: "주방 일이 끝날 때까지 기다릴게."
→  주방이 주문을 다 요리하고(데이터 전송), 모든 일을 끝냈는지 확인.

**Empty check, get은 Atomic하게** 이루어져야 한다.
그렇지 않으면 그 사이에 다른 프로세스가 가져가고 에러의 원흉이 된다.

### multiprocessing.Lock

|특징	|`lock.acquire()` / `lock.release()`	|`with lock: ...`|
|---|---|---|
|코드 간결성|	복잡하고 장황함	|간결하고 명료|
|안전성	|해제 누락 가능성 있음	|해제 자동 처리|
|예외 처리|	try-finally가 필요|	예외 처리 자동|
|세밀한 제어|	가능	|다소 제한적|
|추천 상황| 세밀한 제어 필요시| 일반적|

<details>
    <summary>lock 획득/해제 예시 코드</summary>

        # Critical section
        lock.acquire()
        try:
            # 공유 자원 작업
            print("작업 수행 중...")
        finally:
            # 반드시 lock 해제
            lock.release()

</details>


### multiprocessing.Manager, Pipe

|특징	|Manager	|Pipe|
|---|---|---|
|데이터 공유 방식	|공유 값, 리스트, 딕셔너리 등 데이터 구조 제공	|메시지 기반 통신|
|프로세스 수	|여러 프로세스 간 공유 가능	    |두 프로세스 간 직접 통신|
|사용 복잡성	|데이터 동기화 처리가 포함됨	|간단한 메시지 교환|
|예시 상황	|상태 관리, 동기화가 필요한 작업	|간단한 요청-응답 통신|

> Pipe는 데이터를 어떻게, 어떤 형식으로 넘기나요?
* Pipe는 데이터를 **복사해서 전송**하며, 이는 프로세스 간 독립성을 유지하기 위해 필수적입니다.
하지만 큰 데이터를 다룰 경우 성능에 유의해야 하며, 효율적으로 처리하려면 공유 메모리(multiprocessing.Value, multiprocessing.Array) 등을 고려할 수 있습니다.

<details>
    <summary>Pipe 예시 코드</summary> 
    
    from multiprocessing import Process, Pipe

    def sender(conn):
        for i in range(5):
            conn.send(f"Message {i}")  # 메시지 전송
        conn.close()

    def receiver(conn):
        while True:
            try:
                message = conn.recv()  # 메시지 수신
                print("받은 메시지:", message)
            except EOFError:
                break

    if __name__ == "__main__":
        parent_conn, child_conn = Pipe()  # 파이프 생성

        p1 = Process(target=sender, args=(child_conn,))
        p2 = Process(target=receiver, args=(parent_conn,))

        p1.start()
        p2.start()

        p1.join()
        p2.join()

</details>
    
---


### 멀티스레딩과 GIL(global interpreter lock)?

### 멀티스레딩의 장점과 한계 및 대안
**장점**
→ I/O bound 작업에 적합, 코드 단순화, 멀티프로세싱 대비 낮은 메모리 사용량 등의 
→ C 확장 모듈(Numpy, Scipy...)와 같은 GIL을 해제하는 라이브러리와 사용시 스레드를 사용해 병렬 작업 가능

**단점**
→ CPU bound 작업에 비효율, 컨텍스트 스위칭 비용은 

**대안으로는:**
→ 멀티프로세싱: CPU bound 작업에는 멀티프로세싱이 일반적
→ Asyncio: GIL의 영향을 받지 않고도 동시성 구현 가능

#### GIL이란?

CPython(파이썬의 가장 널리 사용되는 구현)에서 멀티스레딩 환경에서의 메모리 관리와 데이터 무결성을 보장하기 위해 존재하는 일종의 "잠금 메커니즘"

#### GIL의 동작 방식
GIL은 **한 번에 하나의 스레드만** 파이썬 바이트코드를 실행할 수 있도록 보장합니다.
즉, 여러 스레드가 동시에 실행되더라도, GIL은 **한 스레드가 실행 중일 때 다른 스레드가 실행하지 못하게 막습니다.**
GIL은 스레드 간의 컨텍스트 스위칭을 통해 교대로 실행되며, 주기적으로 해제됩니다.

#### GIL이 생긴 이유
1. 간단한 메모리 관리:
    CPython의 메모리 관리 시스템(참조 카운팅 기반)은 GIL을 활용해 데이터 충돌을 방지합니다. 여러 스레드가 동시에 참조 카운트를 변경하려 하면 데이터 손상이 발생할 수 있는데, GIL이 이를 방지합니다.
2. CPython 설계의 역사적 이유:
    파이썬 초기 버전에서 단일 스레드 기반의 성능을 우선시했기 때문에 GIL이 포함되었습니다.
3. 호환성 및 유지보수:
    GIL을 유지하면 C 확장 모듈 작성이 더 쉬워집니다. GIL이 없으면 확장 모듈마다 별도의 동기화 처리가 필요합니다.

#### GIL의 영향
멀티스레딩이 CPU bound 작업에서 성능을 제대로 발휘하지 못합니다.

I/O bound 작업 시 I/O대기 작업 (입출력, 네트워크 요청, DB쿼리 등) 중에는 다른 스레드로 전환 가능
→ GIL의 제약이 크지 않으며 멀티스레딩의 효율을 얻을 수 있음.



---

# 미션 Trouble Shooting 및 고민

>pool.map(func, args)에 넣을 args에 대한 고민이야.<br>
func는 multiprocess.Queue와 int를 받아서 Queue에 int를 넣는 작업을 수행해. <br>
그런데 **map의 args는 iterable**해야 하잖아? 그래서 Queue를 어떻게 넣어야 할지 모르겠어. 도와줘!!

* 시도 : 
`functools.partial`, `pool.starmap`등으로 Queue를 넘겨봤지만 <br>
**RuntimeError**: Queue objects should only be shared between processes through inheritance 발생
<br>

* 원인 :
  * multiprocessing.Queue의 특성:<br>
    Pool에서 Queue 객체를 전달할 때, 프로세스가 직접 Queue 객체를 상속하지 않으면 이 오류가 발생합니다
  
  * 직접 전달 제한:<br>
    Pool.map은 작업을 분산하면서 각 프로세스에 데이터를 **피클링(pickling)**하여 전달함<br>
    Queue 객체는 피클링이 지원되지 않으므로 이를 직접적으로 전달하려고 하면 문제가 발생.

* 해결 방법 :
  1. **Manager.Queue**
    `multiprocessing.Manager`를 사용하면 pickling 가능한 `Queue` 객체를 생성 가능
    → 큐를 프로세스 간 안전하게 공유
        ```python
        with Pool(2) as pool:
            pool.starmap(process_queue, [(q, num) for num in numbers])
        ```

> 10개의 Task, 4개의 프로세스 상황에서 `get_nowait()`으로 데이터를 가져올 시 empty queue가 4번 발생한다.<br>
> 4/4/2 → 2개 남음 으로 empty queue는 2번만 발생해야 할 것 같은데...

* 이유:
  1. 4개씩 2번 가져가서 작업이 2개가 남는다.
  2. 4개 중 2개 프로세스가 작업을 가져가고 남은 두 프로세스는 `queue.Empty` 발생 (2회)
  3. 가져간 작업을 완료한 두 프로세스는 큐가 비었는지는 모르므로 작업을 가져가려 하고 `queue.Empty` 발생 (2회)
  4. 이렇게 총 4회의 `queue.Empty`가 발생
* 작업을 분배하는 과정에서 **이러한 빈 큐 접근은 불가피**하며, race condition이 아닌 **정상 동작임**.

> Github에 큰 파일을 로드했던 jupyter notebook이 안올라가요 (http 400 error) <br>
- git config http.postbuffer 524288000


---

# Docker

## Dockerfile
이미지 빌드 시 컴파일러에 가깝게 동작하는데,
얘를 어떻게 `interactive` 하게 만들까??
    → **Docker desktop**에 콘솔이 있으니 한줄 씩 쳐보고 되면 도커파일에 넣어라

### 도커파일 자체는 주피터 처럼 한줄 한줄 할 수는 없나?

**멀티 스테이지 빌드**를 사용하면 될 것 같다.

Dockerfile이 **멀티스테이지 빌드**를 포함하고 있다면, 
--target 옵션을 사용하여 **특정 빌드 단계까지 실행**하고 결과를 테스트할 수 있습니다.

``` Dockerfile
FROM ubuntu AS base
RUN apt-get update && apt-get install -y python3

FROM base AS build
RUN pip install flask
```

특정 스테이지만 빌드:
```docker build **--target base** -t base-stage-test .```


## EC2 User-data / Container

* 무엇을 어디에 둬야 할까?
  * 무엇이 업데이트되어야 하고 무엇이 고정되어야 하는가
    * 전자는 user-data, 후자는 도커이미지

* 자주 업데이트되는 파일은?
  * 도커 이미지에 종속되는건 싫다 (수정 안할거임!) -> EC2에서 유저데이터 통해 git-clone하는게 맞을 듯
  * 아니면, 도커이미지를 버전 관리할거고 고정된 이름으로 ECR에 올려서 관리할거야.



## 도커를 실행하는 세 가지 모드
1. **Interactive** **mode**
Docker를 사용하면 대화형 모드에서 컨테이너를 실행할 수 있습니다. 
이는 컨테이너가 실행 중인 동안 컨테이너 내에서 명령을 실행할 수 있음을 의미합니다. 
컨테이너를 대화식으로 사용하면 실행 중인 컨테이너 내부의 명령 프롬프트에 액세스할 수 있습니다.

2. **Attached mode**
Attached mode에서 Docker는 컨테이너에서 프로세스를 시작하고 콘솔을 프로세스의 표준 입력, 표준 출력 및 표준 오류에 연결할 수 있습니다.

3. **Detached mode**
컨테이너가 입력 또는 출력 스트림에 연결되지 않고 백그라운드에서 실행됨을 의미합니다.

**모드 간 비교**
| 특징	| Interactive Mode	| Attached Mode	| Detached Mode |
|---|---|---|---|
|터미널 연결	| 사용자와 컨테이너 **터미널이 연결됨**	|컨테이너 **출력이 터미널에 출력됨**	| 터미널과 **분리되어 백그라운드에서** 실행 |
|작업 성격	|**실시간** 작업, 디버깅	| **짧은 실행** 작업	| **지속적인** 서비스 실행 |
|터미널 반환	| 터미널이 반환되지 않음	| 터미널이 반환되지 않음	| 터미널이 **즉시 반환됨** |
|컨테이너 종료	| 터미널 닫히면 종료 |	터미널 닫히면 종료	| 터미널 **닫혀도 계속 실행** |
|주 사용 환경	| 테스트, 디버깅	| 간단한 명령 실행	| 서버, 프로덕션, 장기 실행 작업 |
