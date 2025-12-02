import { useEffect, useMemo, useRef, useState, type ComponentType, type SVGProps } from "react";
import Header from "@/components/layout/Header";
import CaretLeftIcon from "@/assets/icons/caret-left.svg?react";
import CaretDownIcon from "@/assets/icons/caret-down.svg?react";
import AiSparkIcon from "@/assets/icons/AI.svg?react";
import InfoIcon from "@/assets/icons/info.svg?react";
import CrownIcon from "@/assets/icons/crown.svg?react";
import { createChart } from "lightweight-charts";
import IndicatorModal from "./IndicatorModal";
import { getIndicatorsByStyle, type IndicatorInfo } from "../data/indicatorsByStyle";
import { type InvestmentStyle, useInvestmentStyle } from "../contexts/InvestmentStyleContext";
import { api } from "../api/client";

export type TabType = "top3" | "analysis" | "trading";

interface IndicatorGuideInfo {
    title: string;
    description: string;
    fullDescription: string;
    interpretationPoints: string[];
}

interface StockDetailProps {
    stockName: string;
    investmentStyle: InvestmentStyle;
    initialInvestment: number;
    onBack: () => void;
}

interface Trade {
    type: "buy" | "sell";
    quantity: number;
    pricePerShare: number;
    time: string;
    profit?: number;
    profitPercent?: number;
}

interface DayTrading {
    date: string;
    trades: Trade[];
}

type TradeAction = "buy" | "sell" | "hold";

interface PriceDay {
    label: string;
    high: number;
    low: number;
    close: number;
}

const DEFAULT_ACTION_SEQUENCE: TradeAction[] = ["buy", "sell", "hold", "buy", "sell"];

function formatRelativeDayLabel(offset: number) {
    if (offset === 0) return "오늘";
    if (offset === 1) return "어제";
    const date = new Date();
    date.setDate(date.getDate() - offset);
    const month = date.getMonth() + 1;
    const day = date.getDate();
    return `${month}월 ${day}일`;
}

function generateMockPriceSeries(days = 5, basePrice = 70000): PriceDay[] {
    const series: PriceDay[] = [];
    let priceCursor = basePrice;
    for (let i = 0; i < days; i++) {
        const label = formatRelativeDayLabel(i);
        const dailyDrift = (Math.random() - 0.5) * 2000;
        priceCursor = Math.max(45000, priceCursor + dailyDrift);
        const low = Math.max(42000, Math.round(priceCursor - (Math.random() * 1500 + 500)));
        const high = Math.round(priceCursor + (Math.random() * 1800 + 600));
        const close = Math.round((high + low) / 2);
        series.push({ label, high, low, close });
    }
    return series;
}

function simulateTradingHistory(
    initialInvestment: number,
    priceSeries: PriceDay[],
    actions: TradeAction[],
): DayTrading[] {
    let cash = initialInvestment;
    let holdings = 0;
    let totalCost = 0;

    return priceSeries.map((day, index) => {
        const action = actions[index] ?? "hold";
        const trades: Trade[] = [];

        if (action === "buy") {
            const maxAffordable = Math.min(10, Math.floor(cash / day.low));
            if (maxAffordable > 0) {
                const cost = maxAffordable * day.low;
                cash -= cost;
                holdings += maxAffordable;
                totalCost += cost;
                trades.push({
                    type: "buy",
                    quantity: maxAffordable,
                    pricePerShare: day.low,
                    time: "10:05",
                });
            }
        } else if (action === "sell") {
            const sellQuantity = Math.min(10, holdings);
            if (sellQuantity > 0) {
                const averageCostPerShare = holdings > 0 ? totalCost / holdings : 0;
                const costBasis = averageCostPerShare * sellQuantity;
                const revenue = sellQuantity * day.high;
                const profit = revenue - costBasis;
                const profitPercent =
                    averageCostPerShare > 0
                        ? ((day.high - averageCostPerShare) / averageCostPerShare) * 100
                        : 0;

                cash += revenue;
                holdings -= sellQuantity;
                totalCost -= costBasis;

                trades.push({
                    type: "sell",
                    quantity: sellQuantity,
                    pricePerShare: day.high,
                    time: "14:25",
                    profit: Math.round(profit),
                    profitPercent: parseFloat(profitPercent.toFixed(1)),
                });
            }
        }

        return {
            date: day.label,
            trades,
        };
    });
}

function SparklineChart() {
    const chartContainerRef = useRef<HTMLDivElement>(null);
    const chartInstanceRef = useRef<ReturnType<typeof createChart> | null>(null);

    useEffect(() => {
        const container = chartContainerRef.current;
        if (!container) return;

        const generateMockData = () => {
            const data = [];
            const basePrice = 60000;
            const now = new Date();

            for (let i = 30; i >= 0; i--) {
                const date = new Date(now);
                date.setDate(date.getDate() - i);
                const randomChange = (Math.random() - 0.5) * 3000;
                const price = basePrice + randomChange + (30 - i) * 100;
                data.push({ time: Math.floor(date.getTime() / 1000) as any, value: price });
            }
            return data;
        };

        const chart = createChart(container, {
            layout: { background: { color: "transparent" }, textColor: "#1FA9A4" },
            grid: { vertLines: { visible: false }, horzLines: { visible: false } },
            width: container.clientWidth,
            height: 48,
            timeScale: { visible: false, borderVisible: false, fixLeftEdge: true, fixRightEdge: true },
            rightPriceScale: { visible: false, borderVisible: false },
            leftPriceScale: { visible: false, borderVisible: false },
            crosshair: { mode: 0 },
            handleScale: false,
            handleScroll: false,
        });
        chartInstanceRef.current = chart;

        const series = chart.addAreaSeries({
            lineColor: "#1FA9A4",
            lineWidth: 2,
            topColor: "rgba(31,169,164,0.16)",
            bottomColor: "rgba(31,169,164,0)",
            priceLineVisible: false,
            lastValueVisible: false,
            crosshairMarkerVisible: false,
        });

        series.setData(generateMockData());
        chart.timeScale().fitContent();

        const resizeObserver = new ResizeObserver((entries) => {
            const entry = entries[0];
            if (!entry || !chartInstanceRef.current) return;
            const nextWidth = Math.floor(entry.contentRect.width);
            if (nextWidth > 0) {
                chartInstanceRef.current.applyOptions({ width: nextWidth });
            }
        });

        resizeObserver.observe(container);
        return () => {
            resizeObserver.disconnect();
            chart.remove();
            chartInstanceRef.current = null;
        };
    }, []);

    return <div ref={chartContainerRef} className="h-12 w-full" />;
}

function RecommendationCard({
    recommendation,
    aiExplanation,
    loading,
    error,
}: {
    recommendation: string;
    aiExplanation: string;
    loading: boolean;
    error: string | null;
}) {
    return (
        <div className="w-full" style={{ paddingInline: "20px" }}>
            <section
                className="rounded-[16px] bg-[#f2f4f8] flex flex-col"
                style={{ padding: "20px", gap: "20px" }}
            >
                <div className="flex flex-col gap-1">
                    <p className="label-2 text-[#6b6e74] tracking-[0.2px]">오늘의 추천 행동</p>
                    <p className="text-[36px] tracking-[1.2px] text-[#1fa9a4]" style={{ fontWeight: 700 }}>
                        {recommendation}
                    </p>
                </div>
                <SparklineChart />
                <div className="h-[0.5px] w-full" style={{ backgroundColor: "var(--achromatic-200)" }} />
                <div className="flex flex-col gap-[4px] text-[#151b26]">
                    <div className="flex items-center gap-[4px]">
                        <AiSparkIcon className="h-[20px] w-[20px]" />
                        <span className="title-3 tracking-[0.2px]">AI 설명</span>
                    </div>
                    {loading ? (
                        <p className="body-2 text-[#6b6e74]">AI가 최신 데이터를 분석하고 있습니다...</p>
                    ) : error ? (
                        <p className="body-2 text-[#f3646f]">{error}</p>
                    ) : (
                        <p className="body-2 text-[#151b26]">{aiExplanation}</p>
                    )}
                </div>
            </section>
        </div>
    );
}

const TAB_META: {
    id: TabType;
    label: string;
    icon?: ComponentType<SVGProps<SVGSVGElement>>;
}[] = [
    { id: "top3", label: "TOP3 분석" },
    { id: "analysis", label: "지표 분석" },
    { id: "trading", label: "AI 거래 내역", icon: AiSparkIcon },
];

function DetailTabs({ activeTab, onSelect }: { activeTab: TabType; onSelect: (tab: TabType) => void }) {
    return (
        <div className="flex w-full gap-2" role="tablist">
            {TAB_META.map((tab) => {
                const isActive = activeTab === tab.id;
                const Icon = tab.icon;
                return (
                    <button
                        key={tab.id}
                        type="button"
                        onClick={() => onSelect(tab.id)}
                        role="tab"
                        aria-selected={isActive}
                        className="flex-1 flex flex-col items-center px-2 py-3 text-center"
                        style={{ gap: "8px" }}
                    >
                        <span
                            className="title-3 flex items-center justify-center gap-1"
                            style={{ color: isActive ? "var(--achromatic-800)" : "var(--achromatic-500)" }}
                        >
                            {Icon ? (
                                <Icon
                                    className="h-[18px] w-[18px]"
                                    style={{ color: isActive ? "var(--achromatic-800)" : "var(--achromatic-500)" }}
                                />
                            ) : null}
                            {tab.label}
                        </span>
                        <div
                            className="h-[2px] w-full rounded-full"
                            style={{ backgroundColor: isActive ? "var(--achromatic-800)" : "var(--achromatic-200)" }}
                        />
                    </button>
                );
            })}
        </div>
    );
}

interface Top3IndicatorCardProps {
    indicator: IndicatorInfo;
    crownColor?: string;
}

function Top3IndicatorCard({ indicator, crownColor = "#f5c451" }: Top3IndicatorCardProps) {
    return (
        <div
            className="w-full rounded-[16px] bg-[#f2f4f8] text-left"
            style={{ padding: "16px 20px 20px" }}
        >
            <div className="flex items-center gap-[4px]">
                <CrownIcon className="h-4 w-4" style={{ color: crownColor }} aria-hidden />
                <span className="title-3 text-[#1fa9a4] tracking-[0.16px]">{indicator.title}</span>
            </div>
            <p className="body-2 leading-6 text-[#151b26]" style={{ marginTop: "8px" }}>
                {indicator.shortDescription}
            </p>
        </div>
    );
}

function AnalysisIndicatorCard({ indicator }: { indicator: IndicatorInfo }) {
    const [isOpen, setIsOpen] = useState(false);
    const toggleOpen = () => setIsOpen((prev) => !prev);

    return (
        <div
            className="w-full rounded-[16px] bg-[#f2f4f8] text-left"
            style={{ padding: "20px 20px 12px" }}
        >
            <span className="title-3 text-[#151b26] tracking-[0.16px]">{indicator.title}</span>
            <p className="body-2 text-[#414651]" style={{ marginTop: "8px" }}>
                {indicator.shortDescription}
            </p>
            {isOpen && (
                <div className="flex flex-col gap-[26px] text-sm text-[#4b4f59]" style={{ marginTop: "24px" }}>
                    <p className="title-4 text-[#444951]">💡 해석 포인트</p>
                    <ul className="flex list-disc flex-col body-2 gap-2" style={{ paddingLeft: "24px", paddingTop: "8px" }}>
                        {indicator.interpretationPoints.map((point, idx) => (
                            <li key={idx} className="leading-6">
                                {point}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
            <div
                className="flex flex-col items-center justify-center"
                style={{ marginTop: "16px", borderTop: "0.5px solid var(--achromatic-200)", paddingTop: "4px" }}
            >
                <button
                    type="button"
                    aria-expanded={isOpen}
                    onClick={toggleOpen}
                    className="flex items-center justify-center"
                    style={{ padding: "4px"}}
                >
                    <CaretDownIcon
                        className="h-[20px] w-[20px] transition-transform duration-200"
                        style={{
                            color: "var(--achromatic-500)",
                            transform: isOpen ? "rotate(180deg)" : "rotate(0deg)",
                        }}
                    />
                </button>
            </div>
        </div>
    );
}

function IndicatorSection({ investmentStyle }: { investmentStyle: InvestmentStyle }) {
    const indicatorData = getIndicatorsByStyle(investmentStyle);

    return (
        <section className="flex w-full flex-col gap-4" style={{ paddingInline: "20px" }}>
            <div className="flex flex-col" style={{ gap: "16px" }}>
                {indicatorData.analysis.map((indicator) => (
                    <AnalysisIndicatorCard key={indicator.id} indicator={indicator} />
                ))}
            </div>
        </section>
    );
}

function getTop3ReferenceLabel(now = new Date()) {
    const cutoffHour = 20;
    const cutoffMinute = 30;
    const afterCutoff =
        now.getHours() > cutoffHour ||
        (now.getHours() === cutoffHour && now.getMinutes() >= cutoffMinute);
    const referenceDate = new Date(now);
    if (!afterCutoff) {
        referenceDate.setDate(referenceDate.getDate() - 1);
    }
    const month = String(referenceDate.getMonth() + 1).padStart(2, "0");
    const day = String(referenceDate.getDate()).padStart(2, "0");
    return `${month}.${day}`;
}

function Top3AnalysisSection({
    investmentStyle,
    onIndicatorClick,
}: {
    investmentStyle: InvestmentStyle;
    onIndicatorClick: (indicator: IndicatorGuideInfo) => void;
}) {
    const indicatorData = getIndicatorsByStyle(investmentStyle);
    const indicators = indicatorData.top3;
    const rankColors = ["#FFD700", "#C0C0C0", "#CD7F32"];
    const referenceLabel = getTop3ReferenceLabel();
    const handleGuideClick = () => {
        onIndicatorClick({
            title: "AI 선정 기준",
            description: "TOP3 분석은 AI가 우선순위가 높은 지표를 선별해 구성합니다.",
            fullDescription:
                "AI는 최근 시장 변동성, 거래량, 추세 지표 등을 종합적으로 평가해 TOP3 분석 카드를 구성합니다. 각 지표는 현재 투자 전략에 미치는 영향도를 기준으로 선정되며, 변동성이 큰 경우 지표 구성이 달라질 수 있습니다.",
            interpretationPoints: [
                "시장 변동성, 추세, 수급 지표를 중심으로 선별됩니다.",
                "상황에 따라 TOP3에 포함되는 지표가 달라질 수 있습니다.",
                "각 지표 카드를 눌러 세부 해석을 확인해 주세요.",
            ],
        });
    };

    return (
        <section className="flex w-full flex-col gap-[8px]" style={{ paddingInline: "20px" }}>
            <div
                className="flex items-center justify-between body-3"
                style={{ color: "var(--achromatic-500)" }}
            >
                <span className="body-3">{referenceLabel} 20:30분 기준</span>
                <button
                    type="button"
                    className="flex items-center gap-[2px]"
                    onClick={handleGuideClick}
                >
                    <span>AI 선정 기준</span>
                    <InfoIcon className="h-[16px] w-[16px] text-[#b0b4bd]" aria-hidden />
                </button>
            </div>
            <div className="flex flex-col" style={{ gap: "16px" }}>
                {indicators.map((indicator, index) => {
                    const crownColor = rankColors[index] ?? rankColors[rankColors.length - 1];
                    return <Top3IndicatorCard key={indicator.id} indicator={indicator} crownColor={crownColor} />;
                })}
            </div>
        </section>
    );
}

function TradeMeta({ label }: { label: string }) {
    return <span className="text-[11px] text-[#9a9ea9] tracking-[0.2px]">{label}</span>;
}

function TradeItem({ trade }: { trade: Trade }) {
    const isSell = trade.type === "sell";
    const profitColor = trade.profit && trade.profit > 0 ? "text-[#f3646f]" : "text-[#5c87f2]";

    return (
        <div className="rounded-2xl bg-[#f8f9fb] p-4">
            <p className="text-base font-semibold text-[#151b26]">
                {trade.quantity}주 {isSell ? "판매" : "구매"}
            </p>
            {trade.profit !== undefined && trade.profitPercent !== undefined && (
                <p className={`mt-1 text-sm font-semibold ${profitColor}`}>
                    {trade.profit > 0 ? "+" : ""}
                    {trade.profit.toLocaleString()}원 ({trade.profitPercent > 0 ? "+" : ""}
                    {trade.profitPercent}%)
                </p>
            )}
            <div className="mt-2 flex items-center gap-1 text-[11px] text-[#9a9ea9]">
                <TradeMeta label={trade.time} />
                <span>·</span>
                <TradeMeta label="1주당" />
                <span>{trade.pricePerShare.toLocaleString()}원</span>
            </div>
        </div>
    );
}

function TradingHistorySection({
    onGuideClick,
    history,
}: {
    onGuideClick: (info: IndicatorGuideInfo) => void;
    history: DayTrading[];
}) {
    const referenceLabel = getTop3ReferenceLabel();
    return (
        <section className="flex w-full flex-col gap-4 pb-16" style={{ paddingInline: "20px" }}>
            <div className="flex items-center justify-between body-3" style={{ color: "var(--achromatic-500)" }}>
                <span className="body-3">{referenceLabel} 20:30분 기준</span>
                <button
                    type="button"
                    className="flex items-center gap-[2px]"
                    onClick={() =>
                        onGuideClick({
                            title: "AI 거래 내역 안내",
                            description: "AI 거래 내역은 실제 매매가 아닌 모델 기반 시뮬레이션입니다.",
                            fullDescription:
                                "리브리 모델이 추천 전략대로 거래했다면 어떤 수익을 기대할 수 있는지를 가정한 결과입니다. 실제 매매가 아니며, 사용자의 초기 투자금과 시장 데이터에 기반해 산출한 모의 성과입니다.",
                            interpretationPoints: [
                                "AI 거래 내역은 실제로 실행된 거래가 아닙니다.",
                                "사용자의 초기 투자금으로 리브리 추천을 따른 경우의 가상 수익입니다.",
                                "참고용 정보이며 매매 판단은 사용자 책임 하에 진행해야 합니다.",
                            ],
                        })
                    }
                >
                    <span>AI 거래 내역 안내</span>
                    <InfoIcon className="h-[16px] w-[16px] text-[#b0b4bd]" aria-hidden />
                </button>
            </div>
            <div className="flex flex-col gap-6">
                {history.length === 0 ? (
                    <p className="text-xs text-[#9a9ea9]">거래 내역이 없습니다.</p>
                ) : (
                    history.map((day) => (
                        <div key={day.date} className="flex flex-col gap-3">
                            <p
                                className="body-3"
                                style={{ color: "var(--achromatic-500)", marginTop: "16px", marginBottom: "8px" }}
                            >
                                {day.date}
                            </p>
                            {day.trades.length === 0 ? (
                                <p className="text-xs text-[#b0b4bd]">거래 내역 변화 없음</p>
                            ) : (
                                <div className="flex flex-col gap-3">
                                    {day.trades.map((trade, index) => (
                                        <TradeItem key={`${day.date}-${index}`} trade={trade} />
                                    ))}
                                </div>
                            )}
                        </div>
                    ))
                )}
            </div>
        </section>
    );
}

function StockDetailContent({
    stockName,
    onBack,
    recommendation,
    aiExplanation,
    activeTab,
    onTabChange,
    onIndicatorClick,
    investmentStyle,
    tradingHistory,
    loading,
    error,
}: {
    stockName: string;
    onBack: () => void;
    recommendation: string;
    aiExplanation: string;
    activeTab: TabType;
    onTabChange: (tab: TabType) => void;
    onIndicatorClick: (indicator: IndicatorGuideInfo) => void;
    investmentStyle: InvestmentStyle;
    tradingHistory: DayTrading[];
    loading: boolean;
    error: string | null;
}) {
    return (
        <div
            className="absolute content-stretch flex flex-col items-start left-1/2 top-[52px] translate-x-[-50%] w-full max-w-[375px] gap-4"
            style={{ paddingBottom: "52px" }}
        >
            <div className="w-full px-5" style={{ marginBottom: "16px" }}>
                <Header title={stockName} onBack={onBack} leftIcon={CaretLeftIcon} />
            </div>
            <div className="flex flex-col gap-6">
                <RecommendationCard
                    recommendation={recommendation}
                    aiExplanation={aiExplanation}
                    loading={loading}
                    error={error}
                />
                <div style={{ marginTop: "30px", paddingInline: "20px", marginBottom: "12px" }}>
                    <DetailTabs activeTab={activeTab} onSelect={onTabChange} />
                </div>
                {activeTab === "top3" && (
                    <Top3AnalysisSection
                        investmentStyle={investmentStyle}
                        onIndicatorClick={onIndicatorClick}
                    />
                )}
                {activeTab === "analysis" && <IndicatorSection investmentStyle={investmentStyle} />}
                {activeTab === "trading" && (
                    <TradingHistorySection
                        onGuideClick={onIndicatorClick}
                        history={tradingHistory}
                    />
                )}
            </div>
        </div>
    );
}

export default function StockDetail({ stockName, investmentStyle, initialInvestment, onBack }: StockDetailProps) {
    const [activeTab, setActiveTab] = useState<TabType>("analysis");
    const [selectedIndicator, setSelectedIndicator] = useState<IndicatorGuideInfo | null>(null);
    const [aiData, setAiData] = useState({
        recommendation: "분석 중...",
        aiExplanation: "데이터를 분석하고 있습니다...",
        indicators: {},
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const { modelType } = useInvestmentStyle();
    const tradingHistory = useMemo(() => {
        const priceSeries = generateMockPriceSeries();
        return simulateTradingHistory(initialInvestment, priceSeries, DEFAULT_ACTION_SEQUENCE);
    }, [initialInvestment, stockName]);

    const translateSignal = (signal: string): string => {
        const signalMap: Record<string, string> = {
            buy: "매수",
            sell: "매도",
            hold: "보유",
        };
        return signalMap[signal?.toLowerCase()] || "분석 중";
    };

    const getMockPredictionResult = (model: string) => {
        const mockResults: Record<string, any> = {
            model2: {
                signal: "buy",
                confidence_score: 0.75,
                gpt_explanation:
                    "전반적으로 하락세를 유지하고 있으며, 주가는 추가 하락 가능성이 높습니다. 시장 상황에 대한 신중한 접근과 경계를 유지하여 변동성에 대비하는 것이 중요합니다.",
                technical_indicators: {
                    EMA12: 61500,
                    EMA26: 60800,
                    MACD: 0.5,
                    RSI: 65,
                    Volume: 1500000,
                },
            },
            marl: {
                signal: "hold",
                confidence_score: 0.68,
                gpt_explanation:
                    "MARL 4-Agent 모델 분석: 단기/장기/위험/감성 에이전트가 종합 분석한 결과, 현재 보유 전략이 적절합니다. 시장 불확실성을 고려한 신중한 접근이 필요합니다.",
                technical_indicators: {
                    SMA20: 62000,
                    MACD: 0.3,
                    RSI: 58,
                    Stoch_K: 70,
                    Volume: 1200000,
                },
            },
            model3: {
                signal: "hold",
                confidence_score: 0.82,
                gpt_explanation:
                    "MARL 3-Agent 모델 분석: 안정적인 수익을 목표로 하는 전략으로, 현재 보유가 최적입니다. 리스크를 최소화하며 장기적 관점에서 접근하세요.",
                technical_indicators: {
                    DebtRatio: 45.3,
                    ROE: 15,
                    PER: 12,
                    PBR: 1.2,
                    DividendYield: 3.5,
                },
            },
        };

        return mockResults[model] || mockResults.marl;
    };

    const getFallbackRecommendation = (model: string) => {
        const fallbackData: Record<string, any> = {
            model2: {
                recommendation: "매수",
                aiExplanation:
                    "공격적 투자 성향에 맞는 분석을 진행 중입니다. 높은 수익을 추구하는 전략으로 접근하세요.",
                indicators: {},
            },
            marl: {
                recommendation: "보유",
                aiExplanation:
                    "균형잡힌 투자 전략을 바탕으로 분석 중입니다. 리스크와 수익의 균형을 고려한 접근이 필요합니다.",
                indicators: {},
            },
            model3: {
                recommendation: "보유",
                aiExplanation:
                    "안정적인 투자 전략에 맞는 분석을 진행 중입니다. 장기적 관점에서 안전한 투자를 추천합니다.",
                indicators: {},
            },
        };

        return fallbackData[model] || fallbackData.marl;
    };

    useEffect(() => {
        const loadAIAnalysis = async () => {
            try {
                setLoading(true);
                setError(null);

                const mockFeatures = {
                    SMA20: 62000,
                    MACD: 0.5,
                    RSI: 65,
                    Stoch_K: 70,
                    EMA12: 61500,
                    EMA26: 60800,
                    Volume: 1500000,
                    ATR: 2500,
                    Bollinger_B: 0.8,
                    VIX: 18.5,
                    ROA: 8.2,
                    DebtRatio: 45.3,
                    AnalystRating: 3.5,
                };

                let result;
                try {
                    await api.health();
                    result = await api.predictByInvestmentStyle(modelType, mockFeatures);
                } catch (apiError) {
                    console.warn("백엔드 API 호출 실패, Mock 데이터 사용:", apiError);
                    result = getMockPredictionResult(modelType);
                }

                setAiData({
                    recommendation: translateSignal(result.signal),
                    aiExplanation:
                        result.gpt_explanation || "현재 시장 상황을 종합적으로 분석한 결과입니다.",
                    indicators: result.technical_indicators || {},
                });
            } catch (err) {
                console.error("AI 분석 데이터 로딩 실패:", err);
                setError("분석 데이터를 불러오는데 실패했습니다.");
                setAiData(getFallbackRecommendation(modelType));
            } finally {
                setLoading(false);
            }
        };

        loadAIAnalysis();
    }, [modelType]);

    return (
        <div className="relative min-h-screen w-full bg-white overflow-y-scroll" style={{ scrollbarGutter: "stable" }} data-name="종목 상세">
            <StockDetailContent
                stockName={stockName}
                onBack={onBack}
                recommendation={aiData.recommendation}
                aiExplanation={aiData.aiExplanation}
                activeTab={activeTab}
                onTabChange={setActiveTab}
                onIndicatorClick={setSelectedIndicator}
                investmentStyle={investmentStyle}
                tradingHistory={tradingHistory}
                loading={loading}
                error={error}
            />

            <IndicatorModal indicator={selectedIndicator} onClose={() => setSelectedIndicator(null)} />
        </div>
    );
}
