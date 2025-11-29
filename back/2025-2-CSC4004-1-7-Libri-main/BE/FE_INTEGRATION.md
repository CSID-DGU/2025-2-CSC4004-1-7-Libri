# Frontend 연동 가이드

## 모델 선택 플로우

FE에서 사용자가 3개 모델 중 하나를 선택하여 예측을 받을 수 있습니다.

### 1. 모델 목록 가져오기

```javascript
// 사용 가능한 모델 목록 조회
const getModelList = async () => {
  const response = await fetch('http://localhost:8000/models/list', {
    headers: {
      'X-API-Key': 'your_api_key'
    }
  });
  const data = await response.json();
  return data.models;
  // [
  //   {
  //     id: "marl_4agent",
  //     name: "MARL 4-Agent",
  //     description: "4개 에이전트 기반 멀티 에이전트 강화학습 모델",
  //     endpoint: "/predict/marl",
  //     status: "available"
  //   },
  //   ...
  // ]
};
```

### 2. 선택된 모델로 예측 요청

```javascript
// 사용자가 선택한 모델로 예측
const getPrediction = async (modelId, marketData) => {
  // 모델 ID에 따라 엔드포인트 결정
  const endpoints = {
    'marl_4agent': '/predict/marl',
    'model_2': '/predict/model2',
    'model_3': '/predict/model3'
  };
  
  const response = await fetch(`http://localhost:8000${endpoints[modelId]}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': 'your_api_key'
    },
    body: JSON.stringify({
      symbol: "005930",
      features: marketData
    })
  });
  
  const prediction = await response.json();
  return prediction;
  // {
  //   model_type: "marl_4agent",
  //   signal: "매수",
  //   confidence_score: 0.85,
  //   technical_indicators: {...},
  //   gpt_explanation: "RSI와 MACD 지표가...",
  //   timestamp: "2024-11-21T10:30:00"
  // }
};
```

### 3. React 예시 컴포넌트

```jsx
import React, { useState, useEffect } from 'react';

function ModelSelector() {
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState('marl_4agent');
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // 모델 목록 로드
    fetch('http://localhost:8000/models/list', {
      headers: { 'X-API-Key': 'your_api_key' }
    })
      .then(res => res.json())
      .then(data => setModels(data.models));
  }, []);

  const handlePredict = async () => {
    setLoading(true);
    
    const endpoints = {
      'marl_4agent': '/predict/marl',
      'model_2': '/predict/model2',
      'model_3': '/predict/model3'
    };

    const marketData = {
      symbol: "005930",
      features: {
        SMA20: 70000,
        MACD: 500,
        RSI: 65,
        // ... 기타 지표
      }
    };

    try {
      const response = await fetch(
        `http://localhost:8000${endpoints[selectedModel]}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': 'your_api_key'
          },
          body: JSON.stringify(marketData)
        }
      );
      
      const result = await response.json();
      setPrediction(result);
    } catch (error) {
      console.error('예측 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>AI 모델 선택</h2>
      
      {/* 모델 선택 드롭다운 */}
      <select 
        value={selectedModel} 
        onChange={(e) => setSelectedModel(e.target.value)}
      >
        {models.map(model => (
          <option 
            key={model.id} 
            value={model.id}
            disabled={model.status !== 'available'}
          >
            {model.name} ({model.status})
          </option>
        ))}
      </select>

      {/* 예측 버튼 */}
      <button onClick={handlePredict} disabled={loading}>
        {loading ? '분석 중...' : 'AI 예측 받기'}
      </button>

      {/* 예측 결과 표시 */}
      {prediction && (
        <div className="prediction-result">
          <h3>예측 결과</h3>
          <p><strong>모델:</strong> {prediction.model_type}</p>
          <p><strong>신호:</strong> {prediction.signal}</p>
          <p><strong>신뢰도:</strong> {(prediction.confidence_score * 100).toFixed(1)}%</p>
          <p><strong>AI 해석:</strong> {prediction.gpt_explanation}</p>
          
          <h4>기술 지표</h4>
          <ul>
            {Object.entries(prediction.technical_indicators).map(([key, value]) => (
              <li key={key}>{key}: {value}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default ModelSelector;
```

### 4. Vue.js 예시

```vue
<template>
  <div class="model-selector">
    <h2>AI 모델 선택</h2>
    
    <select v-model="selectedModel">
      <option 
        v-for="model in models" 
        :key="model.id" 
        :value="model.id"
        :disabled="model.status !== 'available'"
      >
        {{ model.name }} ({{ model.status }})
      </option>
    </select>

    <button @click="getPrediction" :disabled="loading">
      {{ loading ? '분석 중...' : 'AI 예측 받기' }}
    </button>

    <div v-if="prediction" class="result">
      <h3>예측 결과</h3>
      <p><strong>신호:</strong> {{ prediction.signal }}</p>
      <p><strong>신뢰도:</strong> {{ (prediction.confidence_score * 100).toFixed(1) }}%</p>
      <p><strong>AI 해석:</strong> {{ prediction.gpt_explanation }}</p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      models: [],
      selectedModel: 'marl_4agent',
      prediction: null,
      loading: false
    };
  },
  
  mounted() {
    this.loadModels();
  },
  
  methods: {
    async loadModels() {
      const response = await fetch('http://localhost:8000/models/list', {
        headers: { 'X-API-Key': 'your_api_key' }
      });
      const data = await response.json();
      this.models = data.models;
    },
    
    async getPrediction() {
      this.loading = true;
      
      const endpoints = {
        'marl_4agent': '/predict/marl',
        'model_2': '/predict/model2',
        'model_3': '/predict/model3'
      };
      
      try {
        const response = await fetch(
          `http://localhost:8000${endpoints[this.selectedModel]}`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-API-Key': 'your_api_key'
            },
            body: JSON.stringify({
              symbol: "005930",
              features: {
                SMA20: 70000,
                MACD: 500,
                RSI: 65
              }
            })
          }
        );
        
        this.prediction = await response.json();
      } catch (error) {
        console.error('예측 실패:', error);
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>
```

## API 응답 형식

모든 모델의 예측 응답은 동일한 형식을 따릅니다:

```json
{
  "model_type": "marl_4agent",
  "signal": "매수",
  "confidence_score": 0.85,
  "technical_indicators": {
    "SMA20": 70000.0,
    "MACD": 500.0,
    "RSI": 65.0,
    "Stoch_K": 70.0
  },
  "gpt_explanation": "RSI와 MACD 지표가 상승 추세를 보이고 있어 매수 신호를 생성했습니다.",
  "timestamp": "2024-11-21T10:30:00.123456"
}
```

## 에러 처리

```javascript
const handlePrediction = async (modelId, marketData) => {
  try {
    const response = await fetch(endpoint, options);
    
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('API 키가 유효하지 않습니다.');
      } else if (response.status === 500) {
        throw new Error('모델 예측 중 오류가 발생했습니다.');
      }
    }
    
    return await response.json();
  } catch (error) {
    console.error('예측 요청 실패:', error);
    // 사용자에게 에러 메시지 표시
  }
};
```

## 모델별 특징

### MARL 4-Agent
- 4개 에이전트 (단기/장기/위험/감성) 기반
- 가장 복잡한 분석
- 더 많은 기술 지표 필요

### Model 2
- 중간 복잡도
- 빠른 응답 시간

### Model 3
- 간단한 분석
- 기본 지표만 필요
