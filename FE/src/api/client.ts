const API_URL = import.meta.env.VITE_API_URL || 'https://libri-backend.onrender.com';
const API_KEY = import.meta.env.VITE_API_KEY || '';

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  headers?: Record<string, string>;
  body?: any;
}

async function apiCall(endpoint: string, options: RequestOptions = {}) {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (API_KEY) {
    headers['X-API-Key'] = API_KEY;
  }

  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: options.method || 'GET',
      headers,
      body: options.body ? JSON.stringify(options.body) : undefined,
    });

    if (!response.ok) {
      let errorMessage = `API Error: ${response.status} ${response.statusText}`;
      let errorBody: any = null;
      try {
        errorBody = await response.json();
        if (typeof errorBody === "string") {
          errorMessage = errorBody;
        } else if (errorBody?.detail) {
          errorMessage = Array.isArray(errorBody.detail)
            ? errorBody.detail.map((d: any) => d.msg || d.detail || "").join(", ")
            : errorBody.detail;
        }
      } catch {
        // ignore JSON parse errors and keep default message
      }
      const error = new Error(errorMessage);
      (error as any).status = response.status;
      (error as any).body = errorBody;
      throw error;
    }

    return response.json();
  } catch (error) {
    // 네트워크 오류나 연결 실패 시 더 명확한 메시지 제공
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error(`백엔드 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요. (${API_URL})`);
    }
    throw error;
  }
}

export const api = {
  // 헬스 체크
  health: () => apiCall('/'),

  // AI 예측 관련
  predictByInvestmentStyle: (symbol: string, investmentStyle: 'aggressive' | 'conservative') => {
    // 공격형 -> a2c, 안정형 -> marl
    const mode = investmentStyle === 'aggressive' ? 'a2c' : 'marl';
    return apiCall(`/ai/predict`, {
      method: 'POST',
      body: { 
        symbol,
        mode,
        investment_style: investmentStyle 
      },
    });
  },

  // 주가 히스토리 조회
  getStockHistory: (symbol: string, days: number = 30) =>
    apiCall(`/stocks/${symbol}/history?days=${days}`),

  // 포트폴리오 관련
  getPortfolio: (userId: number) =>
    apiCall(`/portfolio/${userId}`),

  updatePortfolio: (
    userId: number,
    payload: {
      initial_investment?: number;
      investment_style?: string;
      holdings?: Array<{
        symbol: string;
        quantity: number;
        avg_price: number;
      }>;
    },
  ) =>
    apiCall(`/portfolio/${userId}`, {
      method: 'POST',
      body: payload,
    }),

  addHolding: (userId: number, holding: {
    symbol: string;
    quantity: number;
    avg_price: number;
  }) =>
    apiCall(`/portfolio/${userId}/holdings`, {
      method: 'POST',
      body: holding,
    }),

  sellHolding: (userId: number, sellData: {
    symbol: string;
    quantity: number;
    sell_price: number;
  }) =>
    apiCall(`/portfolio/${userId}/sell`, {
      method: 'POST',
      body: sellData,
    }),

  // 투자 내역 조회
  getInvestmentHistory: (userId: number) =>
    apiCall(`/portfolio/${userId}/history`),

  // 사용자 관련
  signup: (email: string, password: string) =>
    apiCall('/users/signup', {
      method: 'POST',
      body: { email, password },
    }),

  login: (email: string, password: string) =>
    apiCall('/users/login', {
      method: 'POST',
      body: { email, password },
    }),

  getUser: (userId: number) =>
    apiCall(`/users/me?user_id=${userId}`),

  updateInvestmentStyle: (userId: number, investmentStyle: string) =>
    apiCall(`/users/${userId}/investment-style`, {
      method: 'PUT',
      body: { investment_style: investmentStyle },
    }),

  // AI 거래 히스토리 조회
  getAIHistory: (modelType: 'a2c' | 'marl', startDate: string) =>
    apiCall(`/ai/history?model_type=${modelType}&start_date=${startDate}`),

  // 온보딩 완료
  completeOnboarding: (userId: number, onboardingData: {
    initial_investment: number;
    investment_style: string;
    holdings: Array<{
      symbol: string;
      quantity: number;
      avg_price: number;
    }>;
  }) =>
    apiCall(`/users/${userId}/onboarding`, {
      method: 'POST',
      body: onboardingData,
    }),
};
