# 설계 문서

## 개요

기존 프론트엔드와 백엔드 구조를 최대한 유지하면서, 투자 성향에 따른 AI 모델 연동과 데이터 표시 기능을 구현합니다. 백엔드의 기존 API를 활용하고, 프론트엔드에서는 데이터 연동 로직만 추가하여 사용자에게 맞춤형 AI 분석 결과를 제공합니다.

## 아키텍처

### 전체 구조
```
Frontend (React/TypeScript)
├── InvestmentStyleSelection.tsx (기존 유지)
├── StockDetail.tsx (데이터 연동 로직 추가)
├── API Client (기존 확장)
└── Investment Style Context (매핑 로직 수정)

Backend (FastAPI - 기존 유지)
├── /predict/marl (marl_4agent)
├── /predict/model2 (a2c 대응)
├── /predict/model3 (marl_3agent)
└── /indicators/history
```

### 투자 성향-모델 매핑
- 공격형 → a2c 모델 (백엔드의 /predict/model2 사용)
- 중간형 → marl_4agent 모델 (백엔드의 /predict/marl 사용)  
- 안정형 → marl_3agent 모델 (백엔드의 /predict/model3 사용)

## 컴포넌트 및 인터페이스

### 1. 투자 성향 매핑 수정
**파일:** `src/contexts/InvestmentStyleContext.tsx`

기존 매핑을 백엔드 API 엔드포인트와 일치하도록 수정:
```typescript
export const getModelType = (style: InvestmentStyle): string => {
  switch (style) {
    case '공격형': return 'model2';    // a2c
    case '중간형': return 'marl';      // marl_4agent  
    case '안정형': return 'model3';    // marl_3agent
    default: return 'marl';
  }
};
```

### 2. API 클라이언트 확장
**파일:** `src/api/client.ts`

기존 API 클라이언트에 투자 성향별 예측 함수 추가:
```typescript
// 투자 성향에 따른 예측 API 호출
predictByInvestmentStyle: (modelType: string, features: Record<string, number>) => {
  const endpoint = `/predict/${modelType}`;
  return apiCall(endpoint, {
    method: 'POST',
    body: { features, symbol: '005930' }
  });
}
```

### 3. StockDetail 컴포넌트 데이터 연동
**파일:** `src/components/StockDetail.tsx`

기존 컴포넌트 구조는 유지하고 데이터 로딩 로직만 추가:

#### 상태 관리
```typescript
const [aiData, setAiData] = useState({
  recommendation: '분석 중...',
  aiExplanation: '데이터를 분석하고 있습니다...',
  indicators: {}
});
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);
```

#### 데이터 로딩 로직
```typescript
useEffect(() => {
  const loadAIAnalysis = async () => {
    try {
      setLoading(true);
      const { modelType } = useInvestmentStyle();
      
      // Mock 기술 지표 데이터 (실제로는 주식 데이터에서 계산)
      const mockFeatures = {
        SMA20: 62000, MACD: 0.5, RSI: 65, 
        Stoch_K: 70, EMA12: 61500, EMA26: 60800
      };
      
      const result = await api.predictByInvestmentStyle(modelType, mockFeatures);
      
      setAiData({
        recommendation: translateSignal(result.signal),
        aiExplanation: result.gpt_explanation || '분석 결과를 준비 중입니다.',
        indicators: result.technical_indicators
      });
    } catch (err) {
      setError('분석 데이터를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };
  
  loadAIAnalysis();
}, []);
```

### 4. 투자 성향별 기술 지표 필터링
**파일:** `src/data/indicatorsByStyle.ts`

각 모델별 사용 지표 정의:
```typescript
export const getIndicatorsByModel = (modelType: string) => {
  const indicatorMap = {
    'model2': ['EMA 12', 'EMA 26', 'MACD', '거래량', 'RSI'],           // a2c
    'marl': ['SMA20', 'MACD', 'RSI', 'STOCH_%K', 'KOSPI'],            // marl_4agent
    'model3': ['SMA20', 'RSI', 'STOCH_%K']                            // marl_3agent
  };
  
  return indicatorMap[modelType] || indicatorMap['marl'];
};
```

## 데이터 모델

### AI 예측 응답 인터페이스
```typescript
interface AIAnalysisData {
  recommendation: string;      // "매수" | "매도" | "보유"
  aiExplanation: string;      // GPT 분석 설명
  indicators: Record<string, number>;  // 기술 지표 값들
}
```

### 기술 지표 정보 인터페이스
```typescript
interface IndicatorInfo {
  title: string;
  description: string;        // 백엔드에서 받은 현재 상황 분석
  fullDescription: string;
  interpretationPoints: string[];
}
```

## 오류 처리

### 네트워크 오류 처리
- API 호출 실패 시 기본 메시지 표시
- 재시도 버튼 제공
- 로딩 상태 관리

### 데이터 검증
- API 응답 데이터 유효성 검사
- 필수 필드 누락 시 기본값 사용
- 잘못된 signal 값에 대한 폴백 처리

```typescript
const translateSignal = (signal: string): string => {
  const signalMap = {
    'buy': '매수',
    'sell': '매도', 
    'hold': '보유'
  };
  return signalMap[signal.toLowerCase()] || '분석 중';
};
```

## 테스트 전략

### 단위 테스트
- 투자 성향-모델 매핑 함수 테스트
- API 클라이언트 함수 테스트
- 신호 번역 함수 테스트

### 통합 테스트
- 투자 성향 선택 → AI 분석 → 결과 표시 플로우 테스트
- 각 투자 성향별 올바른 모델 호출 확인
- 오류 상황에서의 적절한 처리 확인

### 사용자 시나리오 테스트
1. 공격형 선택 → StockDetail 진입 → a2c 모델 결과 확인
2. 중간형 선택 → StockDetail 진입 → marl_4agent 모델 결과 확인  
3. 안정형 선택 → StockDetail 진입 → marl_3agent 모델 결과 확인
4. 네트워크 오류 시나리오 테스트

## 성능 고려사항

### 캐싱 전략
- AI 분석 결과는 하루 단위로 캐싱 (오후 6시 업데이트)
- 기술 지표 데이터 로컬 스토리지 활용
- API 호출 최소화를 위한 데이터 재사용

### 로딩 최적화
- 컴포넌트 마운트 시 즉시 로딩 시작
- 로딩 스피너로 사용자 경험 개선
- 오류 발생 시 빠른 피드백 제공

## 보안 고려사항

### API 키 관리
- 환경 변수를 통한 API 키 관리
- 프로덕션 환경에서 API 키 보안 강화

### 데이터 검증
- 백엔드 응답 데이터 검증
- XSS 방지를 위한 텍스트 이스케이프
- 사용자 입력 데이터 검증