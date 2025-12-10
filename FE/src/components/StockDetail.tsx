import { useEffect, useRef, useState, type ComponentType, type SVGProps } from "react";
import Header from "@/components/layout/Header";
import CaretLeftIcon from "@/assets/icons/caret-left.svg?react";
import CaretDownIcon from "@/assets/icons/caret-down.svg?react";
import AiSparkIcon from "@/assets/icons/AI.svg?react";
import InfoIcon from "@/assets/icons/info.svg?react";
import CrownIcon from "@/assets/icons/crown.svg?react";
import { createChart } from "lightweight-charts";
import IndicatorModal from "./IndicatorModal";
import { getIndicatorsByStyle, type IndicatorInfo } from "../data/indicatorsByStyle";
import { type InvestmentStyle } from "../contexts/InvestmentStyleContext";
import { api } from "../api/client";
import { resolveStockSymbol } from "@/lib/stocks";
import {
    DayTrading,
    type SimulatedTrade,
    generateMockPriceSeries,
    generateRandomActions,
    simulateTradingHistory,
} from "@/utils/aiTradingSimulation";


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

// Mock 데이터 캐시 (종목별로 동일한 데이터 유지)
const mockDataCache: Record<string, Array<{ time: number; value: number }>> = {};

// 거래 내역 계산 함수
function calculateTradingHistory(
    aiHistory: Array<{ date: string; signal: number; daily_return?: number; strategy_return?: number }>,
    stockHistory: Array<{ date: string; open: number; high: number; low: number; close: number }>,
    initialCapital: number
): DayTrading[] {
    const history: DayTrading[] = [];
    let cash = initialCapital;
    let shares = 0;
    let avgPrice = 0;

    // 주가 데이터를 날짜별로 매핑
    const priceMap = new Map(
        stockHistory.map(item => [item.date.split('T')[0], item])
    );

    aiHistory.forEach((signal) => {
        const dateStr = signal.date;
        const priceData = priceMap.get(dateStr);
        
        if (!priceData) return;

        const trades: SimulatedTrade[] = [];

        // signal: 0 = BUY (Long), 1 = SELL (Short), 2 = HOLD
        if (signal.signal === 0) {
            // 매수 시그널
            const buyPrice = priceData.low || priceData.close || priceData.open; // 당일 최저가로 매수
            const maxShares = Math.floor(cash / buyPrice);

            if (maxShares > 0) {
                // 매수 가능
                const buyShares = maxShares;
                const cost = buyShares * buyPrice;
                
                // 평균 단가 계산
                if (shares > 0) {
                    avgPrice = ((avgPrice * shares) + cost) / (shares + buyShares);
                } else {
                    avgPrice = buyPrice;
                }
                
                shares += buyShares;
                cash -= cost;

                trades.push({
                    type: "buy",
                    quantity: buyShares,
                    pricePerShare: buyPrice,
                    time: dateStr,
                });
            } else {
                // 매수 불가 (자금 부족)
                trades.push({
                    type: "hold",
                    quantity: 0,
                    pricePerShare: 0,
                    time: dateStr,
                    reason: "매수 자금이 부족합니다.",
                });
            }
        } else if (signal.signal === 1) {
            // 매도 시그널
            if (shares > 0) {
                const sellPrice = priceData.high || priceData.close || priceData.open; // 당일 최고가로 매도
                const sellShares = shares;
                const revenue = sellShares * sellPrice;
                const profit = revenue - (avgPrice * sellShares);
                const profitPercent = ((sellPrice - avgPrice) / avgPrice) * 100;

                cash += revenue;
                shares = 0;
                avgPrice = 0;

                trades.push({
                    type: "sell",
                    quantity: sellShares,
                    pricePerShare: sellPrice,
                    time: dateStr,
                    profit: Math.round(profit),
                    profitPercent: Math.round(profitPercent * 10) / 10,
                });
            } else {
                // 매도 불가 (보유 주식 없음)
                trades.push({
                    type: "hold",
                    quantity: 0,
                    pricePerShare: 0,
                    time: dateStr,
                    reason: "보유 중인 주식이 없습니다.",
                });
            }
        } else {
            // 보유 시그널
            trades.push({
                type: "hold",
                quantity: 0,
                pricePerShare: 0,
                time: dateStr,
                reason: "리브리 전략에 따라 변동이 없습니다.",
            });
        }

        if (trades.length > 0) {
            history.push({
                date: dateStr,
                trades,
            });
        }
    });

    return history;
}

function SparklineChart({ stockSymbol }: { stockSymbol: string }) {
    const chartContainerRef = useRef<HTMLDivElement>(null);
    const chartInstanceRef = useRef<ReturnType<typeof createChart> | null>(null);
    const seriesRef = useRef<any>(null);

    useEffect(() => {
        const container = chartContainerRef.current;
        if (!container) return;

        // Mock 데이터 생성 함수 (백엔드 연결 실패 시 사용)
        // 종목별로 동일한 데이터를 반환하도록 캐싱
        const generateMockData = () => {
            // 이미 생성된 Mock 데이터가 있으면 재사용
            if (mockDataCache[stockSymbol]) {
                return mockDataCache[stockSymbol];
            }

            const data = [];
            const basePrice = 60000;
            const now = new Date();

            // 종목 이름을 시드로 사용하여 일관된 랜덤 데이터 생성
            let seed = 0;
            for (let i = 0; i < stockSymbol.length; i++) {
                seed += stockSymbol.charCodeAt(i);
            }

            for (let i = 30; i >= 0; i--) {
                const date = new Date(now);
                date.setDate(date.getDate() - i);
                
                // 시드 기반 의사 랜덤 생성 (동일한 종목은 항상 같은 패턴)
                seed = (seed * 9301 + 49297) % 233280;
                const randomChange = ((seed / 233280) - 0.5) * 3000;
                const price = basePrice + randomChange + (30 - i) * 100;
                
                data.push({ time: Math.floor(date.getTime() / 1000) as any, value: price });
            }

            // 캐시에 저장
            mockDataCache[stockSymbol] = data;
            return data;
        };

        const loadChartData = async () => {
            try {
                // 백엔드에서 최근 30일 주가 데이터 가져오기
                const historyData = await api.getStockHistory(stockSymbol, 30);
                
                if (!historyData || historyData.length === 0) {
                    throw new Error("Stock data is empty");
                }
                
                // 데이터를 차트 형식으로 변환
                const chartData = historyData
                    .map((item: any) => {
                        const dateStr = item.date.split('T')[0]; // YYYY-MM-DD 형식으로 변환
                        return {
                            time: dateStr as any,
                            value: item.close || 0,
                        };
                    })
                    .sort((a: any, b: any) => a.time.localeCompare(b.time));

                if (chartInstanceRef.current && seriesRef.current && chartData.length > 0) {
                    seriesRef.current.setData(chartData);
                    chartInstanceRef.current.timeScale().fitContent();
                }
            } catch (error) {
                console.error("주가 데이터 로딩 실패, Mock 데이터 사용:", error);
                // 에러 시 Mock 데이터 사용
                if (chartInstanceRef.current && seriesRef.current) {
                    seriesRef.current.setData(generateMockData());
                    chartInstanceRef.current.timeScale().fitContent();
                }
            }
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

        seriesRef.current = chart.addAreaSeries({
            lineColor: "#1FA9A4",
            lineWidth: 2,
            topColor: "rgba(31,169,164,0.16)",
            bottomColor: "rgba(31,169,164,0)",
            priceLineVisible: false,
            lastValueVisible: false,
            crosshairMarkerVisible: false,
        });

        loadChartData();

        let cleanupResize: (() => void) | null = null;

        if (typeof ResizeObserver !== "undefined") {
            const resizeObserver = new ResizeObserver((entries) => {
                const entry = entries[0];
                if (!entry || !chartInstanceRef.current) return;
                const nextWidth = Math.floor(entry.contentRect.width);
                if (nextWidth > 0) {
                    chartInstanceRef.current.applyOptions({ width: nextWidth });
                }
            });

            resizeObserver.observe(container);
            cleanupResize = () => resizeObserver.disconnect();
        } else {
            const handleWindowResize = () => {
                if (!chartInstanceRef.current || !container) return;
                const nextWidth = Math.floor(container.clientWidth);
                if (nextWidth > 0) {
                    chartInstanceRef.current.applyOptions({ width: nextWidth });
                }
            };

            window.addEventListener("resize", handleWindowResize);
            cleanupResize = () => window.removeEventListener("resize", handleWindowResize);
        }

        return () => {
            cleanupResize?.();
            chart.remove();
            chartInstanceRef.current = null;
        };
    }, [stockSymbol]);

    return <div ref={chartContainerRef} className="h-12 w-full" />;
}

function RecommendationCard({
    stockName,
    recommendation,
    aiExplanation,
    loading,
    error,
}: {
    stockName: string;
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
                    <p className="label-2 text-[#6b6e74] tracking-[0.2px]">추천 행동</p>
                    <p className="text-[36px] tracking-[1.2px] text-[#1fa9a4]" style={{ fontWeight: 700 }}>
                        {recommendation}
                    </p>
                </div>
                <SparklineChart stockSymbol={stockName} />
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
    { id: "trading", label: "AI 가상 거래" },
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

function formatDateForDisplay(dateStr: string) {
    // YYYY-MM-DD 형식의 날짜를 받아서 표시용으로 변환
    const today = new Date();
    const targetDate = new Date(dateStr);
    
    // 오늘 날짜와 비교
    const todayStr = today.toISOString().split('T')[0];
    const yesterdayStr = new Date(today.getTime() - 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    
    if (dateStr === todayStr) {
        return "오늘";
    } else if (dateStr === yesterdayStr) {
        return "어제";
    } else {
        // n월 n일 형식으로 표시
        const month = targetDate.getMonth() + 1;
        const day = targetDate.getDate();
        return `${month}월 ${day}일`;
    }
}

function Top3AnalysisSection({
    investmentStyle,
    onIndicatorClick,
    xaiFeatures,
}: {
    investmentStyle: InvestmentStyle;
    onIndicatorClick: (indicator: IndicatorGuideInfo) => void;
    xaiFeatures: Array<{
        base: string;
        shap: number;
        direction: string;
        description: string;
    }>;
}) {
    const rankColors = ["#FFD700", "#C0C0C0", "#CD7F32"];
    const referenceLabel = getTop3ReferenceLabel();
    
    // 백엔드에서 받은 XAI 데이터를 IndicatorInfo 형식으로 변환
    const indicators: IndicatorInfo[] = xaiFeatures.length > 0 
        ? xaiFeatures.slice(0, 3).map((feature, index) => {
            const shapValue = typeof feature.shap === "number" ? feature.shap : 0;
            const impact = Math.abs(shapValue).toFixed(4);
            const shapText = shapValue.toFixed(6);

            return {
                id: `xai-${index}`,
                title: feature.base,
                value: impact,
                status: (feature.direction === "지지" ? "positive" : "negative") as "positive" | "negative" | "neutral",
                shortDescription: `${feature.description} - AI가 이 지표를 ${feature.direction} 요인으로 판단했습니다. (영향도: ${impact})`,
                detailedDescription: feature.description,
                interpretationPoints: [
                    `이 지표는 AI 모델의 결정에 ${feature.direction === "지지" ? "긍정적" : "부정적"}인 영향을 미쳤습니다.`,
                    `SHAP 값: ${shapText}`,
                    `${feature.direction === "지지" ? "매수" : "매도"} 신호를 강화하는 요인입니다.`,
                ],
            };
        })
        : getIndicatorsByStyle(investmentStyle).top3; // 폴백: 기존 정적 데이터
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

function TradeItem({ trade }: { trade: SimulatedTrade }) {
    if (trade.type === "hold") {
        return (
            <div className="rounded-2xl bg-[#f8f9fb] p-4">
                <p className="title-3 text-[#151b26]">거래 내역 변화 없음</p>
                <p className="mt-1 body-3 text-[#6b6e74]">
                    {trade.reason ?? "리브리 전략에 따라 변동이 없습니다."}
                </p>
            </div>
        );
    }

    const isSell = trade.type === "sell";

    return (
        <div className="rounded-2xl bg-[#f8f9fb] p-4">
            <p className="title-3 text-[#151b26]">
                {trade.quantity}주 {isSell ? "판매" : "구매"}
            </p>
            {isSell && trade.profit !== undefined && trade.profitPercent !== undefined ? (
                <p
                    className="mt-1 title-3"
                    style={{ color: trade.profit > 0 ? "var(--component-red)" : "var(--component-blue)" }}
                >
                    {trade.profit > 0 ? "+" : ""}
                    {trade.profit.toLocaleString()}원 ({trade.profitPercent > 0 ? "+" : ""}
                    {trade.profitPercent}%)
                </p>
            ) : null}
            <span
                className="label-3"
                style={{ color: "var(--achromatic-500)", display: "inline-block", marginTop: "4px" }}
            >
                1주당 {trade.pricePerShare.toLocaleString()}원
            </span>
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
        const entries = history
        .map((day) => ({
            ...day,
            trades: day.trades.filter((trade) => trade.type !== "hold"),
        }))
        .filter((day) => day.trades.length > 0);
    return (
        <section className="flex w-full flex-col gap-4 pb-16" style={{ paddingInline: "20px" }}>
            <div className="flex items-center justify-between body-3" style={{ color: "var(--achromatic-500)" }}>
                <span className="body-3">{referenceLabel} 20:30분 기준</span>
                <button
                    type="button"
                    className="flex items-center gap-[2px]"
                    onClick={() =>
                        onGuideClick({
                            title: "AI 가상 거래 안내",
                            description: "AI 가상 거래는 실제 매매가 아닌 모델 기반 시뮬레이션입니다.",
                            fullDescription:
                                "리브리 모델이 추천 전략대로 거래했다면 어떤 수익을 기대할 수 있는지를 가정한 결과입니다. 실제 매매가 아니며, 사용자의 초기 투자금과 시장 데이터에 기반해 산출한 모의 성과입니다.",
                            interpretationPoints: [
                                "AI 가상 거래는 실제로 실행된 거래가 아닙니다.",
                                "사용자의 초기 투자금으로 리브리 추천을 따른 경우의 가상 수익입니다.",
                                "참고용 정보이며 매매 판단은 사용자 책임 하에 진행해야 합니다.",
                                "",
                                "AI 거래 내역은 어떻게 추가되나요?",
                                "- 리브리가 '보유'를 추천한 경우엔 '거래 내역 변화 없음'이 표시됩니다.",
                                "- 리브리가 '매수'를 추천한 경우엔 해당 일 최저가(최초 형성 시각) 기준으로 보유 현금이 허용하는 한 매수합니다.",
                                "- 리브리가 '매도'를 추천한 경우엔 해당 일 최고가(최초 형성 시각) 기준으로 보유 수량 전량을 매도합니다.",
                            ],
                        })
                    }
                >
                    <span>AI 가상 거래 안내</span>
                    <InfoIcon className="h-[16px] w-[16px] text-[#b0b4bd]" aria-hidden />
                </button>
            </div>
            <div className="flex flex-col gap-6">
                {entries.length === 0 ? (
                    <p className="text-xs text-[#9a9ea9]">거래 내역이 없습니다.</p>
                ) : (
                    entries.map((day) => (
                        <div key={day.date} className="flex flex-col gap-3">
                            <p
                                className="body-3"
                                style={{ color: "var(--achromatic-500)", marginTop: "16px", marginBottom: "8px" }}
                            >
                                {formatDateForDisplay(day.date)}
                            </p>
                            <div className="flex flex-col gap-3">
                                {day.trades.map((trade, index) => (
                                    <TradeItem key={`${day.date}-${index}`} trade={trade} />
                                ))}
                            </div>
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
    xaiFeatures,
    isBackendConnected,
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
    xaiFeatures: Array<{
        base: string;
        shap: number;
        direction: string;
        description: string;
    }>;
    isBackendConnected: boolean;
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
                    stockName={stockName}
                    recommendation={recommendation}
                    aiExplanation={aiExplanation}
                    loading={loading}
                    error={error}
                />
                {!isBackendConnected && (
                    <div className="w-full" style={{ paddingInline: "20px" }}>
                        <div className="rounded-[12px] bg-[#fff3cd] border border-[#ffeaa7] p-3">
                            <p className="body-3 text-[#856404] mb-2">
                                ⚠️ 백엔드 서버에 연결할 수 없어 Mock 데이터를 표시하고 있습니다.
                            </p>
                            <p className="body-3 text-[#856404] text-xs">
                                실제 데이터를 보려면 백엔드 서버를 실행해주세요:<br/>
                                <code className="bg-[#f8f9fa] px-1 rounded">cd BE && uvicorn app.main:app --reload --port 8000</code>
                            </p>
                            <p className="body-3 text-[#856404] text-xs mt-1">
                                OpenAI API 키도 BE/.env 파일에 설정해주세요.
                            </p>
                        </div>
                    </div>
                )}
                <div style={{ marginTop: "30px", paddingInline: "20px", marginBottom: "16px" }}>
                    <DetailTabs activeTab={activeTab} onSelect={onTabChange} />
                </div>
                {activeTab === "top3" && (
                    <Top3AnalysisSection
                        investmentStyle={investmentStyle}
                        onIndicatorClick={onIndicatorClick}
                        xaiFeatures={xaiFeatures}
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
    const [activeTab, setActiveTab] = useState<TabType>("top3");
    const [selectedIndicator, setSelectedIndicator] = useState<IndicatorGuideInfo | null>(null);
    const [aiData, setAiData] = useState({
        recommendation: "분석 중...",
        aiExplanation: "데이터를 분석하고 있습니다...",
        indicators: {},
        xaiFeatures: [] as Array<{
            base: string;
            shap: number;
            direction: string;
            description: string;
        }>,
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [tradingHistory, setTradingHistory] = useState<DayTrading[]>([]);
    const [isBackendConnected, setIsBackendConnected] = useState(false);

    const translateSignal = (signal: string): string => {
        const signalMap: Record<string, string> = {
            buy: "매수",
            sell: "매도",
            hold: "보유",
        };
        return signalMap[signal?.toLowerCase()] || "분석 중";
    };

    const getMockPredictionResult = (model: string) => {
        const mockResults: Record<string, { signal: string; gpt_explanation: string }> = {
            model2: {
                signal: "buy",
                gpt_explanation:
                    "전반적으로 하락세를 유지하고 있으며, 주가는 추가 하락 가능성이 높습니다. 시장 상황에 대한 신중한 접근과 경계를 유지하여 변동성에 대비하는 것이 중요합니다.",
            },
            model3: {
                signal: "hold",
                gpt_explanation:
                    "안정적인 수익을 목표로 하는 전략으로, 현재 보유가 최적입니다. 리스크를 최소화하며 장기적 관점에서 접근하세요.",
            },
        };

        return mockResults[model] || mockResults.model3;
    };

    useEffect(() => {
        const loadAIAnalysis = async () => {
            try {
                setLoading(true);
                setError(null);

                // 종목 코드 변환 (삼성전자 -> 005930)
                const symbol = resolveStockSymbol(stockName) || "005930.KS";

                // 투자 성향 변환 (공격형 -> aggressive, 안정형 -> conservative)
                const styleMap: Record<string, "aggressive" | "conservative"> = {
                    "공격형": "aggressive",
                    "안정형": "conservative",
                };
                const investmentStyleEn = styleMap[investmentStyle] || "aggressive";

                let result;
                try {
                    // 백엔드 API 호출
                    await api.health();
                    setIsBackendConnected(true);
                    result = await api.predictByInvestmentStyle(symbol, investmentStyleEn);
                } catch (apiError) {
                    console.warn("백엔드 API 호출 실패, Mock 데이터 사용:", apiError);
                    setIsBackendConnected(false);
                    // Mock 데이터 폴백
                    result = getMockPredictionResult(investmentStyleEn === "aggressive" ? "model2" : "model3");
                }

                setAiData({
                    recommendation: translateSignal(result.signal || result.action),
                    aiExplanation:
                        result.gpt_explanation || result.explanation || "현재 시장 상황을 종합적으로 분석한 결과입니다.",
                    indicators: result.technical_indicators || {},
                xaiFeatures: Array.isArray(result.xai_features) ? result.xai_features : [],
                });
            } catch (err) {
                console.error("AI 분석 데이터 로딩 실패:", err);
                setError("분석 데이터를 불러오는데 실패했습니다.");
                // 최종 폴백
                const fallback = getMockPredictionResult("model3");
                setAiData({
                    recommendation: translateSignal(fallback.signal),
                    aiExplanation: fallback.gpt_explanation || "현재 시장 상황을 종합적으로 분석한 결과입니다.",
                    indicators: {},
                    xaiFeatures: [],
                });
            } finally {
                setLoading(false);
            }
        };

        loadAIAnalysis();
    }, [stockName, investmentStyle]);

    // 거래 내역 로드
    useEffect(() => {
        const loadTradingHistory = async () => {
            try {

                // 종목 코드 변환
                const symbol = resolveStockSymbol(stockName) || "005930.KS";

                // 모델 타입 결정 (공격형 -> a2c, 안정형 -> marl)
                const modelType = investmentStyle === "공격형" ? "a2c" : "marl";

                // 30일 전부터 데이터 가져오기
                const startDate = new Date();
                startDate.setDate(startDate.getDate() - 30);
                const startDateStr = startDate.toISOString().split('T')[0];

                // AI 히스토리와 주가 데이터 동시 가져오기
                const [aiHistory, stockHistory] = await Promise.all([
                    api.getAIHistory(modelType, startDateStr),
                    api.getStockHistory(symbol, 30)
                ]);

                // 거래 내역 계산
                const history = calculateTradingHistory(aiHistory, stockHistory, initialInvestment);
                setTradingHistory(history);
            } catch (error) {
                console.error("거래 내역 로딩 실패, Mock 데이터 사용:", error);
                // 폴백: Mock 데이터 사용
                const priceSeries = generateMockPriceSeries(stockName);
                const actionPlan = generateRandomActions(stockName, priceSeries.length || 5);
                const { history } = simulateTradingHistory(initialInvestment, priceSeries, actionPlan);
                
                // Mock 데이터의 날짜를 실제 날짜 형식으로 변환
                const today = new Date();
                const updatedHistory = history.map((day, index) => {
                    const date = new Date(today);
                    date.setDate(date.getDate() - index);
                    const dateStr = date.toISOString().split('T')[0]; // YYYY-MM-DD 형식
                    
                    return {
                        ...day,
                        date: dateStr,
                    };
                });
                
                setTradingHistory(updatedHistory);
            }
        };

        loadTradingHistory();
    }, [stockName, investmentStyle, initialInvestment]);

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
                xaiFeatures={aiData.xaiFeatures}
                isBackendConnected={isBackendConnected}
            />

            <IndicatorModal indicator={selectedIndicator} onClose={() => setSelectedIndicator(null)} />
        </div>
    );
}
