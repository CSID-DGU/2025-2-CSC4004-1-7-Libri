import { useEffect, useRef, useState, useMemo, type ComponentType, type SVGProps } from "react";
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
import { DayTrading, type SimulatedTrade } from "@/utils/aiTradingSimulation";
import {
    fetchAiTradingSummary,
    getReferenceDate,
    isStockSupported,
    type TradingSummary,
} from "@/utils/aiTradingSummary";

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
    onSimulatedHoldingsUpdate?: (stockName: string, summary: TradingSummary | null) => void;
    userCreatedAt?: string | null;
    userId?: number | null;
}

// Mock 데이터 캐시 (종목별로 동일한 데이터 유지)
const mockDataCache: Record<string, Array<{ time: number; value: number }>> = {};

type XAIReference = {
    base?: string;
    name?: string;
    indicator?: string;
    shap?: number;
    importance?: number;
    direction?: string;
    description?: string;
    short_description?: string;
    explain?: string;
    explanation?: string;
};

interface PredictionData {
    recommendation: string;
    aiExplanation: string;
    indicators: Record<string, number>;
    xaiFeatures: XAIReference[];
}

function isErrorPrediction(data: PredictionData | undefined): boolean {
    if (!data) return true;
    const explanation = (data.aiExplanation || "").toLowerCase();
    if (explanation.includes("오류") || explanation.includes("error")) return true;
    if (!data.xaiFeatures || data.xaiFeatures.length === 0) return true;
    return false;
}

// 거래 내역 계산 함수
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
                // 종목 코드 변환 (삼성전자 -> 005930.KS)
                const symbol = resolveStockSymbol(stockSymbol) || "005930.KS";
                console.log("차트용 종목 코드:", symbol, "원본:", stockSymbol);
                
                // 백엔드에서 최근 30일 주가 데이터 가져오기
                const historyData = await api.getStockHistory(symbol, 30);
                
                if (!historyData || historyData.length === 0) {
                    throw new Error("Stock data is empty");
                }
                
                console.log("주가 데이터 로딩 성공:", historyData.length, "개 데이터");
                
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
                
                // 구체적인 에러 정보 로깅
                if (error instanceof Error) {
                    console.error("에러 메시지:", error.message);
                    if ('status' in error) {
                        console.error("HTTP 상태:", (error as any).status);
                    }
                }
                
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
    aiSupported,
}: {
    stockName: string;
    recommendation: string;
    aiExplanation: string;
    loading: boolean;
    error: string | null;
    aiSupported: boolean;
}) {
    const displayRecommendation = aiSupported ? recommendation : "-";
    const displayExplanation = aiSupported ? aiExplanation : "지원되지 않습니다";

    return (
        <div className="w-full" style={{ paddingInline: "20px" }}>
            <section
                className="rounded-[16px] bg-[#f2f4f8] flex flex-col"
                style={{ padding: "20px", gap: "20px" }}
            >
                <div className="flex flex-col gap-1">
                    <p className="label-2 text-[#6b6e74] tracking-[0.2px]">추천 행동</p>
                    <p className="text-[36px] tracking-[1.2px] text-[#1fa9a4]" style={{ fontWeight: 700 }}>
                        {displayRecommendation}
                    </p>
                </div>
                {aiSupported ? (
                    <SparklineChart stockSymbol={stockName} />
                ) : (
                    <div className="h-12 flex items-center justify-center rounded-[12px] bg-white text-[#9a9ea9]">
                        지원되지 않습니다
                    </div>
                )}
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
                    ) : !aiSupported ? (
                        <p className="body-2 text-[#6b6e74]">지원되지 않습니다</p>
                    ) : (
                        <p className="body-2 text-[#151b26]">{displayExplanation}</p>
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
    const displayTitle =
        (typeof indicator.title === "string" && indicator.title.trim().length > 0)
            ? indicator.title.trim()
            : indicator.id || "AI 주요 지표";

    return (
        <div
            className="w-full rounded-[16px] bg-[#f2f4f8] text-left"
            style={{ padding: "16px 20px 20px" }}
        >
            <div className="flex items-center gap-[4px]">
                <CrownIcon className="h-4 w-4" style={{ color: crownColor }} aria-hidden />
                <span className="title-3 text-[#1fa9a4] tracking-[0.16px]">{displayTitle}</span>
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
    const referenceDate = getReferenceDate(now);
    const year = referenceDate.getFullYear();
    const month = String(referenceDate.getMonth() + 1).padStart(2, "0");
    const day = String(referenceDate.getDate()).padStart(2, "0");
    return `${year}.${month}.${day}`;
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
    loading,
    isSupported,
}: {
    investmentStyle: InvestmentStyle;
    onIndicatorClick: (indicator: IndicatorGuideInfo) => void;
    xaiFeatures: XAIReference[];
    loading: boolean;
    isSupported: boolean;
}) {
    const rankColors = ["#FFD700", "#C0C0C0", "#CD7F32"];
    const referenceLabel = getTop3ReferenceLabel();
    
    // 백엔드에서 받은 XAI 데이터를 IndicatorInfo 형식으로 변환
    const hasXaiData = xaiFeatures.length > 0;
    
    // XAI 데이터 디버깅
    console.log("Top3AnalysisSection - xaiFeatures:", xaiFeatures);
    
    const indicators: IndicatorInfo[] = hasXaiData
        ? xaiFeatures.slice(0, 3).map((feature, index) => {
            const shapSource =
                typeof feature.shap === "number"
                    ? feature.shap
                    : typeof feature.importance === "number"
                        ? feature.importance
                        : 0;
            const shapValue = shapSource ?? 0;
            const impact = Math.abs(shapValue).toFixed(4);
            const shapText = shapValue.toFixed(6);
            const rawTitle = feature.name ?? feature.base ?? feature.indicator ?? "";
            const displayTitle =
                (typeof rawTitle === "string" && rawTitle.trim().length > 0)
                    ? rawTitle.trim()
                    : `AI 주요 지표 ${index + 1}`;
            const direction = feature.direction ?? (shapValue >= 0 ? "지지" : "방해");
            const description =
                feature.description ||
                feature.short_description ||
                `${displayTitle} 지표`;

            // 백엔드에서 받은 설명 사용 (explain 필드 우선)
            const backendExplanation = feature.explain || feature.explanation;
            
            // 디버깅 로그
            console.log(`Feature ${index} (${displayTitle}):`, {
                explain: feature.explain,
                explanation: feature.explanation,
                backendExplanation,
                hasValidExplanation: backendExplanation && backendExplanation.trim().length > 0
            });
            
            // 백엔드 explain 필드를 우선 사용, 없으면 기본 템플릿
            let finalDescription;
            if (feature.explain && typeof feature.explain === 'string' && feature.explain.trim().length > 0) {
                finalDescription = feature.explain.trim();
            } else if (feature.explanation && typeof feature.explanation === 'string' && feature.explanation.trim().length > 0) {
                finalDescription = feature.explanation.trim();
            } else {
                finalDescription = `${description} - AI가 이 지표를 ${direction} 요인으로 판단했습니다. (영향도: ${impact})`;
            }

            return {
                id: `xai-${index}`,
                title: displayTitle,
                value: impact,
                status: direction === "지지" ? "positive" : "negative",
                shortDescription: finalDescription,
                detailedDescription: backendExplanation || description,
                interpretationPoints: [
                    backendExplanation || `이 지표는 AI 모델의 결정에 ${direction === "지지" ? "긍정적" : "부정적"}인 영향을 미쳤습니다.`,
                    `SHAP 값: ${shapText}`,
                    `${direction === "지지" ? "매수" : "매도"} 신호를 강화하는 요인입니다.`,
                ],
            };
        })
        : getIndicatorsByStyle(investmentStyle).top3; // 폴백: 기존 정적 데이터

    if (!isSupported) {
        return (
            <section className="flex w-full flex-col gap-[8px]" style={{ paddingInline: "20px" }}>
                <div
                    className="flex items-center justify-between body-3"
                    style={{ color: "var(--achromatic-500)" }}
                >
                    <span className="body-3">{referenceLabel} (20:30 기준)</span>
                </div>
                <div className="rounded-[16px] bg-[#f2f4f8] p-6 text-center text-[#9a9ea9]">
                    이 종목은 AI 예측 데이터를 지원하지 않습니다.
                </div>
            </section>
        );
    }
    return (
        <section className="flex w-full flex-col gap-[8px]" style={{ paddingInline: "20px" }}>
            <div
                className="flex items-center justify-between body-3"
                style={{ color: "var(--achromatic-500)" }}
            >
                <span className="body-3">{referenceLabel} (20:30 기준)</span>
            </div>
            <div className="flex flex-col" style={{ gap: "16px" }}>
                {loading ? (
                    [1, 2, 3].map((idx) => (
                        <div
                            key={`top3-loading-${idx}`}
                            className="w-full rounded-[16px] bg-[#f2f4f8] text-left"
                            style={{ padding: "16px 20px 20px" }}
                        >
                            <div className="flex items-center gap-[4px]">
                                <CrownIcon className="h-4 w-4" style={{ color: rankColors[idx - 1] ?? rankColors[rankColors.length - 1] }} aria-hidden />
                                <span className="title-3 text-[#1fa9a4] tracking-[0.16px]">분석 중입니다...</span>
                            </div>
                            <p className="body-2 leading-6 text-[#151b26]" style={{ marginTop: "8px" }}>
                                잠시만 기다려 주세요. AI가 TOP3 지표를 선정하고 있습니다.
                            </p>
                        </div>
                    ))
                ) : (
                    indicators.map((indicator, index) => {
                        const crownColor = rankColors[index] ?? rankColors[rankColors.length - 1];
                        return <Top3IndicatorCard key={indicator.id} indicator={indicator} crownColor={crownColor} />;
                    })
                )}
            </div>
        </section>
    );
}

function TradeItem({ trade }: { trade: SimulatedTrade }) {
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
    isSupported,
}: {
    onGuideClick: (info: IndicatorGuideInfo) => void;
    history: DayTrading[];
    isSupported: boolean;
}) {
    const referenceLabel = getTop3ReferenceLabel();
    const entries = history
        .map((day) => ({
            ...day,
            trades: day.trades.filter((trade) => trade.type !== "hold"),
        }))
        .filter((day) => day.trades.length > 0)
        .sort((a, b) => b.date.localeCompare(a.date));
    if (!isSupported) {
        return (
            <section className="flex w-full flex-col gap-4 pb-16" style={{ paddingInline: "20px" }}>
                <div className="flex items-center justify-between body-3" style={{ color: "var(--achromatic-500)" }}>
                    <span className="body-3">{referenceLabel} (20:30 기준)</span>
                </div>
                <div
                    className="flex flex-col items-center text-center w-full text-[#9a9ea9]"
                    style={{ marginTop: "80px" }}
                >
                    <InfoIcon className="h-[32px] w-[32px]" aria-hidden style={{ marginBottom: "8px" }} />
                    <p className="title-3 mb-1 text-[#9a9ea9]">AI 가상 거래 데이터를 지원하지 않습니다.</p>
                </div>
            </section>
        );
    }

    return (
        <section className="flex w-full flex-col gap-4 pb-16" style={{ paddingInline: "20px" }}>
            <div className="flex items-center justify-between body-3" style={{ color: "var(--achromatic-500)" }}>
                <span className="body-3">{referenceLabel} (20:30 기준)</span>
            </div>
            <div className="flex flex-col gap-6">
                {entries.length === 0 ? (
                    <div
                        className="flex flex-col items-center text-center w-full text-[#9a9ea9]"
                        style={{ marginTop: "80px" }}
                    >
                        <InfoIcon
                            className="h-[32px] w-[32px]"
                            aria-hidden
                            style={{
                                marginBottom: "8px",
                                color: "var(--achromatic-500)",
                            }}
                        />
                        <p
                            className="title-3"
                            style={{
                                marginBottom: "4px",
                                color: "var(--achromatic-500)",
                            }}
                        >
                            아직 거래 내역이 없어요
                        </p>
                        <p className="body-3" style={{ color: "var(--achromatic-500)", textAlign: "center" }}>
                            AI가 매수, 매도를 판단하면
                            <br />
                            이곳에 거래 내역이 표시돼요.
                        </p>
                    </div>
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
    aiSupported,
    tradingSupported,
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
    xaiFeatures: XAIReference[];
    aiSupported: boolean;
    tradingSupported: boolean;
}) {
    const showWarning = !loading && (!aiSupported || !tradingSupported);
    const warningMessage = (() => {
        if (aiSupported && tradingSupported) return "";
        if (!aiSupported && !tradingSupported) {
            return "이 종목은 AI 예측 및 가상 거래 데이터를 지원하지 않습니다.";
        }
        if (!aiSupported) {
            return "이 종목은 AI 예측 데이터를 지원하지 않습니다.";
        }
        return "이 종목은 AI 가상 거래 데이터를 지원하지 않습니다.";
    })();

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
                    aiSupported={aiSupported}
                />
                {showWarning && (
                    <div className="w-full" style={{ paddingInline: "20px" }}>
                        <div className="rounded-[12px] bg-[#fff3cd] border border-[#ffeaa7] p-3">
                            <p className="body-3 text-[#856404] mb-2">
                                ⚠️ {warningMessage}
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
                        loading={loading}
                        isSupported={aiSupported}
                    />
                )}
                {activeTab === "analysis" && <IndicatorSection investmentStyle={investmentStyle} />}
                {activeTab === "trading" && (
                    <TradingHistorySection
                        onGuideClick={onIndicatorClick}
                        history={tradingHistory}
                        isSupported={tradingSupported}
                    />
                )}
            </div>
        </div>
    );
}

export default function StockDetail({
    stockName,
    investmentStyle,
    initialInvestment,
    onBack,
    onSimulatedHoldingsUpdate,
    userCreatedAt,
    userId,
}: StockDetailProps) {
    const [activeTab, setActiveTab] = useState<TabType>("top3");
    const [selectedIndicator, setSelectedIndicator] = useState<IndicatorGuideInfo | null>(null);
    const [aiData, setAiData] = useState<PredictionData>({
        recommendation: "분석 중...",
        aiExplanation: "데이터를 분석하고 있습니다...",
        indicators: {},
        xaiFeatures: [],
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [tradingHistory, setTradingHistory] = useState<DayTrading[]>([]);
    const [aiDataSupported, setAiDataSupported] = useState(true);
    const [tradingDataSupported, setTradingDataSupported] = useState(true);
    const stockSupported = useMemo(() => isStockSupported(stockName), [stockName]);

    const translateSignal = (signal: string): string => {
        const signalMap: Record<string, string> = {
            buy: "매수",
            sell: "매도",
            hold: "보유",
        };
        return signalMap[signal?.toLowerCase()] || "분석 중";
    };

    useEffect(() => {
        const loadAIAnalysis = async () => {
            if (!stockSupported) {
                setAiDataSupported(false);
                setAiData({
                    recommendation: "-",
                    aiExplanation: "지원되지 않습니다",
                    indicators: {},
                    xaiFeatures: [],
                });
                setLoading(false);
                return;
            }
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

                let result: any = null;
                try {
                    // 백엔드 API 호출
                    result = await api.predictByInvestmentStyle(symbol, investmentStyleEn);
                    setAiDataSupported(true);
                } catch (apiError) {
                    console.warn("백엔드 API 호출 실패, Mock 데이터 사용:", apiError);
                    setAiDataSupported(false);
                    setAiData({
                        recommendation: "-",
                        aiExplanation: "지원되지 않습니다",
                        indicators: {},
                        xaiFeatures: [],
                    });
                    return;
                }

                if (!result) {
                    setAiDataSupported(false);
                    setAiData({
                        recommendation: "-",
                        aiExplanation: "지원되지 않습니다",
                        indicators: {},
                        xaiFeatures: [],
                    });
                    return;
                }

                const actionKey = typeof result.action === "string" ? result.action.toLowerCase() : "";
                const recommendationText =
                    actionKey ? translateSignal(actionKey) : (result.action_ko || translateSignal(""));
                const explanationText =
                    result.explanation ||
                    result.gpt_explanation ||
                    "현재 시장 상황을 종합적으로 분석한 결과입니다.";
                if (result?.technical_indicators || result?.xai_features) {
                    const nextData: PredictionData = {
                        recommendation: recommendationText,
                        aiExplanation: explanationText,
                        indicators: result.technical_indicators || {},
                        xaiFeatures: Array.isArray(result.xai_features) ? result.xai_features : [],
                    };
                    setAiData(nextData);
                } else {
                    setAiData({
                        recommendation: "-",
                        aiExplanation: "지원되지 않습니다",
                        indicators: {},
                        xaiFeatures: [],
                    });
                    setAiDataSupported(false);
                }
            } catch (err) {
                console.error("AI 분석 데이터 로딩 실패:", err);
                setError("분석 데이터를 불러오는데 실패했습니다.");
                setAiData({
                    recommendation: "-",
                    aiExplanation: "지원되지 않습니다",
                    indicators: {},
                    xaiFeatures: [],
                });
                setAiDataSupported(false);
            } finally {
                setLoading(false);
            }
        };

        loadAIAnalysis();
    }, [stockName, investmentStyle, stockSupported]);

    // 거래 내역 로드
    useEffect(() => {
        let cancelled = false;

        const loadTradingSummary = async () => {
            if (!stockSupported) {
                setTradingDataSupported(false);
                setTradingHistory([]);
                onSimulatedHoldingsUpdate?.(stockName, null);
                return;
            }
            try {
                const result = await fetchAiTradingSummary({
                    stockName,
                    investmentStyle,
                    initialInvestment,
                    userCreatedAt,
                    userId,
                });
                if (cancelled) return;
                setTradingDataSupported(result.backendConnected);
                setTradingHistory(result.history);
                onSimulatedHoldingsUpdate?.(stockName, result.summary);
            } catch (error) {
                console.error("AI 거래 요약 로딩 실패:", error);
                if (!cancelled) {
                    setTradingDataSupported(false);
                    setTradingHistory([]);
                    onSimulatedHoldingsUpdate?.(stockName, null);
                }
            }
        };

        loadTradingSummary();
        return () => {
            cancelled = true;
        };
    }, [stockName, investmentStyle, initialInvestment, userCreatedAt, userId, stockSupported, onSimulatedHoldingsUpdate]);

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
                aiSupported={aiDataSupported}
                tradingSupported={tradingDataSupported}
            />

            <IndicatorModal indicator={selectedIndicator} onClose={() => setSelectedIndicator(null)} />
        </div>
    );
}
