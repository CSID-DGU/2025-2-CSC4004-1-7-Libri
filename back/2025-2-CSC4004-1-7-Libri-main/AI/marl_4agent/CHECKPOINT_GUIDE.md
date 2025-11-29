# 체크포인트 시스템 사용 가이드

## 개요
학습 중단 시 진행 상황을 저장하고, 나중에 이어서 학습할 수 있는 체크포인트 시스템입니다.

## 주요 기능

### 1. 자동 체크포인트 저장
- 학습 중 일정 간격마다 자동으로 진행 상황 저장
- 저장 내용: 에피소드 번호, 총 스텝 수, 모델 가중치, 옵티마이저 상태

### 2. 학습 재개
- 중단된 지점부터 학습 재개 가능
- 에피소드 번호와 스텝 수 자동 복원

### 3. 저장 파일
- `checkpoint.pth`: 모델 가중치 및 학습 상태
- `checkpoint_meta.json`: 메타 정보 (에피소드, 스텝, 타임스탬프)
- `qmix_model.pth`: 최종 학습 완료 모델

## 사용 방법

### 기본 학습 (체크포인트 자동 저장)
```bash
# 10 에피소드마다 체크포인트 저장 (기본값)
python main.py --capital 10000000

# 5 에피소드마다 체크포인트 저장
python main.py --capital 10000000 --checkpoint-interval 5

# 1 에피소드마다 체크포인트 저장 (자주 저장)
python main.py --capital 10000000 --checkpoint-interval 1
```

### 중단된 학습 재개
```bash
# checkpoint.pth에서 자동으로 로드하여 재개
python main.py --resume

# 투자 금액 지정하여 재개
python main.py --resume --capital 10000000

# 체크포인트 저장 간격 변경하여 재개
python main.py --resume --checkpoint-interval 5
```

### 기존 모델 로드 후 추가 학습
```bash
# 기존 모델 로드 후 추가 학습
python main.py --load-model qmix_model.pth --capital 10000000

# 기존 모델 로드 후 백테스트만 수행 (학습 건너뛰기)
python main.py --load-model qmix_model.pth --skip-training
```

### 백테스트만 수행
```bash
# 학습된 모델로 백테스트
python backtest.py --model qmix_model.pth --capital 10000000

# 체크포인트에서 백테스트
python backtest.py --model checkpoint.pth --capital 20000000
```

## 체크포인트 메타 정보 확인

`checkpoint_meta.json` 파일을 열어 현재 진행 상황 확인:

```json
{
  "episode": 50,
  "total_steps": 125000,
  "timestamp": "2025-11-26 14:30:45"
}
```

## 실전 시나리오

### 시나리오 1: 학습 중 중단 발생
```bash
# 1. 학습 시작 (10 에피소드마다 자동 저장)
python main.py --capital 10000000 --checkpoint-interval 10

# 2. 학습 중 Ctrl+C로 중단 또는 시스템 종료

# 3. 나중에 재개
python main.py --resume
```

### 시나리오 2: 단계별 학습
```bash
# 1단계: 50 에피소드 학습
python main.py --capital 10000000
# (config.py에서 NUM_EPISODES=50으로 설정)

# 2단계: 추가 50 에피소드 학습
python main.py --load-model qmix_model.pth --capital 10000000
# (config.py에서 NUM_EPISODES=100으로 변경)

# 3단계: 최종 백테스트
python backtest.py --model qmix_model.pth --capital 10000000
```

### 시나리오 3: 실험 및 비교
```bash
# 실험 1: 기본 설정으로 학습
python main.py --capital 10000000
mv qmix_model.pth qmix_model_v1.pth

# 실험 2: 다른 하이퍼파라미터로 학습
# (config.py 수정 후)
python main.py --capital 10000000
mv qmix_model.pth qmix_model_v2.pth

# 비교: 두 모델 백테스트
python backtest.py --model qmix_model_v1.pth --capital 10000000
python backtest.py --model qmix_model_v2.pth --capital 10000000
```

## 주의사항

1. **체크포인트 간격 설정**
   - 너무 자주 저장: 학습 속도 저하
   - 너무 드물게 저장: 중단 시 많은 진행 손실
   - 권장: 10~20 에피소드 간격

2. **디스크 공간**
   - 체크포인트 파일은 약 10~50MB
   - 충분한 디스크 공간 확보 필요

3. **재개 시 주의**
   - `--resume` 사용 시 `config.py`의 `NUM_EPISODES`가 이전보다 크거나 같아야 함
   - 예: 50 에피소드에서 중단 → `NUM_EPISODES=100`으로 설정 후 재개

4. **백업 권장**
   - 중요한 체크포인트는 별도 백업
   ```bash
   cp checkpoint.pth checkpoint_backup_ep50.pth
   cp checkpoint_meta.json checkpoint_backup_ep50_meta.json
   ```

## 로그 파일 활용

학습 로그를 파일로 저장하여 나중에 참고:

```bash
# 로그를 파일로 저장하면서 화면에도 출력
python main.py --capital 10000000 2>&1 | tee training_log.txt

# 재개 시에도 로그 저장
python main.py --resume 2>&1 | tee -a training_log.txt
```

## 문제 해결

### 체크포인트 로드 실패
```bash
# 체크포인트 파일 확인
ls -lh checkpoint.pth checkpoint_meta.json

# 체크포인트 삭제 후 처음부터 시작
rm checkpoint.pth checkpoint_meta.json
python main.py --capital 10000000
```

### 모델 호환성 문제
- 코드 변경 후 이전 체크포인트가 호환되지 않을 수 있음
- 이 경우 처음부터 재학습 필요

## 성능 모니터링

학습 중 다른 터미널에서 진행 상황 확인:

```bash
# 메타 정보 확인
cat checkpoint_meta.json

# 실시간 로그 모니터링
tail -f training_log.txt

# 그래프 생성 확인
ls -lh backtest_results.png
```
