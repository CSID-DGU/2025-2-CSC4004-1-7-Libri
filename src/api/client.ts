const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
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

  const response = await fetch(`${API_URL}${endpoint}`, {
    method: options.method || 'GET',
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

export const api = {
  // 헬스 체크
  health: () => apiCall('/health'),

  // 모델 관련
  getModels: () => apiCall('/models/list'),
  getModelStatus: () => apiCall('/models/status'),

  // 예측 관련
  predictMARL: (features: number[]) =>
    apiCall('/predict/marl', {
      method: 'POST',
      body: { features, symbol: 'AAPL' },
    }),

  predictModel2: (features: number[]) =>
    apiCall('/predict/model2', {
      method: 'POST',
      body: { features, symbol: 'AAPL' },
    }),

  predictModel3: (features: number[]) =>
    apiCall('/predict/model3', {
      method: 'POST',
      body: { features, symbol: 'AAPL' },
    }),

  // 포트폴리오 관련
  setPortfolioCapital: (portfolioId: string, initialCapital: number) =>
    apiCall('/portfolio/capital', {
      method: 'POST',
      body: { portfolio_id: portfolioId, initial_capital: initialCapital },
    }),

  getPortfolio: (portfolioId: string) =>
    apiCall(`/portfolio/${portfolioId}`),

  // 투자 내역 관련
  createInvestmentRecord: (data: {
    portfolio_id: string;
    model_type: string;
    signal: string;
    entry_price: number;
    shares: number;
    portfolio_value: number;
    pnl: number;
    confidence_score: number;
    gpt_explanation?: string;
  }) =>
    apiCall('/investment/record', {
      method: 'POST',
      body: data,
    }),

  getInvestmentHistory: (filters?: {
    portfolio_id?: string;
    model_type?: string;
    start_date?: string;
    end_date?: string;
    page?: number;
    page_size?: number;
  }) => {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) params.append(key, String(value));
      });
    }
    return apiCall(`/investment/history?${params.toString()}`);
  },

  getPerformanceMetrics: (filters?: {
    portfolio_id?: string;
    model_type?: string;
    start_date?: string;
    end_date?: string;
  }) => {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) params.append(key, String(value));
      });
    }
    return apiCall(`/investment/metrics?${params.toString()}`);
  },

  // 기술 지표 관련
  getIndicatorHistory: (filters?: {
    symbol?: string;
    indicator_name?: string;
    start_date?: string;
    end_date?: string;
    aggregation?: string;
    limit?: number;
  }) => {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) params.append(key, String(value));
      });
    }
    return apiCall(`/indicators/history?${params.toString()}`);
  },
};