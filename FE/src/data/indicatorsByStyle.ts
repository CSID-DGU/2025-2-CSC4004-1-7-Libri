import { InvestmentStyle } from "../contexts/InvestmentStyleContext";

export interface IndicatorInfo {
    id: string;
    title: string;
    value: string;
    status: "positive" | "negative" | "neutral";
    shortDescription: string;
    detailedDescription: string;
    interpretationPoints: string[];
}

export interface IndicatorDataset {
    top3: IndicatorInfo[];
    analysis: IndicatorInfo[];
}

// 공격형 지표
const aggressiveAnalysisIndicators: IndicatorInfo[] = [
    {
        id: "ema12",
        title: "EMA 12",
        value: "",
        status: "positive",
        shortDescription:
            "최근 12일간의 주가 평균을 계산하되, 최근 가격에 더 큰 비중을 두는 이동평균선입니다. 주가의 단기적인 흐름을 빠르게 파악하는 데 사용됩니다.",
        detailedDescription: "",
        interpretationPoints: [
            "주가가 EMA12 위에 있으면 단기 상승 흐름으로 볼 수 있습니다.",
            "EMA12가 상승 중이면 단기 매수세가 강하다고 해석합니다.",
            "EMA12가 급격히 꺾이면 단기 하락 가능성을 의심해볼 수 있습니다.",
        ],
    },
    {
        id: "ema26",
        title: "EMA 26",
        value: "",
        status: "positive",
        shortDescription:
            "최근 26일간의 평균 주가를 기반으로 한 지수이동평균선으로, EMA12보다 느리게 움직이며 중기 흐름을 보여줍니다.",
        detailedDescription: "",
        interpretationPoints: [
            "주가가 EMA26 위에 있으면 비교적 안정적인 상승 흐름입니다.",
            "EMA26이 우상향하면 중기적으로 긍정적인 흐름입니다.",
            "EMA26 아래로 내려가면 추세 약화를 의심할 수 있습니다.",
        ],
    },
    {
        id: "macd",
        title: "MACD",
        value: "",
        status: "neutral",
        shortDescription:
            "EMA12와 EMA26의 차이를 통해, 주가가 최근보다 더 빠르게 오르고 있는지 아니면 힘이 약해지고 있는지를 보여줍니다. 주가 상승, 하락 속도가 빨라지는지 느려지는지를 확인할 수 있는 지표입니다.",
        detailedDescription: "",
        interpretationPoints: [
            "MACD가 상승 중이면 주가가 점점 더 빠르게 오르고 있다는 의미입니다.",
            "MACD가 하락 중이면 상승 힘이 줄거나 하락 속도가 커지고 있음을 뜻합니다.",
            "EMA12가 EMA26 위로 올라가면 상승 흐름이 우세하다고 볼 수 있습니다.",
            "EMA12가 EMA26 아래로 내려가면 하락 흐름이 강해졌다고 해석합니다.",
        ],
    },
    {
        id: "volume",
        title: "거래량",
        value: "",
        status: "positive",
        shortDescription:
            "특정 기간 동안 얼마나 많은 주식이 거래되었는지를 나타내는 지표입니다. 가격 변화가 얼마나 많은 사람의 참여로 이루어졌는지를 알려줍니다.",
        detailedDescription: "",
        interpretationPoints: [
            "가격 상승과 함께 거래량이 증가하면 신뢰도 높은 상승입니다.",
            "가격만 오르고 거래량이 줄면 힘 없는 상승일 수 있습니다.",
            "거래량 급증은 큰 변동이 시작될 신호일 수 있습니다.",
        ],
    },
    {
        id: "kospi",
        title: "KOSPI",
        value: "",
        status: "neutral",
        shortDescription:
            "한국 전체 주식시장의 평균적인 흐름을 보여주는 지수입니다. 개별 종목이 아닌 시장 전체의 분위기를 파악하는 데 사용됩니다.",
        detailedDescription: "",
        interpretationPoints: [
            "KOSPI가 상승하면 시장 전반의 분위기가 좋습니다.",
            "KOSPI 하락 시 개별 종목도 영향을 받을 수 있습니다.",
            "시장 흐름과 반대로 움직이는 종목은 주의가 필요합니다.",
        ],
    },
    {
        id: "sma20",
        title: "SMA20",
        value: "",
        status: "positive",
        shortDescription:
            "최근 20일간의 종가를 단순 평균한 값으로, 현재 주가의 중기적인 흐름을 확인하는 데 사용됩니다.",
        detailedDescription: "",
        interpretationPoints: [
            "주가가 SMA20 위에 있으면 비교적 안정적인 상태입니다.",
            "SMA20이 상승하면 추세가 긍정적입니다.",
            "SMA20 아래에 있으면 상승 흐름이 약해졌을 수 있으므로, 섣불리 매수하지 않고 관망하는 것이 좋습니다.",
        ],
    },
    {
        id: "rsi",
        title: "RSI",
        value: "",
        status: "neutral",
        shortDescription:
            "주가가 얼마나 많이 올랐는지 또는 내렸는지를 수치로 나타내는 지표로, 과매수나 과매도 상태를 판단하는 데 사용됩니다.",
        detailedDescription: "",
        interpretationPoints: [
            "RSI가 70 이상이면 과하게 오른 상태로 볼 수 있습니다.",
            "RSI가 30 이하이면 과하게 떨어진 상태로 볼 수 있습니다.",
            "RSI가 중간에서 상승하면 상승 가능성이 남아 있을 수 있습니다.",
        ],
    },
    {
        id: "stoch_k",
        title: "스토캐스틱 %K",
        value: "",
        status: "neutral",
        shortDescription:
            "현재 주가가 최근 가격 범위에서 어느 위치에 있는지를 보여주는 지표로, 단기적인 타이밍 판단에 주로 사용됩니다.",
        detailedDescription: "",
        interpretationPoints: [
            "%K가 80 이상이면 단기 과열 상태입니다.",
            "%K가 20 이하이면 단기 과매도 상태입니다.",
            "%K가 올라가기 시작하면 반등 신호로 볼 수 있습니다.",
        ],
    },
    {
        id: "vix",
        title: "VIX",
        value: "",
        status: "neutral",
        shortDescription:
            "시장이 얼마나 불안한지를 나타내는 지표로, 숫자가 높을수록 투자자들의 불안 심리가 크다는 의미입니다. 시장이 얼마나 불안한 상태인지를 판단하고, 매수에 신중해야 할 시점을 가늠할 수 있습니다.",
        detailedDescription: "",
        interpretationPoints: [
            "VIX가 높으면 시장 변동성이 커질 수 있습니다.",
            "VIX 급등은 하락 가능성이 커졌다는 신호입니다.",
            "VIX가 낮아지면 시장이 안정되고 있다고 봅니다.",
        ],
    },
    {
        id: "bollinger_band_b",
        title: "Bollinger Band_B",
        value: "",
        status: "neutral",
        shortDescription:
            "현재 주가가 ‘평소 가격 범위’에서 상단에 가까운지, 하단에 가까운지를 알려주는 지표입니다. 지금 가격이 많이 오른 상태인지, 충분히 눌린 상태인지를 판단하는 데 사용됩니다.",
        detailedDescription: "",
        interpretationPoints: [
            "%B가 1에 가까우면 밴드 상단에 위치합니다.",
            "%B가 0에 가까우면 하단에 위치합니다.",
            "상단 근처에서는 조정을, 하단 근처에서는 반등을 생각할 수 있습니다.",
        ],
    },
    {
        id: "bb_bw",
        title: "BB_BW",
        value: "",
        status: "neutral",
        shortDescription:
            "상단과 하단 밴드 사이의 간격을 나타내는 지표입니다. 현재 주가 변동이 큰지 또는 비교적 안정적인지를 판단하는 데 사용됩니다.",
        detailedDescription: "",
        interpretationPoints: [
            "밴드 폭이 넓으면 가격이 이미 크게 흔들린 상태일 수 있습니다.",
            "밴드 폭이 좁으면 이후 변동성이 커질 가능성을 염두에 둡니다.",
            "밴드 폭이 갑자기 확장되면 주가가 방향성을 가지고 움직이기 시작하는 신호일 수 있습니다.",
        ],
    },
    {
        id: "atr",
        title: "ATR",
        value: "",
        status: "neutral",
        shortDescription:
            "하루 동안 주가가 얼마나 크게 움직였는지를 평균으로 나타낸 지표입니다. 변동성 크기를 판단하는 데 사용됩니다.",
        detailedDescription: "",
        interpretationPoints: [
            "ATR이 높으면 가격 변동이 큽니다.",
            "ATR이 낮으면 비교적 안정적인 상태입니다.",
            "ATR이 급증하면 시장이 불안해졌다는 신호입니다.",
        ],
    },
    {
        id: "position",
        title: "Position",
        value: "둔화",
        status: "negative",
        shortDescription: "모멘텀이 둔화되며 상승 추세의 에너지가 약화되고 있습니다.",
        detailedDescription:
            "Position은 가격의 위치와 모멘텀을 종합적으로 나타내는 지표입니다. 추세의 강도와 지속 가능성을 판단하는데 유용합니다.",
        interpretationPoints: [
            "Position 상승은 추세 가속화",
            "Position 둔화는 추세 약화 신호",
            "Position 전환은 추세 반전 가능성",
        ],
    },
];

// 중간형 지표 (현재 미사용 데이터)
const moderateAnalysisIndicators: IndicatorInfo[] = [
    {
        id: "volume",
        title: "거래량",
        value: "증가",
        status: "positive",
        shortDescription: "거래량이 평균 대비 증가하며 추세에 대한 시장 참여도가 높습니다.",
        detailedDescription:
            "거래량은 특정 기간 동안 거래된 주식의 수량을 나타냅니다. 가격 변동과 함께 분석하면 추세의 신뢰도를 확인할 수 있어요.",
        interpretationPoints: [
            "상승과 함께 거래량 증가는 강한 상승 신호",
            "하락과 함께 거래량 증가는 강한 하락 신호",
            "거래량 없는 가격 변동은 신뢰도가 낮음",
        ],
    },
    {
        id: "rsi",
        title: "RSI",
        value: "72",
        status: "neutral",
        shortDescription: "RSI가 과매수 구간(70 이상)에 진입하여 단기 조정 가능성이 있습니다.",
        detailedDescription:
            "RSI(상대강도지수)는 가격의 상승과 하락 강도를 비교하여 과매수/과매도 상태를 판단하는 지표입니다. 0~100 사이의 값을 가져요.",
        interpretationPoints: [
            "RSI 70 이상은 과매수 구간, 조정 가능성",
            "RSI 30 이하는 과매도 구간, 반등 가능성",
            "50을 기준으로 상승/하락 추세 판단",
        ],
    },
    {
        id: "stoch_k",
        title: "Stoch_K",
        value: "78",
        status: "neutral",
        shortDescription: "스토캐스틱이 과매수 구간(80 이상)에 머물며 하락 반전 가능성이 있습니다.",
        detailedDescription:
            "스토캐스틱은 일정 기간 동안의 가격 변동 폭 중 현재 가격의 위치를 백분율로 나타낸 지표입니다. 과매수/과매도를 빠르게 포착해요.",
        interpretationPoints: [
            "%K가 80 이상에서 하락 전환하면 매도 신호",
            "%K가 20 이하에서 상승 전환하면 매수 신호",
            "%K와 %D의 교차로 매매 타이밍 포착",
        ],
    },
    {
        id: "stoch_d",
        title: "Stoch_D",
        value: "75",
        status: "neutral",
        shortDescription: "스토캐스틱이 과매수 구간(80 이상)에 머물며 하락 반전 가능성이 있습니다.",
        detailedDescription:
            "Stoch_D는 Stoch_K의 이동평균으로, 보다 완만한 신호를 제공합니다. %K와 %D의 교차로 매매 타이밍을 포착할 수 있습니다.",
        interpretationPoints: [
            "%D가 %K보다 위에 있으면 하락 압력",
            "%D가 %K보다 아래 있으면 상승 압력",
            "두 선의 교차점에서 매매 신호 발생",
        ],
    },
    {
        id: "atr",
        title: "ATR",
        value: "상승",
        status: "neutral",
        shortDescription: "ATR이 상승하며 가격 변동성이 확대되고 있습니다.",
        detailedDescription:
            "ATR(Average True Range)은 가격 변동성을 측정하는 지표입니다. 값이 클수록 변동성이 크다는 것을 의미합니다.",
        interpretationPoints: [
            "ATR 상승은 변동성 증가 신호",
            "ATR 하락은 변동성 감소, 횡보 가능",
            "높은 ATR에서는 손절매 폭 확대 필요",
        ],
    },
    {
        id: "bollinger_band_b",
        title: "Bollinger Band_B",
        value: "수축",
        status: "neutral",
        shortDescription:
            "볼린저 밴드가 수축하며 변동성이 낮은 구간에 진입했습니다. 추후 급등락 가능성에 유의해야 합니다.",
        detailedDescription:
            "볼린저 밴드는 주가의 변동성을 나타내는 지표입니다. 밴드가 수축하면 변동성이 낮고, 확장하면 변동성이 높은 상태입니다.",
        interpretationPoints: [
            "밴드 상단 돌파 시 상승 추세 강화",
            "밴드 하단 이탈 시 하락 추세 강화",
            "밴드 수축 후 확장은 큰 변동 신호",
        ],
    },
    {
        id: "sma20",
        title: "SMA20",
        value: "상승",
        status: "positive",
        shortDescription:
            "현재 주가가 장기 이동평균선을 상회하며 중기적 상승 추세를 유지하고 있어요.",
        detailedDescription:
            "SMA(단순이동평균선)는 일정 기간 동안의 종가를 산술 평균한 값입니다. 20일 평균은 중기 추세를 나타내요.",
        interpretationPoints: [
            "주가가 SMA20 위에 있으면 상승 추세",
            "주가가 SMA20 아래로 떨어지면 하락 신호",
            "장기 투자 시 중요한 지지/저항선으로 활용",
        ],
    },
    {
        id: "macd",
        title: "MACD",
        value: "하향 돌파",
        status: "negative",
        shortDescription: "MACD가 시그널선을 하향 돌파하며 매도 신호가 강화되고 있습니다.",
        detailedDescription:
            "MACD(이동평균수렴확산)는 단기와 장기 이동평균선의 차이를 이용한 추세 추종 지표입니다. 추세의 방향과 강도를 동시에 파악할 수 있어요.",
        interpretationPoints: [
            "MACD선이 시그널선을 상향 돌파하면 매수 신호",
            "MACD선이 시그널선을 하향 돌파하면 매도 신호",
            "0선 위에 있으면 상승 추세, 아래면 하락 추세",
        ],
    },
    {
        id: "vix",
        title: "VIX",
        value: "상승",
        status: "negative",
        shortDescription: "거래량이 평균 대비 증가하며 추세에 대한 시장 참여도가 높습니다.",
        detailedDescription:
            "VIX(변동성 지수)는 시장의 불확실성과 공포 수준을 나타냅니다. 수치가 높을수록 시장 불안이 크다는 의미입니다.",
        interpretationPoints: [
            "VIX 20 이상은 시장 불안이 높은 상태",
            "VIX 하락은 시장 안정화 신호",
            "급격한 VIX 상승은 조정 국면 진입 신호",
        ],
    },
    {
        id: "v_kospi",
        title: "V-KOSPI",
        value: "상승",
        status: "negative",
        shortDescription:
            "V-KOSPI가 상승하며 시장 불확실성이 커지고 있습니다. 보수적인 접근이 필요합니다.",
        detailedDescription:
            "V-KOSPI는 한국 시장의 변동성 지수로, 투자자들의 불안 심리를 반영합니다. 높을수록 시장 불확실성이 크다는 신호입니다.",
        interpretationPoints: [
            "V-KOSPI 25 이상은 높은 변동성 구간",
            "V-KOSPI 하락은 시장 안정 신호",
            "급격한 상승은 시장 패닉 가능성",
        ],
    },
    {
        id: "roa",
        title: "ROA",
        value: "양호",
        status: "positive",
        shortDescription: "단기 흐름이 장기 흐름보다 강해지며, 최근 주가가 상승세를 타고 있습니다.",
        detailedDescription:
            "ROA(총자산이익률)는 기업이 보유한 자산을 얼마나 효율적으로 활용하여 이익을 창출하는지 나타내는 지표입니다.",
        interpretationPoints: [
            "ROA 5% 이상이면 양호한 수준",
            "ROA 상승은 자산 효율성 개선",
            "업종 평균 대비 ROA 비교 필요",
        ],
    },
    {
        id: "debt_ratio",
        title: "DebtRatio",
        value: "양호",
        status: "positive",
        shortDescription:
            "시장 지수 대비 상대적으로 강세를 보이며, 시장 평균보다 높은 상승 탄력을 유지하고 있습니다.",
        detailedDescription:
            "부채비율은 기업의 재무 건전성을 나타내는 지표로, 낮을수록 재무구조가 안정적입니다.",
        interpretationPoints: [
            "부채비율 100% 이하면 건전",
            "부채비율 상승은 재무 위험 증가",
            "업종 특성 고려한 분석 필요",
        ],
    },
];

// 안정형 지표
const conservativeAnalysisIndicators: IndicatorInfo[] = [
    {
        id: "close",
        title: "종가",
        value: "",
        status: "neutral",
        shortDescription:
            "종가는 하루 거래가 모두 끝난 뒤의 마지막 가격으로, 그날 시장 참여자들의 판단이 가장 종합적으로 반영된 가격입니다.",
        detailedDescription: "",
        interpretationPoints: [
            "종가는 하루 동안의 가격 변화를 종합한 결과로, 시장의 최종 판단 가격으로 봅니다.",
            "이동평균선, RSI, MACD 등 대부분의 지표는 종가를 기준으로 계산됩니다.",
            "종가 흐름이 안정적이면 추세가 유지되고 있다고 해석합니다.",
        ],
    },
    {
        id: "high",
        title: "고가",
        value: "",
        status: "neutral",
        shortDescription:
            "하루 동안 주가가 도달한 가장 높은 가격을 의미하며, 매수세가 가장 강했던 지점을 보여줍니다.",
        detailedDescription: "",
        interpretationPoints: [
            "고가가 높아지면 상승 시도가 강했음을 의미합니다.",
            "고가 돌파 여부는 상승 지속 가능성 판단에 사용됩니다.",
            "고가·저가 범위가 크고 거래량이 많으면 중요한 움직임일 가능성이 높습니다.",
            "고가·저가 범위가 크지만 거래량이 적으면 일시적인 흔들림일 수 있습니다.",
            "고가 부근에서 종가가 형성되면 매수 압력이 더 컸다고 볼 수 있습니다.",
        ],
    },
    {
        id: "low",
        title: "저가",
        value: "",
        status: "neutral",
        shortDescription:
            "하루 동안 주가가 내려간 가장 낮은 가격으로, 매도 압력이 가장 강했던 지점을 나타냅니다.",
        detailedDescription: "",
        interpretationPoints: [
            "저가가 계속 낮아지면 하락 압력이 강하다고 봅니다.",
            "저가가 이전 수준에서 유지되면 하락이 멈추고 있을 가능성이 있습니다.",
            "고가·저가 범위가 크고 거래량이 많으면 중요한 움직임일 가능성이 높습니다.",
            "고가·저가 범위가 크지만 거래량이 적으면 일시적인 흔들림일 수 있습니다.",
            "저가 부근에서 종가가 형성되면 매도 압력이 더 컸다고 볼 수 있습니다.",
        ],
    },
    {
        id: "volume",
        title: "거래량",
        value: "",
        status: "neutral",
        shortDescription:
            "특정 기간 동안 얼마나 많은 주식이 거래되었는지를 나타내는 지표입니다. 가격 변화가 얼마나 많은 사람의 참여로 이루어졌는지를 알려줍니다.",
        detailedDescription: "",
        interpretationPoints: [
            "가격 상승과 함께 거래량이 증가하면 신뢰도 높은 상승입니다.",
            "가격만 오르고 거래량이 줄면 힘 없는 상승일 수 있습니다.",
            "거래량 급증은 큰 변동이 시작될 신호일 수 있습니다.",
        ],
    },
    {
        id: "rsi",
        title: "RSI",
        value: "",
        status: "neutral",
        shortDescription:
            "주가가 얼마나 많이 올랐는지 또는 내렸는지를 수치로 나타내는 지표로, 과매수나 과매도 상태를 판단하는 데 사용됩니다.",
        detailedDescription: "",
        interpretationPoints: [
            "RSI가 70 이상이면 과하게 오른 상태로 볼 수 있습니다.",
            "RSI가 30 이하이면 과하게 떨어진 상태로 볼 수 있습니다.",
            "RSI가 중간에서 상승하면 상승 가능성이 남아 있을 수 있습니다.",
        ],
    },
    {
        id: "stoch_k",
        title: "스토캐스틱 %K",
        value: "",
        status: "neutral",
        shortDescription:
            "현재 주가가 최근 가격 범위에서 어느 위치에 있는지를 보여주는 지표로, 단기적인 타이밍 판단에 주로 사용됩니다.",
        detailedDescription: "",
        interpretationPoints: [
            "%K가 80 이상이면 단기 과열 상태입니다.",
            "%K가 20 이하이면 단기 과매도 상태입니다.",
            "%K가 올라가기 시작하면 반등 신호로 볼 수 있습니다.",
        ],
    },
    {
        id: "stoch_d",
        title: "스토캐스틱 %D",
        value: "",
        status: "neutral",
        shortDescription:
            "Stoch %K를 부드럽게 만든 평균선으로, 단기 신호의 신뢰도를 높이기 위해 사용됩니다.",
        detailedDescription: "",
        interpretationPoints: [
            "%K와 %D 교차는 타이밍 판단에 활용됩니다.",
            "%D가 위로 향하면 흐름이 안정되고 있음을 의미합니다.",
            "%D 하락은 단기 약세 신호로 볼 수 있습니다.",
        ],
    },
    {
        id: "atr",
        title: "ATR",
        value: "",
        status: "neutral",
        shortDescription:
            "하루 동안 주가가 얼마나 크게 움직였는지를 평균으로 나타낸 지표입니다. 변동성 크기를 판단하는 데 사용됩니다.",
        detailedDescription: "",
        interpretationPoints: [
            "ATR이 높으면 가격 변동이 큽니다.",
            "ATR이 낮으면 비교적 안정적인 상태입니다.",
            "ATR이 급증하면 시장이 불안해졌다는 신호입니다.",
        ],
    },
    {
        id: "bollinger_band_b",
        title: "볼린저 밴드 %B",
        value: "",
        status: "neutral",
        shortDescription:
            "현재 주가가 ‘평소 가격 범위’에서 상단에 가까운지, 하단에 가까운지를 알려주는 지표입니다.",
        detailedDescription: "",
        interpretationPoints: [
            "%B가 1에 가까우면 밴드 상단에 위치합니다.",
            "%B가 0에 가까우면 하단에 위치합니다.",
            "상단 근처에서는 조정을, 하단 근처에서는 반등을 생각할 수 있습니다.",
        ],
    },
    {
        id: "sma20",
        title: "SMA20",
        value: "",
        status: "neutral",
        shortDescription:
            "최근 20일간의 종가를 단순 평균한 값으로, 현재 주가의 중기적인 흐름을 확인하는 데 사용됩니다.",
        detailedDescription: "",
        interpretationPoints: [
            "주가가 SMA20 위에 있으면 비교적 안정적인 상태입니다.",
            "SMA20이 상승하면 추세가 긍정적입니다.",
            "SMA20 아래에 있으면 상승 흐름이 약해졌을 수 있으므로 관망이 필요합니다.",
        ],
    },
    {
        id: "macd",
        title: "MACD",
        value: "",
        status: "neutral",
        shortDescription:
            "EMA12와 EMA26의 차이를 통해, 주가 상승·하락 속도가 어떻게 변하는지 보여주는 지표입니다.",
        detailedDescription: "",
        interpretationPoints: [
            "MACD가 상승 중이면 주가가 점점 더 빠르게 오르고 있다는 의미입니다.",
            "MACD가 하락 중이면 상승 힘이 줄거나 하락 속도가 커지고 있음을 뜻합니다.",
            "EMA12가 EMA26 위로 올라가면 상승 흐름이 우세하다고 볼 수 있습니다.",
            "EMA12가 EMA26 아래로 내려가면 하락 흐름이 강해졌다고 해석합니다.",
        ],
    },
    {
        id: "macd_signal",
        title: "MACD_Signal",
        value: "",
        status: "neutral",
        shortDescription:
            "MACD를 부드럽게 만든 평균선으로, MACD 해석을 보조해 매수 및 매도 타이밍을 확인하는 데 사용됩니다.",
        detailedDescription: "",
        interpretationPoints: [
            "MACD가 시그널선 위로 올라가면 긍정적인 신호입니다.",
            "MACD가 시그널선 아래로 내려가면 흐름 약화 신호로 볼 수 있습니다.",
            "시그널선 교차는 다른 지표와 함께 확인해 진짜 전환인지 판단합니다.",
        ],
    },
    {
        id: "vix",
        title: "VIX",
        value: "",
        status: "neutral",
        shortDescription:
            "시장 불안도를 나타내는 지표로, 숫자가 높을수록 투자자들의 불안 심리가 크다는 의미입니다.",
        detailedDescription: "",
        interpretationPoints: [
            "VIX가 높으면 시장 변동성이 커질 수 있습니다.",
            "VIX 급등은 하락 가능성이 커졌다는 신호입니다.",
            "VIX가 낮아지면 시장이 안정되고 있다고 봅니다.",
        ],
    },
    {
        id: "roa",
        title: "ROA",
        value: "",
        status: "positive",
        shortDescription:
            "회사가 가진 자산으로 얼마나 효율적으로 이익을 내고 있는지를 보여주는 지표입니다.",
        detailedDescription: "",
        interpretationPoints: [
            "ROA가 높을수록 수익 구조가 효율적입니다.",
            "ROA가 낮으면 이익 창출력이 떨어질 수 있습니다.",
            "장기적인 관점에서 기업 신뢰도를 판단하는 데 활용합니다.",
        ],
    },
    {
        id: "debt_ratio",
        title: "부채 비율",
        value: "",
        status: "neutral",
        shortDescription:
            "기업이 보유한 자산 대비 부채가 얼마나 되는지를 나타내며 재무 안정성을 평가합니다.",
        detailedDescription: "",
        interpretationPoints: [
            "부채비율이 높으면 재무 부담이 큽니다.",
            "부채비율이 낮으면 비교적 안정적인 기업입니다.",
            "급격한 상승은 주의 신호로 봅니다.",
        ],
    },
    {
        id: "analyst_opinion",
        title: "애널리스트 투자의견",
        value: "",
        status: "neutral",
        shortDescription:
            "증권사 애널리스트들이 제시한 투자 의견을 수치화한 값으로, 시장 전문가들의 평가를 반영합니다.",
        detailedDescription: "",
        interpretationPoints: [
            "긍정적인 의견이 많을수록 기대감이 큽니다.",
            "의견 변화는 주가 변동의 계기가 될 수 있습니다.",
            "참고 지표로 활용하고 맹신하지는 않습니다.",
        ],
    },
];

export const aggressiveIndicatorData: IndicatorDataset = {
    top3: aggressiveAnalysisIndicators.slice(0, 3),
    analysis: aggressiveAnalysisIndicators,
};

export const conservativeIndicatorData: IndicatorDataset = {
    top3: conservativeAnalysisIndicators.slice(0, 3),
    analysis: conservativeAnalysisIndicators,
};

export const INDICATOR_DATA_BY_STYLE: Record<InvestmentStyle, IndicatorDataset> = {
    공격형: aggressiveIndicatorData,
    안정형: conservativeIndicatorData,
};

export function getIndicatorsByStyle(style: InvestmentStyle): IndicatorDataset {
    return INDICATOR_DATA_BY_STYLE[style] ?? aggressiveIndicatorData;
}
