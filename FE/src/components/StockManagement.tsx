import Header from "@/components/layout/Header";
import StockCard from "@/components/StockCard";

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
                                stocks.map((stock) => {
                                    const evaluationValue = Math.round((stock.quantity ?? 0) * (stock.averagePrice ?? 0));
                                    const profit = (stock.totalValue ?? 0) - evaluationValue;
                                    const profitRate =
                                        evaluationValue > 0 ? (profit / evaluationValue) * 100 : 0;
                                    const profitInfo = formatProfitText(profit, profitRate);
                                    return (
                                        <StockCard
                                            key={stock.name}
                                            name={stock.name}
                                            quantity={stock.quantity}
                                            averagePrice={stock.averagePrice}
                                            logoUrl={stock.logoUrl}
                                            profitText={profitInfo.text}
                                            profitColor={profitInfo.color}
                                            onClick={() => onSelectStock?.(stock.name)}
                                        />
                                    );
                                })
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
