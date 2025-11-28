import { InvestmentStyle } from '../contexts/InvestmentStyleContext';

export interface IndicatorInfo {
  id: string;
  title: string;
  value: string;
  status: 'positive' | 'negative' | 'neutral';
  shortDescription: string;
  detailedDescription: string;
  interpretationPoints: string[];
}

// 공격형 지표
export const aggressiveIndicators: IndicatorInfo[] = [
  {
    id: 'ema12',
    title: 'EMA 12',
    value: '상승',
    status: 'positive',
    shortDescription: '단기 흐름이 장기 흐름보다 강해지며, 최근 주가가 상승세를 타고 있습니다.',
    detailedDescription: 'EMA(지수이동평균선)은 최근 가격에 더 큰 비중을 두고 계산한 평균선이에요. 숫자(12)는 12일 동안의 평균을 의미합니다.',
    interpretationPoints: [
      '단기(EMA12)가 장기(EMA26)를 뚫으면 상승 신호',
      '반대로 내려가면 하락 신호'
    ]
  },
  {
    id: 'ema26',
    title: 'EMA 26',
    value: '상승',
    status: 'positive',
    shortDescription: '단기 흐름이 장기 흐름보다 강해지며, 최근 주가가 상승세를 타고 있습니다.',
    detailedDescription: 'EMA(지수이동평균선)은 최근 가격에 더 큰 비중을 두고 계산한 평균선이에요. 숫자(26)는 26일 동안의 평균을 의미합니다.',
    interpretationPoints: [
      '장기 추세를 확인하는 지표로 활용',
      'EMA12와 함께 보면서 추세 전환 시점 파악'
    ]
  },
  {
    id: 'macd',
    title: 'MACD',
    value: '하향 돌파',
    status: 'negative',
    shortDescription: 'MACD가 시그널선을 하향 돌파하며 매도 신호가 강화되고 있습니다.',
    detailedDescription: 'MACD(이동평균수렴확산)는 단기와 장기 이동평균선의 차이를 이용한 추세 추종 지표입니다. 추세의 방향과 강도를 동시에 파악할 수 있어요.',
    interpretationPoints: [
      'MACD선이 시그널선을 상향 돌파하면 매수 신호',
      'MACD선이 시그널선을 하향 돌파하면 매도 신호',
      '0선 위에 있으면 상승 추세, 아래면 하락 추세'
    ]
  },
  {
    id: 'volume',
    title: '거래량',
    value: '증가',
    status: 'positive',
    shortDescription: '거래량이 평균 대비 증가하며 추세에 대한 시장 참여도가 높습니다.',
    detailedDescription: '거래량은 특정 기간 동안 거래된 주식의 수량을 나타냅니다. 가격 변동과 함께 분석하면 추세의 신뢰도를 확인할 수 있어요.',
    interpretationPoints: [
      '상승과 함께 거래량 증가는 강한 상승 신호',
      '하락과 함께 거래량 증가는 강한 하락 신호',
      '거래량 없는 가격 변동은 신뢰도가 낮음'
    ]
  },
  {
    id: 'kospi',
    title: 'KOSPI',
    value: '2,450',
    status: 'positive',
    shortDescription: '시장 지수 대비 상대적으로 강세를 보이며, 시장 평균보다 높은 상승 탄력을 유지하고 있습니다.',
    detailedDescription: 'KOSPI는 한국 종합주가지수로, 전체 시장의 흐름을 나타냅니다. 개별 종목이 시장 대비 얼마나 강한지 비교할 수 있어요.',
    interpretationPoints: [
      '시장이 상승하는데 종목도 상승하면 강세',
      '시장이 하락하는데 종목이 상승하면 매우 강세',
      '시장 대비 상대적 강도로 투자 판단'
    ]
  },
  {
    id: 'sma20',
    title: 'SMA20',
    value: '상승',
    status: 'positive',
    shortDescription: '현재 주가가 장기 이동평균선을 상회하며 중기적 상승 추세를 유지하고 있어요.',
    detailedDescription: 'SMA(단순이동평균선)는 일정 기간 동안의 종가를 산술 평균한 값입니다. 20일 평균은 중기 추세를 나타내요.',
    interpretationPoints: [
      '주가가 SMA20 위에 있으면 상승 추세',
      '주가가 SMA20 아래로 떨어지면 하락 신호',
      '장기 투자 시 중요한 지지/저항선으로 활용'
    ]
  },
  {
    id: 'rsi',
    title: 'RSI',
    value: '65',
    status: 'neutral',
    shortDescription: 'RSI가 과매수 구간(70 이상)에 진입하여 단기 조정 가능성이 있습니다.',
    detailedDescription: 'RSI(상대강도지수)는 가격의 상승과 하락 강도를 비교하여 과매수/과매도 상태를 판단하는 지표입니다. 0~100 사이의 값을 가져요.',
    interpretationPoints: [
      'RSI 70 이상은 과매수 구간, 조정 가능성',
      'RSI 30 이하는 과매도 구간, 반등 가능성',
      '50을 기준으로 상승/하락 추세 판단'
    ]
  },
  {
    id: 'stoch_k',
    title: 'STOCH_%K',
    value: '75',
    status: 'neutral',
    shortDescription: '스토캐스틱이 과매수 구간(80 이상)에 머물며 하락 반전 가능성이 있습니다.',
    detailedDescription: '스토캐스틱은 일정 기간 동안의 가격 변동 폭 중 현재 가격의 위치를 백분율로 나타낸 지표입니다. 과매수/과매도를 빠르게 포착해요.',
    interpretationPoints: [
      '%K가 80 이상에서 하락 전환하면 매도 신호',
      '%K가 20 이하에서 상승 전환하면 매수 신호',
      '%K와 %D의 교차로 매매 타이밍 포착'
    ]
  },
  {
    id: 'vix',
    title: 'VIX',
    value: '상승',
    status: 'negative',
    shortDescription: '거래량이 평균 대비 증가하며 추세에 대한 시장 참여도가 높습니다.',
    detailedDescription: 'VIX(변동성 지수)는 시장의 불확실성과 공포 수준을 나타냅니다. 수치가 높을수록 시장 불안이 크다는 의미입니다.',
    interpretationPoints: [
      'VIX 20 이상은 시장 불안이 높은 상태',
      'VIX 하락은 시장 안정화 신호',
      '급격한 VIX 상승은 조정 국면 진입 신호'
    ]
  },
  {
    id: 'bollinger_band_b',
    title: 'Bollinger Band_B',
    value: '수축',
    status: 'neutral',
    shortDescription: '볼린저 밴드가 수축하며 변동성이 낮은 구간에 진입했습니다. 추후 급등락 가능성에 유의해야 합니다.',
    detailedDescription: '볼린저 밴드는 주가의 변동성을 나타내는 지표입니다. 밴드가 수축하면 변동성이 낮고, 확장하면 변동성이 높은 상태입니다.',
    interpretationPoints: [
      '밴드 상단 돌파 시 상승 추세 강화',
      '밴드 하단 이탈 시 하락 추세 강화',
      '밴드 수축 후 확장은 큰 변동 신호'
    ]
  },
  {
    id: 'bb_bw',
    title: 'BB_BW',
    value: '수축',
    status: 'neutral',
    shortDescription: '볼린저 밴드가 수축하며 변동성이 낮은 구간에 진입했습니다. 추후 급등락 가능성에 유의해야 합니다.',
    detailedDescription: 'BB_BW(Bollinger Band Width)는 볼린저 밴드의 폭을 나타내는 지표입니다. 폭이 좁을수록 변동성이 낮고, 곧 큰 변동이 올 가능성이 있습니다.',
    interpretationPoints: [
      '폭이 좁아지면 큰 변동 전 신호',
      '폭이 넓어지면 변동성 확대 진행 중',
      '극단적 수축 후 확장은 강한 추세 시작'
    ]
  },
  {
    id: 'atr',
    title: 'ATR',
    value: '상승',
    status: 'neutral',
    shortDescription: 'ATR이 상승하며 가격 변동성이 확대되고 있습니다.',
    detailedDescription: 'ATR(Average True Range)은 가격 변동성을 측정하는 지표입니다. 값이 클수록 변동성이 크다는 것을 의미합니다.',
    interpretationPoints: [
      'ATR 상승은 변동성 증가 신호',
      'ATR 하락은 변동성 감소, 횡보 가능',
      '높은 ATR에서는 손절매 폭 확대 필요'
    ]
  },
  {
    id: 'position',
    title: 'Position',
    value: '둔화',
    status: 'negative',
    shortDescription: '모멘텀이 둔화되며 상승 추세의 에너지가 약화되고 있습니다.',
    detailedDescription: 'Position은 가격의 위치와 모멘텀을 종합적으로 나타내는 지표입니다. 추세의 강도와 지속 가능성을 판단하는데 유용합니다.',
    interpretationPoints: [
      'Position 상승은 추세 가속화',
      'Position 둔화는 추세 약화 신호',
      'Position 전환은 추세 반전 가능성'
    ]
  }
];

// 중간형 지표
export const moderateIndicators: IndicatorInfo[] = [
  {
    id: 'volume',
    title: '거래량',
    value: '증가',
    status: 'positive',
    shortDescription: '거래량이 평균 대비 증가하며 추세에 대한 시장 참여도가 높습니다.',
    detailedDescription: '거래량은 특정 기간 동안 거래된 주식의 수량을 나타냅니다. 가격 변동과 함께 분석하면 추세의 신뢰도를 확인할 수 있어요.',
    interpretationPoints: [
      '상승과 함께 거래량 증가는 강한 상승 신호',
      '하락과 함께 거래량 증가는 강한 하락 신호',
      '거래량 없는 가격 변동은 신뢰도가 낮음'
    ]
  },
  {
    id: 'rsi',
    title: 'RSI',
    value: '72',
    status: 'neutral',
    shortDescription: 'RSI가 과매수 구간(70 이상)에 진입하여 단기 조정 가능성이 있습니다.',
    detailedDescription: 'RSI(상대강도지수)는 가격의 상승과 하락 강도를 비교하여 과매수/과매도 상태를 판단하는 지표입니다. 0~100 사이의 값을 가져요.',
    interpretationPoints: [
      'RSI 70 이상은 과매수 구간, 조정 가능성',
      'RSI 30 이하는 과매도 구간, 반등 가능성',
      '50을 기준으로 상승/하락 추세 판단'
    ]
  },
  {
    id: 'stoch_k',
    title: 'Stoch_K',
    value: '78',
    status: 'neutral',
    shortDescription: '스토캐스틱이 과매수 구간(80 이상)에 머물며 하락 반전 가능성이 있습니다.',
    detailedDescription: '스토캐스틱은 일정 기간 동안의 가격 변동 폭 중 현재 가격의 위치를 백분율로 나타낸 지표입니다. 과매수/과매도를 빠르게 포착해요.',
    interpretationPoints: [
      '%K가 80 이상에서 하락 전환하면 매도 신호',
      '%K가 20 이하에서 상승 전환하면 매수 신호',
      '%K와 %D의 교차로 매매 타이밍 포착'
    ]
  },
  {
    id: 'stoch_d',
    title: 'Stoch_D',
    value: '75',
    status: 'neutral',
    shortDescription: '스토캐스틱이 과매수 구간(80 이상)에 머물며 하락 반전 가능성이 있습니다.',
    detailedDescription: 'Stoch_D는 Stoch_K의 이동평균으로, 보다 완만한 신호를 제공합니다. %K와 %D의 교차로 매매 타이밍을 포착할 수 있습니다.',
    interpretationPoints: [
      '%D가 %K보다 위에 있으면 하락 압력',
      '%D가 %K보다 아래 있으면 상승 압력',
      '두 선의 교차점에서 매매 신호 발생'
    ]
  },
  {
    id: 'atr',
    title: 'ATR',
    value: '상승',
    status: 'neutral',
    shortDescription: 'ATR이 상승하며 가격 변동성이 확대되고 있습니다.',
    detailedDescription: 'ATR(Average True Range)은 가격 변동성을 측정하는 지표입니다. 값이 클수록 변동성이 크다는 것을 의미합니다.',
    interpretationPoints: [
      'ATR 상승은 변동성 증가 신호',
      'ATR 하락은 변동성 감소, 횡보 가능',
      '높은 ATR에서는 손절매 폭 확대 필요'
    ]
  },
  {
    id: 'bollinger_band_b',
    title: 'Bollinger Band_B',
    value: '수축',
    status: 'neutral',
    shortDescription: '볼린저 밴드가 수축하며 변동성이 낮은 구간에 진입했습니다. 추후 급등락 가능성에 유의해야 합니다.',
    detailedDescription: '볼린저 밴드는 주가의 변동성을 나타내는 지표입니다. 밴드가 수축하면 변동성이 낮고, 확장하면 변동성이 높은 상태입니다.',
    interpretationPoints: [
      '밴드 상단 돌파 시 상승 추세 강화',
      '밴드 하단 이탈 시 하락 추세 강화',
      '밴드 수축 후 확장은 큰 변동 신호'
    ]
  },
  {
    id: 'sma20',
    title: 'SMA20',
    value: '상승',
    status: 'positive',
    shortDescription: '현재 주가가 장기 이동평균선을 상회하며 중기적 상승 추세를 유지하고 있어요.',
    detailedDescription: 'SMA(단순이동평균선)는 일정 기간 동안의 종가를 산술 평균한 값입니다. 20일 평균은 중기 추세를 나타내요.',
    interpretationPoints: [
      '주가가 SMA20 위에 있으면 상승 추세',
      '주가가 SMA20 아래로 떨어지면 하락 신호',
      '장기 투자 시 중요한 지지/저항선으로 활용'
    ]
  },
  {
    id: 'macd',
    title: 'MACD',
    value: '하향 돌파',
    status: 'negative',
    shortDescription: 'MACD가 시그널선을 하향 돌파하며 매도 신호가 강화되고 있습니다.',
    detailedDescription: 'MACD(이동평균수렴확산)는 단기와 장기 이동평균선의 차이를 이용한 추세 추종 지표입니다. 추세의 방향과 강도를 동시에 파악할 수 있어요.',
    interpretationPoints: [
      'MACD선이 시그널선을 상향 돌파하면 매수 신호',
      'MACD선이 시그널선을 하향 돌파하면 매도 신호',
      '0선 위에 있으면 상승 추세, 아래면 하락 추세'
    ]
  },
  {
    id: 'vix',
    title: 'VIX',
    value: '상승',
    status: 'negative',
    shortDescription: '거래량이 평균 대비 증가하며 추세에 대한 시장 참여도가 높습니다.',
    detailedDescription: 'VIX(변동성 지수)는 시장의 불확실성과 공포 수준을 나타냅니다. 수치가 높을수록 시장 불안이 크다는 의미입니다.',
    interpretationPoints: [
      'VIX 20 이상은 시장 불안이 높은 상태',
      'VIX 하락은 시장 안정화 신호',
      '급격한 VIX 상승은 조정 국면 진입 신호'
    ]
  },
  {
    id: 'v_kospi',
    title: 'V-KOSPI',
    value: '상승',
    status: 'negative',
    shortDescription: 'V-KOSPI가 상승하며 시장 불확실성이 커지고 있습니다. 보수적인 접근이 필요합니다.',
    detailedDescription: 'V-KOSPI는 한국 시장의 변동성 지수로, 투자자들의 불안 심리를 반영합니다. 높을수록 시장 불확실성이 크다는 신호입니다.',
    interpretationPoints: [
      'V-KOSPI 25 이상은 높은 변동성 구간',
      'V-KOSPI 하락은 시장 안정 신호',
      '급격한 상승은 시장 패닉 가능성'
    ]
  },
  {
    id: 'roa',
    title: 'ROA',
    value: '양호',
    status: 'positive',
    shortDescription: '단기 흐름이 장기 흐름보다 강해지며, 최근 주가가 상승세를 타고 있습니다.',
    detailedDescription: 'ROA(총자산이익률)는 기업이 보유한 자산을 얼마나 효율적으로 활용하여 이익을 창출하는지 나타내는 지표입니다.',
    interpretationPoints: [
      'ROA 5% 이상이면 양호한 수준',
      'ROA 상승은 자산 효율성 개선',
      '업종 평균 대비 ROA 비교 필요'
    ]
  },
  {
    id: 'debt_ratio',
    title: 'DebtRatio',
    value: '양호',
    status: 'positive',
    shortDescription: '시장 지수 대비 상대적으로 강세를 보이며, 시장 평균보다 높은 상승 탄력을 유지하고 있습니다.',
    detailedDescription: '부채비율은 기업의 재무 건전성을 나타내는 지표로, 낮을수록 재무구조가 안정적입니다.',
    interpretationPoints: [
      '부채비율 100% 이하면 건전',
      '부채비율 상승은 재무 위험 증가',
      '업종 특성 고려한 분석 필요'
    ]
  }
];

// 안정형 지표
export const conservativeIndicators: IndicatorInfo[] = [
  {
    id: 'debt_ratio',
    title: 'DebtRatio',
    value: '양호',
    status: 'positive',
    shortDescription: '재무 건전성 양호',
    detailedDescription: '부채비율이 업종 평균보다 낮아 재무 건전성이 양호합니다. 안정적인 재무구조를 바탕으로 장기 투자에 적합합니다.',
    interpretationPoints: [
      '부채비율 100% 이하면 건전',
      '부채비율 상승은 재무 위험 증가',
      '업종 특성 고려한 분석 필요'
    ]
  },
  {
    id: 'roe',
    title: 'ROE',
    value: '15%',
    status: 'positive',
    shortDescription: '자기자본이익률 양호',
    detailedDescription: '자기자본이익률(ROE)이 15%로 양호한 수준을 유지하고 있습니다. 주주 가치 창출 능력이 우수합니다.',
    interpretationPoints: [
      'ROE 10% 이상이면 우수',
      'ROE 상승은 수익성 개선',
      '지속 가능한 ROE가 중요'
    ]
  },
  {
    id: 'per',
    title: 'PER',
    value: '12배',
    status: 'positive',
    shortDescription: '적정 밸류에이션',
    detailedDescription: 'PER(주가수익비율)이 12배로 업종 평균 대비 적정 수준입니다. 저평가도 고평가도 아닌 안정적인 구간입니다.',
    interpretationPoints: [
      'PER 낮을수록 저평가 가능성',
      '업종 평균 PER과 비교 필요',
      '성장성 고려한 PER 분석 필요'
    ]
  },
  {
    id: 'pbr',
    title: 'PBR',
    value: '1.2배',
    status: 'positive',
    shortDescription: '저평가 구간',
    detailedDescription: 'PBR(주가순자산비율)이 1.2배로 저평가 구간에 있습니다. 장부가치 대비 매력적인 가격대입니다.',
    interpretationPoints: [
      'PBR 1배 이하면 저평가',
      'PBR 낮다고 무조건 좋은 것은 아님',
      '자산 질과 함께 평가 필요'
    ]
  },
  {
    id: 'dividend_yield',
    title: '배당수익률',
    value: '3.5%',
    status: 'positive',
    shortDescription: '안정적 배당 수익',
    detailedDescription: '배당수익률이 3.5%로 시장 금리 대비 매력적입니다. 안정적인 배당 수익이 기대됩니다.',
    interpretationPoints: [
      '배당수익률 3% 이상이면 양호',
      '배당 지속성 확인 필요',
      '배당성향과 함께 분석'
    ]
  },
  {
    id: 'operating_margin',
    title: '영업이익률',
    value: '12%',
    status: 'positive',
    shortDescription: '수익성 우수',
    detailedDescription: '영업이익률이 12%로 양호한 수익성을 보이고 있습니다. 안정적인 영업 구조를 갖추고 있습니다.',
    interpretationPoints: [
      '영업이익률 10% 이상이면 우수',
      '영업이익률 상승은 경쟁력 강화',
      '업종 평균과 비교 필요'
    ]
  },
  {
    id: 'current_ratio',
    title: '유동비율',
    value: '180%',
    status: 'positive',
    shortDescription: '단기 재무 안정성',
    detailedDescription: '유동비율이 180%로 단기 부채 상환 능력이 우수합니다. 재무적 안정성이 높습니다.',
    interpretationPoints: [
      '유동비율 150% 이상이면 안정적',
      '유동비율 너무 높으면 자산 활용 미흡',
      '업종 특성 고려 필요'
    ]
  },
  {
    id: 'eps_growth',
    title: 'EPS 성장률',
    value: '8%',
    status: 'positive',
    shortDescription: '꾸준한 이익 성장',
    detailedDescription: '주당순이익(EPS)이 전년 대비 8% 성장하며 꾸준한 이익 성장세를 보이고 있습니다.',
    interpretationPoints: [
      'EPS 지속 성장이 중요',
      'EPS 성장률 높을수록 좋음',
      '일회성 요인 제외한 분석 필요'
    ]
  }
];

export function getIndicatorsByStyle(style: InvestmentStyle): IndicatorInfo[] {
  switch (style) {
    case '공격형':
      return aggressiveIndicators;
    case '중간형':
      return moderateIndicators;
    case '안정형':
      return conservativeIndicators;
    default:
      return aggressiveIndicators;
  }
}
