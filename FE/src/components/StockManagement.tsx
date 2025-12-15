import Header from "@/components/layout/Header";
import LogoIcon from "@/assets/icons/Logo.svg?react";
import samsungLogo from "@/assets/logos/samsunglogo.png";
import skLogo from "@/assets/logos/sklogo.png";

export interface ManagedStock {
    name: string;
    quantity: number;
    averagePrice: number;
    totalValue: number;
    logoUrl?: string;
}

interface StockManagementProps {
    stocks: ManagedStock[];
    onBack?: () => void;
    onSelectStock?: (stockName: string) => void;
}

const formatNumber = (value: number) => value.toLocaleString();

const formatProfitText = (profit: number, profitRate: number) => {
    if (profit === 0 && profitRate === 0) {
        return {
            text: `0 (0%)`,
            color: "var(--component-main)",
        };
    }
    const positive = profit >= 0;
    const sign = positive ? "+" : "";
    return {
        text: `${sign}${formatNumber(profit)} (${sign}${profitRate.toFixed(1)}%)`,
        color: positive ? "#f3646f" : "#2563eb",
    };
};

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
    onSelectStock,
}: {
    stock: ManagedStock;
    onSelectStock?: (stockName: string) => void;
}) {
    const investedAmount = (stock.quantity ?? 0) * (stock.averagePrice ?? 0);
    const profit = (stock.totalValue ?? 0) - investedAmount;
    const profitRate = investedAmount > 0 ? (profit / investedAmount) * 100 : 0;
    const { text, color } = formatProfitText(profit, profitRate);

    return (
        <button
            type="button"
            onClick={() => onSelectStock?.(stock.name)}
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
                        {formatNumber(stock.totalValue ?? 0)}원
                    </p>
                    <p
                        className="body-3"
                        style={{ color, fontWeight: 500 }}
                    >
                        {text}
                    </p>
                </div>
            </div>
        </button>
    );
}

export default function StockManagement({ stocks, onBack, onSelectStock }: StockManagementProps) {
    return (
        <div className="bg-white relative size-full min-h-screen" data-name="종목 관리">
            <div className="absolute content-stretch flex flex-col items-start left-1/2 top-[52px] translate-x-[-50%] w-full max-w-[375px]">
                <Header title="종목 관리" onBack={onBack} />

                <div
                    className="flex w-full flex-col px-0 py-4"
                    style={{ gap: "24px", marginTop: "16px", paddingInline: "20px" }}
                >
                    <section className="flex flex-col px-5" style={{ gap: "12px" }}>
                        <p
                            className="body-3 tracking-[0.14px]"
                            style={{ color: "var(--achromatic-500)" }}
                        >
                            내 종목
                        </p>
                        <div className="flex flex-col" style={{ gap: "12px" }}>
                            {stocks.length > 0 ? (
                                stocks.map((stock) => (
                                    <StockCard
                                        key={stock.name}
                                        stock={stock}
                                        onSelectStock={onSelectStock}
                                    />
                                ))
                            ) : (
                                <div className="w-full rounded-2xl bg-[#f2f4f8] py-8 text-center text-[#a1a4a8]">
                                    아직 추가된 종목이 없습니다.
                                </div>
                            )}
                        </div>
                    </section>
                </div>
            </div>
        </div>
    );
}
