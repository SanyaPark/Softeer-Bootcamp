# 1/10 회고록 <br>

### 🌅 하루 감상
아.. 야심차게 조회를 원하는 시점의 데이터를 보여주게 하는 작업을 했지만<br>
점점 복잡해지다 결국 감당이 안되어 코드 백업만 해 놓고 재설계만 했다.<br>
<br>


### 📚 What I Learned?

- 처음부터 얼마나 유연하게 설계하는지에 따라 나중의 변화에 쉽게 대응할 수 있는지가 결정된다<br>
  가능한 상황들을 생각해 보고 확장성 있게 설계해야 한다.
- 판다스 데이터프레임 다룰 때 apply로 단순 연산하는 것 보다 벡터연산을 거는 것이 더 성능이 좋다
- ETL의 각 과정에서 시스템의 어떤 부분에 부하가 걸리는지, 프로세스 안에서 세부 프로세스를 쪼갤 수 있는지 등을 생각하고 각 단계 별 비용을 잘 산출해야 한다.

- Extract 과정은 보통 네트워크를 타므로 에러가 날 확률이 상대적으로 높다.<br>

- 외부 변화에 대응한다는 것이 각 과정을 충분히 추상화시켜 한 프로세스의 변경이 다른 프로세스에 영향을 안주도록 해야 한다는 것임을 알았다.
 
- 판다스로 웹 테이블을 긁었는데 내부 구현 상 리스트를 생성한다는 것을 알았다.<br>
  JSON을 스트림으로 저장하는 방식과 청크 단위로 데이터프레임을 만들고 JSON으로 합치는 방식이 더 IO부하를 줄이고 메모리 사용량을 아낄 수 있을 것 같다.<br>



### 💾 Keep
- 요구사항에 대해 충분히 생각하기
- 작은 데이터에서는 눈에 보이지 않는 차이가 빅-데이터에서는 유의미한 차이를 발생시킬 수 있다는것 유념
- 좀 복잡해진다 싶으면 무작정 코드만 치는건 아닌지 생각해보자

### ⚠️ Problem
- 데이터베이스 락이 걸려 생각지도 못한 상황을 맞이했다.<br>
  SQLite가 다른 데이터베이스와 어떤 차이가 있는지, 그로 인해 설계를 어떻게 수정해야 하는지를 생각해야 한다



### 🏃‍♂️ Try
- 깃은 뭐 잘못 누르면 올리기도 안되고 먹통이 되는 경험을 많이 해서 아직도 푸시 / 풀 정도만 한다 <br>
  프로젝트 하면서 좀 더 안전하고 유용하게 쓰는 법을 익혀보기
