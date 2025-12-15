import LogoIcon from "@/assets/icons/Logo.svg?react";
import samsungLogo from "@/assets/logos/samsunglogo.png";
import skLogo from "@/assets/logos/sklogo.png";
import { isStockSupported } from "@/utils/aiTradingSummary";

interface StockCardProps {
    name: string;
    quantity: number;
    averagePrice: number;
    logoUrl?: string;
    profitText: string;
    profitColor: string;
    onClick?: () => void;
}

const formatNumber = (value: number) => value.toLocaleString();

const PREDEFINED_LOGOS: Record<string, string> = {
    삼성전자: samsungLogo,
    "SK하이닉스": skLogo,
};

function StockLogo({ name, logoUrl }: { name: string; logoUrl?: string }) {
    const resolvedLogo = logoUrl || PREDEFINED_LOGOS[name];
    if (resolvedLogo) {
        return (
            <div
                className="overflow-hidden bg-white"
                style={{ width: "46px", height: "46px", borderRadius: "100px" }}
            >
                <img src={resolvedLogo} alt={`${name} 로고`} className="size-full object-cover" loading="lazy" />
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

export default function StockCard({
    name,
    quantity,
    averagePrice,
    logoUrl,
    profitText,
    profitColor,
    onClick,
}: StockCardProps) {
    const evaluationValue = Math.round((quantity ?? 0) * (averagePrice ?? 0));
    const supported = isStockSupported(name);
    const displayProfitText = supported ? profitText : "지원되지 않습니다";
    const displayProfitColor = supported ? profitColor : "var(--achromatic-400)";

    return (
        <button
            type="button"
            onClick={onClick}
            className="w-full rounded-[16px] bg-[#f2f4f8] text-left transition-transform hover:scale-[0.995]"
        >
            <div className="flex items-start justify-between" style={{ padding: "16px 20px" }}>
                <div className="flex items-center gap-[12px]">
                    <StockLogo name={name} logoUrl={logoUrl} />
                    <div className="flex flex-col">
                        <span className="title-3 text-[#151b26]">{name}</span>
                        <span className="body-3 text-[#a1a4a8]">{quantity}주</span>
                    </div>
                </div>
                <div className="flex flex-col items-end text-right">
                    <p className="title-3 text-[#444951]" style={{ fontWeight: 700 }}>
                        {formatNumber(evaluationValue)}원
                    </p>
                    <p className="body-3" style={{ color: displayProfitColor, fontWeight: 500 }}>
                        {displayProfitText}
                    </p>
                </div>
            </div>
        </button>
    );
}
