import { useMemo, useState } from "react";
import SettingsIcon from "@/assets/icons/settings.svg?react";
import AiSparkIcon from "@/assets/icons/AI.svg?react";
import PlusIcon from "@/assets/icons/plus.svg?react";
import LogoIcon from "@/assets/icons/Logo.svg?react";
import samsungLogo from "@/assets/logos/samsunglogo.png";
import skLogo from "@/assets/logos/sklogo.png";
import StockDetail from "./StockDetail";
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

interface HomeProps {
    initialInvestment: number;
    stocks: Stock[];
    onAddStock: () => void;
    investmentStyle: "공격형" | "안정형";
    onOpenSettings: () => void;
}

const formatNumber = (value: number) => value.toLocaleString();

const formatProfitText = (profit: number, profitRate: number) => {
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
                    으로 총 수익률{" "}
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
    initialInvestment,
}: {
    stock: Stock;
    onClick: (stockName: string) => void;
    initialInvestment: number;
}) {
    const { totalProfit: aiProfit } = useMemo(() => {
        const priceSeries = generateMockPriceSeries(stock.name);
        const actions = generateRandomActions(stock.name, priceSeries.length || 5);
        return simulateTradingHistory(initialInvestment, priceSeries, actions);
    }, [stock.name, initialInvestment]);
    const aiProfitRate = initialInvestment > 0 ? (aiProfit / initialInvestment) * 100 : 0;
    const { text, color } = formatProfitText(aiProfit, aiProfitRate);

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
                        {formatNumber(stock.totalValue)}원
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
    initialInvestment,
}: {
    stocks: Stock[];
    onStockClick: (stock: string) => void;
    initialInvestment: number;
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
                    initialInvestment={initialInvestment}
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
    initialInvestment,
}: {
    stocks: Stock[];
    onAddStock: () => void;
    onStockClick: (stock: string) => void;
    initialInvestment: number;
}) {
    return (
        <section className="flex flex-col mt-[28px]">
            <h2 className="title-3 tracking-[0.16px] text-[#151b26]" style={{ margin: 0, marginBottom: "10px" }}>
                종목별 상세</h2>
            <div className="mt-[10px] flex flex-col">
                <div style={{ marginBottom: "12px" }}>
                    <StockList stocks={stocks} onStockClick={onStockClick} initialInvestment={initialInvestment} />
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
}: {
    initialInvestment: number;
    aiTradeProfit: number;
    aiTradeProfitRate: number;
    stocks: Stock[];
    onAddStock: () => void;
    onStockClick: (stock: string) => void;
    onOpenSettings: () => void;
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
                <div className="w-full" style={{ paddingInline: "20px" }}>
                    <StockSection
                        stocks={stocks}
                        onAddStock={onAddStock}
                        onStockClick={onStockClick}
                        initialInvestment={initialInvestment}
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
}: HomeProps) {
    const [currentView, setCurrentView] = useState<"list" | "detail">("list");
    const [selectedStockName, setSelectedStockName] = useState("");

    const summaryStockName = stocks[0]?.name || "삼성전자";
    const { totalProfit: aiTradeProfit } = useMemo(() => {
        const priceSeries = generateMockPriceSeries(summaryStockName);
        const actions = generateRandomActions(summaryStockName, priceSeries.length || 5);
        return simulateTradingHistory(initialInvestment, priceSeries, actions);
    }, [initialInvestment, summaryStockName]);
    const aiTradeProfitRate = initialInvestment > 0 ? (aiTradeProfit / initialInvestment) * 100 : 0;

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
                initialInvestment={initialInvestment}
                onBack={handleBackToList}
            />
        );
    }

    return (
        <div className="relative min-h-screen w-full bg-white">
            <HomeContent
                initialInvestment={initialInvestment}
                aiTradeProfit={aiTradeProfit}
                aiTradeProfitRate={aiTradeProfitRate}
                stocks={stocks}
                onAddStock={onAddStock}
                onStockClick={handleStockClick}
                onOpenSettings={onOpenSettings}
            />
        </div>
    );
}
