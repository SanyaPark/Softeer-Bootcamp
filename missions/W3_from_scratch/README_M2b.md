### 파이썬에서 Bash 쉘 커맨드를 실행하는 방법
파이썬에서 Bash 명령어를 실행하려면 ```subprocess``` 모듈을 사용합니다.
```bash
import subprocess

# Bash 명령 실행
result = subprocess.run(['ls', '-l'], capture_output=True, text=True)

# 출력 확인
print(result.stdout)
if result.returncode != 0:  # 오류 확인
    print(f"Error: {result.stderr}")
```

