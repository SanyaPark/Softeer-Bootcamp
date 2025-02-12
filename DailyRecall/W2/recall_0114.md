# 🌅 하루 감상

!! 고칠 것 !!

아 이거 오래 걸릴텐데... 다른 방법 없나?<br>
  보통 이런거 찾는게 더 오래걸리거나 저게 방법인 경우도 상당하다. 심지어 찾았더니 더 느린 경우도 있다.<br>
  귀찮아하지 말고 돌려놓고 생각하든지 이런 일 없게 미리 설계를 탄탄히 하자<br>
하나에 꽃히면 시야가 점점점 좁아진다.<br>
  저번 미션도 그렇고 메인 요구사항보다 곁가지에 힘이 더 들어가는 것 같다<br>
  제대로 만드는 것도 좋지만 핵심이 뭔지 항상 생각하자
---
## 📚 배운 것
### 🏃‍♂️ Try
Docker와 한바탕 전쟁.<br>
직접 빌드하는 경험을 처음 해 봤고 이렇게 진이 다 빠질 줄 몰랐다.<br>

- 이미 빌드한 이미지의 도커파일을 수정하더라도 빌드된 이미지는 영향을 받지 않겠..지? 
  - 다시 빌드해야 한다고?
  - 30분 걸렸다 자그마치 빌드만 30분
- 도커 run 명령어에서 -d 하나 빠지더니 주피터랩이 실행되고 접속 토큰이 나왔다.
  - -d가 detatch 모드였는데... 이게 어떤 영향을 미친건지 자세히 조사해봐야 한다.
- EC2에서 원격 접속을 하려면 8888 포트(주피터용), 22포트(ssh)가 열려있어야 한다.
- 도커파일의 CMD를 잘 설정해 놓으면 컨테이너 실행 시 마다 귀찮은 명령어를 칠 일이 상당히 줄어든다.
  - 이 또한 설계 후 작업의 중요성이리라.
  - 
  
미션 5
- 멀티프로세싱으로 1.6M 라인을 처리하려고 했으나 jupyter 문제로 일단 보류.
- 긍정/부정으로 나누고 단어구름을 봤더니 'lol', 'now' 등의 단어가 둘 다 가장 앞쪽에 등장했다.
  - 이런 단어들은 어떤 감정의 문장에도 사용할 수 있기에 공통으로 등장한 단어들을 배제했다.
    - 다시 생각해보니 무작정 차집합 하면 안되고 비율 컷이나 공통이더라도 양측 비율 차가 크면 살려야 했다.
  - 이렇게 하니 부정은 hate, sad 등이, 긍정은 thanks, good, luck 등이 출현했다.
    - good이 여러개 뜬다. 대체 왜?  200개를 못채워서 그럴 수도? 내일 다시 체크해야겠다.
    - 
---
프로세스에 작업을 할당하는 과정이 잘 이해가 가지 않는다.<br>
큐를 파라미터로 넘겨야 하는데 Pool.map에서는 iterable하지 않다고 까인다.
- multiprocess.Manager를 사용해서 pickling 가능한 큐 객체를 만들 수 있다고 한다.
- Process , Pool.apply를 사용해도 된다고 한다.
- functools.partial로 파라미터를 고정하고 다른 부분만 iterable로 넘기는 방법도 있다.
- 실패한 방법:
  - starmap() -> 큐 객체는 pickling 불가하므로 직접 전달 시 문제 발생.

멀티프로세싱은 GIL의 영향을 받지 않아 CPU-bound 작업에 효과적이다.

### Problem
jupyter notebook에서 AttributeError: Can't get attribute 'pull_task' on <module '__main__' (built-in)> 에러가 발생한다.<br>
> ⚠️ GPT는 이렇게 말했다 1: Jupyter Notebook의 구조를 피하려면, 멀티프로세싱 관련 코드를 별도 .py 파일로 작성한 후 이를 subprocess를 통해 호출할 수도 있어.
> ⚠️ GPT는 이렇게 말했다 2: Python의 멀티프로세싱 코드는 항상 if __name__ == "__main__": 조건문 안에 있어야 해. Jupyter Notebook에서도 이 규칙을 지켜야 문제가 해결돼.
>     이건 안됐다. 
> 정녕 주피터 노트북 내부에서는 해결이 안된단 말인가?

### Keep
셜계 후 작업은 역시 중요하다.<br>
이번 미션 5도 160만개 라인을 쪼개서 병렬로 전처리 할 계획을 했으나 대차게 꼬였긴 하다.<br>
도커파일의 CMD만 잘 설정해도 명령어 타이핑을 많이 줄이니 이미지 설계할 때 용도와 진입 후 바로 실행되어야 할 작업들을 미리 생각해 놓는게 중요하다<br>

