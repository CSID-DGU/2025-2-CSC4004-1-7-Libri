// API 응답 데이터 검증 및 폴백 처리 유틸리티

export interface APIResponse {
  model_type: string;
  signal: string;
  confidence_score: number;
  technical_indicators: Record<string, number>;
  gpt_explanation?: string;
  timestamp: string;
}

// API 응답 데이터 유효성 검사
export function validateAPIResponse(data: any): APIResponse | null {
  if (!data || typeof data !== 'object') {
    return null;
  }

  // 필수 필드 검증
  const requiredFields = ['model_type', 'signal', 'confidence_score', 'technical_indicators'];
  for (const field of requiredFields) {
    if (!(field in data)) {
      console.warn(`Missing required field: ${field}`);
      return null;
    }
  }

  // 신호 값 검증
  const validSignals = ['buy', 'sell', 'hold'];
  if (!validSignals.includes(data.signal?.toLowerCase())) {
    console.warn(`Invalid signal: ${data.signal}`);
    return null;
  }

  // 신뢰도 점수 검증
  if (typeof data.confidence_score !== 'number' || data.confidence_score < 0 || data.confidence_score > 1) {
    console.warn(`Invalid confidence_score: ${data.confidence_score}`);
    return null;
  }

  // 기술 지표 검증
  if (!data.technical_indicators || typeof data.technical_indicators !== 'object') {
    console.warn('Invalid technical_indicators');
    return null;
  }

  return {
    model_type: data.model_type,
    signal: data.signal,
    confidence_score: data.confidence_score,
    technical_indicators: data.technical_indicators,
    gpt_explanation: data.gpt_explanation || '',
    timestamp: data.timestamp || new Date().toISOString()
  };
}

// 기본값 제공 함수
export function getDefaultAIData(modelType: string) {
  const defaultExplanations: Record<string, string> = {
    'model2': 'A2C 모델 분석: 공격적인 투자 전략을 바탕으로 한 분석 결과입니다.',
    'marl': 'MARL 4-Agent 모델 분석: 다중 에이전트 강화학습을 통한 균형잡힌 분석 결과입니다.',
    'model3': 'MARL 3-Agent 모델 분석: 안정적인 투자를 위한 보수적 분석 결과입니다.'
  };

  return {
    recommendation: '분석 중',
    aiExplanation: defaultExplanations[modelType] || '분석을 진행하고 있습니다.',
    indicators: {}
  };
}

// 모델 타입 검증 및 폴백
export function validateModelType(modelType: string): string {
  const validModels = ['model2', 'marl', 'model3'];
  if (validModels.includes(modelType)) {
    return modelType;
  }
  
  console.warn(`Invalid model type: ${modelType}, falling back to 'marl'`);
  return 'marl'; // 기본값으로 폴백
}

// 네트워크 오류 타입 판별
export function getErrorMessage(error: any): string {
  if (!error) return '알 수 없는 오류가 발생했습니다.';
  
  if (error.name === 'TypeError' && error.message.includes('fetch')) {
    return '네트워크 연결을 확인해주세요.';
  }
  
  if (error.message?.includes('500')) {
    return '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
  }
  
  if (error.message?.includes('404')) {
    return '요청한 데이터를 찾을 수 없습니다.';
  }
  
  if (error.message?.includes('401') || error.message?.includes('403')) {
    return '인증 오류가 발생했습니다.';
  }
  
  return error.message || '데이터를 불러오는데 실패했습니다.';
}

// 재시도 로직을 위한 지연 함수
export function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// 지수 백오프를 사용한 재시도 함수
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000
): Promise<T> {
  let lastError: any;
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      
      if (i === maxRetries - 1) {
        throw error;
      }
      
      const delayTime = baseDelay * Math.pow(2, i);
      await delay(delayTime);
    }
  }
  
  throw lastError;
}