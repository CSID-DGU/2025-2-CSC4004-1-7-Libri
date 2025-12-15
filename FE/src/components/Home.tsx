import { useMemo, useState, useEffect, useCallback } from "react";
import SettingsIcon from "@/assets/icons/settings.svg?react";
import AiSparkIcon from "@/assets/icons/AI.svg?react";
import PlusIcon from "@/assets/icons/plus.svg?react";
import LogoIcon from "@/assets/icons/Logo.svg?react";
import samsungLogo from "@/assets/logos/samsunglogo.png";
import skLogo from "@/assets/logos/sklogo.png";
import StockDetail, { type TradingSummary } from "./StockDetail";
import { api } from "@/api/client";
import { mapSymbolToDisplayName, resolveStockSymbol } from "@/lib/stocks";
import {
    generateMockPriceSeries,
    generateRandomActions,
    simulateTradingHistory,
} from "@/utils/aiTradingSimulation";

interface Stock {
    name: string;
    quantity: number;
    averagePrice: number;
    totalValue: number;
    logoUrl?: string;
}

interface StockPerformance {
    profit: number;
    profitRate: number;
    latestPrice?: number;
}

type StockPerformanceMap = Record<string, StockPerformance>;

interface HomeProps {
    initialInvestment: number;
    stocks: Stock[];
    onAddStock: () => void;
    investmentStyle: "공격형" | "안정형";
    onOpenSettings: () => void;
    userId?: number | null;
}

const formatNumber = (value: number) => value.toLocaleString();

const formatProfitText = (profit: number, profitRate: number, zeroColor = "var(--component-main)") => {
        if (profit === 0 && profitRate === 0) {
            return {
                text: `0 (0%)`,
                color: zeroColor,
            };
        }
        const positive = profit >= 0;
        const sign = positive ? "+" : "";
        return {
            text: `${sign}${formatNumber(profit)} (${sign}${profitRate.toFixed(1)}%)`,
            color: positive ? "#f3646f" : "#2563eb",
        };
    };

function HomeHeader({ onOpenSettings }: { onOpenSettings: () => void }) {
    return (
        <header
            className="flex w-full items-center justify-between"
            style={{ paddingInline: "20px", paddingBlock: "13px" }}
        >
            <div className="flex items-center gap-[8px]">
                <div className="size-[28px] text-achromatic-600">
                    <LogoIcon />
                </div>
                <span className="home-title text-[#3e3f40] flex items-center leading-none">
                    리브리
                </span>
            </div>
            <button
                type="button"
                onClick={onOpenSettings}
                aria-label="설정 이동"
                className="size-6 flex items-center justify-center"
            >
                <SettingsIcon style={{ color: "var(--achromatic-600)" }} className="w-6 h-6" />
            </button>
        </header>
    );
}

function InvestmentState({
    initialInvestment,
    aiTradeProfit,
    aiTradeProfitRate,
}: {
    initialInvestment: number;
    aiTradeProfit: number;
    aiTradeProfitRate: number;
}) {
    const aiProfitInfo = formatProfitText(aiTradeProfit, aiTradeProfitRate);
    return (
        <section className="flex flex-col gap-[10px] rounded-[16px] bg-[rgba(31,169,164,0.08)] p-[20px]">
            <div className="flex items-center gap-[4px] text-[#1fa9a4]">
                <div className="flex items-center justify-center">
                    <AiSparkIcon width={18} height={18} />
                </div>
                <span className="title-3 tracking-[0.16px]">
                    AI 투자 현황
                </span>
            </div>

            <div className="flex flex-col text-[16px] tracking-[0.16px] text-[#151b26]">
                <p className="body-1">
                    리브리가{" "}
                    <span className="body-1 text-[#1fa9a4]" style={{ fontWeight: 700 }}>
                        {formatNumber(initialInvestment)}
                    </span>
                    으로{" "}
                </p>
                <p className="body-1">
                    총 수익률{" "}
                    <span className="body-1" style={{ color: aiProfitInfo.color, fontWeight: 700 }}>
                        {aiProfitInfo.text}
                    </span>
                    을 내고 있어요.
                </p>
            </div>

            <p className="label-3 tracking-[0.22px] text-[#b9bbbe]">
                *실제 투자 환경 데이터 기반, AI가 시뮬레이션한 수익률입니다.
            </p>
        </section>
    );
}

function StockLogo({ name, logoUrl }: { name: string; logoUrl?: string }) {
    if (logoUrl) {
        return (
            <div
                className="overflow-hidden"
                style={{ width: "46px", height: "46px", borderRadius: "100px" }}
            >
                <img src={logoUrl} alt={`${name} 로고`} className="size-full object-cover" loading="lazy" />
            </div>
        );
    }

    const predefinedLogos: Record<string, string> = {
        삼성전자: samsungLogo,
        "SK하이닉스": skLogo,
    };

    const matchedLogo = predefinedLogos[name];

    if (matchedLogo) {
        return (
            <div
                className="overflow-hidden bg-white"
                style={{ width: "46px", height: "46px", borderRadius: "100px" }}
            >
                <img src={matchedLogo} alt={`${name} 로고`} className="size-full object-cover" loading="lazy" />
            </div>
        );
    }

    return (
        <div
            className="flex items-center justify-center bg-white text-achromatic-600"
            style={{ width: "46px", height: "46px", borderRadius: "100px" }}
        >
            <LogoIcon className="size-6" />
        </div>
    );
}

function StockCard({
    stock,
    onClick,
    aiProfit,
    aiProfitRate,
    latestPrice,
}: {
    stock: Stock;
    onClick: (stockName: string) => void;
    aiProfit: number;
    aiProfitRate: number;
    latestPrice?: number;
}) {
    const { text, color } = formatProfitText(aiProfit, aiProfitRate);
    const displayValue = latestPrice !== undefined
        ? Math.round((stock.quantity ?? 0) * latestPrice)
        : stock.totalValue;

    return (
        <button
            type="button"
            onClick={() => onClick(stock.name)}
            className="w-full rounded-[16px] bg-[#f2f4f8] text-left transition-transform hover:scale-[0.995]"
        >
            <div className="flex items-start justify-between" style={{ padding: "16px 20px" }}>
                <div className="flex items-center gap-[12px]">
                    <StockLogo name={stock.name} logoUrl={stock.logoUrl} />
                    <div className="flex flex-col">
                        <span className="title-3 text-[#151b26]">
                            {stock.name}
                        </span>
                        <span className="body-3 text-[#a1a4a8]">
                            {stock.quantity}주
                        </span>
                    </div>
                </div>
                <div className="flex flex-col items-end text-right">
                    <p className="title-3 text-[#444951]" style={{ fontWeight: 700 }}>
                        {formatNumber(displayValue)}원
                    </p>
                    <p
                        className="body-3 "
                        style={{ color, fontWeight: 500 }}
                    >
                        {text}
                    </p>
                </div>
            </div>
        </button>
    );
}

function StockList({
    stocks,
    onStockClick,
    stockPerformance,
}: {
    stocks: Stock[];
    onStockClick: (stock: string) => void;
    stockPerformance: StockPerformanceMap;
}) {
    if (!stocks.length) {
        return (
            <div className="w-full rounded-2xl bg-[#f2f4f8] py-8 text-center text-[#a1a4a8]">
                아직 추가된 종목이 없습니다.
            </div>
        );
    }

    return (
        <div className="flex w-full flex-col gap-[12px]">
            {stocks.map((stock) => (
                            <StockCard
                                key={stock.name}
                                stock={stock}
                                onClick={onStockClick}
                                aiProfit={stockPerformance[stock.name]?.profit ?? 0}
                                aiProfitRate={stockPerformance[stock.name]?.profitRate ?? 0}
                                latestPrice={stockPerformance[stock.name]?.latestPrice}
                            />
                        ))}
        </div>
    );
}

function AddStockButton({ onAddStock }: { onAddStock: () => void }) {
    return (
        <button
            type="button"
            onClick={onAddStock}
            className="flex w-full items-center justify-center gap-1 rounded-[8px] bg-[#1fa9a4] text-white"
            style={{ paddingBlock: "12px", columnGap: "4px" }}
        >
            <span className="text-white flex items-center justify-center">
                <PlusIcon width={20} height={20} />
            </span>
            <span className="flex items-center title-3 tracking-[0.16px] leading-none">
                종목 추가
            </span>
        </button>
    );
}

function StockSection({
    stocks,
    onAddStock,
    onStockClick,
    stockPerformance,
}: {
    stocks: Stock[];
    onAddStock: () => void;
    onStockClick: (stock: string) => void;
    stockPerformance: StockPerformanceMap;
}) {
    return (
        <section className="flex flex-col mt-[28px]">
            <h2 className="title-3 tracking-[0.16px] text-[#151b26]" style={{ margin: 0, marginBottom: "10px" }}>
                내 종목</h2>
            <div className="mt-[10px] flex flex-col">
                <div style={{ marginBottom: "12px" }}>
                    <StockList
                        stocks={stocks}
                        onStockClick={onStockClick}
                        stockPerformance={stockPerformance}
                    />
                </div>
                <AddStockButton onAddStock={onAddStock} />
            </div>
        </section>
    );
}

function HomeContent({
    initialInvestment,
    aiTradeProfit,
    aiTradeProfitRate,
    stocks,
    onAddStock,
    onStockClick,
    onOpenSettings,
    stockPerformance,
    isBackendConnected,
}: {
    initialInvestment: number;
    aiTradeProfit: number;
    aiTradeProfitRate: number;
    stocks: Stock[];
    onAddStock: () => void;
    onStockClick: (stock: string) => void;
    onOpenSettings: () => void;
    stockPerformance: StockPerformanceMap;
    isBackendConnected: boolean;
}) {
    return (
        <div className="absolute content-stretch flex flex-col gap-[12px] items-start left-1/2 top-[52px] translate-x-[-50%] w-full max-w-[375px] pb-16">
            <div className="w-full px-5">
                <HomeHeader onOpenSettings={onOpenSettings} />
            </div>
            <div className="flex w-full flex-col">
                <div className="w-full" style={{ paddingInline: "20px", marginBottom: "28px" }}>
                    <InvestmentState
                        initialInvestment={initialInvestment}
                        aiTradeProfit={aiTradeProfit}
                        aiTradeProfitRate={aiTradeProfitRate}
                    />
                </div>
                {!isBackendConnected && (
                    <div className="w-full" style={{ paddingInline: "20px", marginBottom: "20px" }}>
                        <div className="rounded-[12px] bg-[#fff3cd] border border-[#ffeaa7] p-3">
                            <p className="body-3 text-[#856404] mb-2">
                                ⚠️ 백엔드 서버에 연결할 수 없어 Mock 데이터를 표시하고 있습니다.
                            </p>
                            <p className="body-3 text-[#856404] text-xs">
                                실제 데이터를 보려면 백엔드 서버를 실행해주세요:<br/>
                                <code className="bg-[#f8f9fa] px-1 rounded">cd BE && uvicorn app.main:app --reload --port 8000</code>
                            </p>
                        </div>
                    </div>
                )}
                <div className="w-full" style={{ paddingInline: "20px" }}>
                    <StockSection
                        stocks={stocks}
                        onAddStock={onAddStock}
                        onStockClick={onStockClick}
                        stockPerformance={stockPerformance}
                    />
                </div>
            </div>
        </div>
    );
}

export default function Home({
    initialInvestment,
    stocks,
    onAddStock,
    investmentStyle,
    onOpenSettings,
    userId,
}: HomeProps) {
    const [currentView, setCurrentView] = useState<"list" | "detail">("list");
    const [selectedStockName, setSelectedStockName] = useState("");
    const [stockPerformance, setStockPerformance] = useState<StockPerformanceMap>({});
    const [portfolioStocks, setPortfolioStocks] = useState<Stock[]>([]);
    const [portfolioInitialInvestment, setPortfolioInitialInvestment] = useState<number | null>(null);
    const [isBackendConnected, setIsBackendConnected] = useState(true);
    const [simulatedHoldings, setSimulatedHoldings] = useState<Record<string, TradingSummary>>({});
    const handleSimulatedHoldingsUpdate = useCallback((stockName: string, summary: TradingSummary | null) => {
        setSimulatedHoldings((prev) => {
            const next = { ...prev };
            if (!summary || (summary.netShares === 0 && summary.realizedProfit === 0 && summary.positionValue === 0)) {
                delete next[stockName];
            } else {
                next[stockName] = summary;
            }
            return next;
        });
    }, []);

    useEffect(() => {
        if (!userId) return;
        let cancelled = false;

        const loadPortfolio = async () => {
            try {
                const portfolio = await api.getPortfolio(userId);
                if (cancelled || !portfolio) return;

                const mappedStocks: Stock[] = (portfolio.holdings || []).map((holding: any) => {
                    const displayName = mapSymbolToDisplayName(holding.symbol) || holding.symbol || "알 수 없음";
                    const quantity = holding.quantity ?? 0;
                    const averagePrice = holding.avg_price ?? 0;
                    const currentPrice = holding.current_price ?? holding.avg_price ?? 0;

                    return {
                        name: displayName,
                        quantity,
                        averagePrice,
                        totalValue: currentPrice * quantity,
                        logoUrl: undefined,
                    };
                });

                setPortfolioStocks(mappedStocks);
                if (typeof portfolio.initial_capital === "number") {
                    setPortfolioInitialInvestment(portfolio.initial_capital);
                } else if (typeof portfolio.total_asset === "number") {
                    setPortfolioInitialInvestment(portfolio.total_asset);
                } else if (typeof portfolio.current_capital === "number") {
                    setPortfolioInitialInvestment(portfolio.current_capital);
                } else {
                    setPortfolioInitialInvestment(null);
                }
            } catch (error) {
                console.error("포트폴리오 정보를 불러오지 못했습니다:", error);
            } finally {
                if (cancelled) {
                    return;
                }
            }
        };

        loadPortfolio();

        return () => {
            cancelled = true;
        };
    }, [userId]);

    const effectiveStocks = stocks;
    const [adjustedStocks, summaryStockName] = useMemo(() => {
        const adjusted = effectiveStocks.map((stock) => {
            const summary = simulatedHoldings[stock.name];
            if (!summary) {
                return stock;
            }
            const baseQuantity = stock.quantity ?? 0;
            const adjustedQuantity = baseQuantity + summary.netShares;
            const unitPrice = summary.lastTradePrice ?? summary.averagePrice ?? stock.averagePrice ?? 0;
            const totalValue = Math.max(adjustedQuantity, 0) * unitPrice;
            return {
                ...stock,
                quantity: Math.max(adjustedQuantity, 0),
                averagePrice: unitPrice,
                totalValue,
            };
        });
        const firstName = adjusted[0]?.name || "삼성전자";
        return [adjusted, firstName] as const;
    }, [effectiveStocks, simulatedHoldings]);
    const effectiveInitialInvestment = (() => {
        if (typeof portfolioInitialInvestment === "number" && !Number.isNaN(portfolioInitialInvestment)) {
            return portfolioInitialInvestment;
        }
        const parsed = Number(initialInvestment);
        return Number.isNaN(parsed) ? 0 : parsed;
    })();
    
    // Mock 데이터 생성 함수 (백엔드 연결 실패 시 사용)
    const generateMockPerformance = useMemo(() => {
        return (stockName: string) => {
            const priceSeries = generateMockPriceSeries(stockName);
            const actions = generateRandomActions(stockName, priceSeries.length || 5);
            const { totalProfit } = simulateTradingHistory(
                effectiveInitialInvestment,
                priceSeries,
                actions,
            );
            const profitRate =
                effectiveInitialInvestment > 0
                    ? (totalProfit / effectiveInitialInvestment) * 100
                    : 0;
            return { profit: totalProfit, profitRate };
        };
    }, [effectiveInitialInvestment]);

    useEffect(() => {
        const loadStockPerformance = async () => {
            try {
                
                const performanceMap: StockPerformanceMap = {};

                // 각 종목에 대해 AI 거래 내역 기반 수익률 계산
                const targetStocks = adjustedStocks.length > 0
                    ? adjustedStocks
                    : [{ name: summaryStockName, quantity: 0, averagePrice: 0, totalValue: 0 }];
                for (const stock of targetStocks) {
                    try {
                        const symbol = resolveStockSymbol(stock.name) || "005930.KS";
                        
                        // 30일 전부터 데이터 가져오기
                        const stockHistory = await api.getStockHistory(symbol, 30);

                        // 백엔드 연결 성공
                        setIsBackendConnected(true);

                        const latestEntry = [...stockHistory].sort((a: any, b: any) => a.date.localeCompare(b.date)).at(-1);
                        const latestClose = latestEntry?.close ?? 0;
                        const quantity = stock.quantity ?? 0;
                        const averagePrice = stock.averagePrice ?? 0;
                        let profit = 0;
                        let profitRate = 0;
                        if (quantity > 0 && averagePrice > 0) {
                            profit = (latestClose - averagePrice) * quantity;
                            profitRate = ((latestClose - averagePrice) / averagePrice) * 100;
                        }
                        
                        performanceMap[stock.name] = { 
                            profit, 
                            profitRate,
                            latestPrice: latestClose,
                        };
                    } catch (error) {
                        console.warn(`${stock.name} 데이터 로딩 실패, Mock 데이터 사용:`, error);
                        setIsBackendConnected(false);
                        const mock = generateMockPerformance(stock.name);
                        performanceMap[stock.name] = {
                            ...mock,
                            latestPrice: stock.averagePrice ?? 0,
                        };
                    }
                }

                setStockPerformance(performanceMap);
            } catch (error) {
                console.error("주식 성과 데이터 로딩 실패, Mock 데이터 사용:", error);
                // 전체 실패 시 Mock 데이터 사용
                const mockPerformance: StockPerformanceMap = {};
                const stockList = adjustedStocks.length > 0 ? adjustedStocks : [{ name: summaryStockName, quantity: 0, averagePrice: 0, totalValue: 0 }];
                stockList.forEach(stock => {
                    const basePerformance = generateMockPerformance(stock.name);
                    const simulated = simulatedHoldings[stock.name];
                    if (simulated) {
                        mockPerformance[stock.name] = {
                            profit: simulated.realizedProfit,
                            profitRate:
                                effectiveInitialInvestment > 0
                                    ? (simulated.realizedProfit / effectiveInitialInvestment) * 100
                                    : 0,
                        };
                    } else {
                        mockPerformance[stock.name] = basePerformance;
                    }
                });
                setStockPerformance(mockPerformance);
            }
        };

        loadStockPerformance();
    }, [adjustedStocks, summaryStockName, effectiveInitialInvestment, generateMockPerformance, simulatedHoldings]);

    const aiTradeProfit = useMemo(
        () => Object.values(simulatedHoldings).reduce((acc, summary) => acc + (summary?.realizedProfit ?? 0), 0),
        [simulatedHoldings],
    );
    const aiTradeProfitRate =
        effectiveInitialInvestment > 0 ? (aiTradeProfit / effectiveInitialInvestment) * 100 : 0;

    const handleStockClick = (stockName: string) => {
        setSelectedStockName(stockName);
        setCurrentView("detail");
    };

    const handleBackToList = () => {
        setCurrentView("list");
        setSelectedStockName("");
    };

    if (currentView === "detail") {
        return (
            <StockDetail
                stockName={selectedStockName}
                investmentStyle={investmentStyle}
                initialInvestment={effectiveInitialInvestment}
                onBack={handleBackToList}
                onSimulatedHoldingsUpdate={handleSimulatedHoldingsUpdate}
            />
        );
    }

    return (
        <div className="relative min-h-screen w-full bg-white">
            <HomeContent
                initialInvestment={effectiveInitialInvestment}
                aiTradeProfit={aiTradeProfit}
                aiTradeProfitRate={aiTradeProfitRate}
                stocks={adjustedStocks}
                onAddStock={onAddStock}
                onStockClick={handleStockClick}
                onOpenSettings={onOpenSettings}
                stockPerformance={stockPerformance}
                isBackendConnected={isBackendConnected}
            />
        </div>
    );
}
