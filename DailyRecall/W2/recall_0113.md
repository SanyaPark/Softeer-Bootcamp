# 하루 회고

## 배운 것
### Try
10개 원소가 든 큐에서 4개 프로세스가 작업을 가져갈 때 로그를 찍어보니
empty_queue가 4번 발생하고 각 프로세스가 한 번씩 발생시킨다는 것을 알았다.
분석 결과
- 4개의 프로세스가 작업을 각각 1개씩 가져간다 * 2
- 작업은 2개가 남고 4개의 프로세스 중 2개(편의 상 p1, p2)는 작업을 획득, 남은 2개(편의 상 p3, p4)는 작업이 없어 empty_queue를 뱉는다.
- p1, p2는 작업이 끝났지만 큐가 비어있는지 알 수가 없으므로 작업을 요청한다.
- 둘 다 empty_queue를 뱉고 종료.
위 순서대로 돌아간 것이라 이해했고 로그 내용 또한 이를 잘 설명한다.
> 이렇게 프로그램이 돌아가는 세부 사항을 살펴보고 그 속에서 의문점을 찾고 공식문서, gpt등을 참고해서 동작 원리를 알 수 있었다.
---
프로세스에 작업을 할당하는 과정이 잘 이해가 가지 않는다.
큐를 파라미터로 넘겨야 하는데 Pool.map에서는 iterable하지 않다고 까인다.
- multiprocess.Manager를 사용해서 pickling 가능한 큐 객체를 만들 수 있다고 한다.
- Process , Pool.apply를 사용해도 된다고 한다.
- functools.partial로 파라미터를 고정하고 다른 부분만 iterable로 넘기는 방법도 있다.
- 실패한 방법:
  - starmap() -> 큐 객체는 pickling 불가하므로 직접 전달 시 문제 발생.

파일 이름에 신경쓰자.

의도하신건진 모르겠는데 파일 이름을 multiprocessing.py로 하니 모듈 이름과 충돌해 시작과 동시에 뻗는다.

멀티프로세싱은 GIL의 영향을 받지 않아 CPU-bound 작업에 효과적이다.

jupyter notebook에서 AttributeError: Can't get attribute 'pull_task' on <module '__main__' (built-in)> 에러가 발생한다.
>내일 찾아볼 것: jupyter에서는 if __name__ == "__main__"이 없으면 어떻게 하지.. 

**python multiprocessing 관련 정보는 위키에 게재하는 편이 파편화를 막고 더 응집성 있게 정보를 정리할 수 있을 것 같다.**