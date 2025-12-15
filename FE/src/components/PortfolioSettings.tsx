import { useEffect, useMemo, useState, type ComponentType, type SVGProps } from "react";
import Header from "@/components/layout/Header";
import LightningIcon from "@/assets/icons/lightning.svg?react";
import ShieldIcon from "@/assets/icons/shield.svg?react";
import CloseCircleIcon from "@/assets/icons/close-circle.svg?react";
import { api } from "@/api/client";

interface PortfolioSettingsProps {
    onBack?: () => void;
    onSave?: (data: { investmentAmount: number; investmentStyle: string }) => void | Promise<void>;
    initialInvestmentAmount?: number;
    initialInvestmentStyle?: string;
    userId?: number | null;
}

interface StyleOption {
    id: string;
    label: string;
    description: string;
    Icon: ComponentType<SVGProps<SVGSVGElement>>;
}

const STYLE_OPTIONS: StyleOption[] = [
    {
        id: "공격형",
        label: "공격형",
        description: "높은 리스크, 높은 수익 추구형",
        Icon: LightningIcon,
    },
    {
        id: "안정형",
        label: "안정형",
        description: "낮은 리스크, 낮은 수익 추구형",
        Icon: ShieldIcon,
    },
];

function StyleOptionCard({
    label,
    description,
    Icon,
    selected,
    onSelect,
}: StyleOption & { selected: boolean; onSelect: () => void }) {
    return (
        <button
            type="button"
            onClick={onSelect}
            className="w-full rounded-[16px] text-left transition-all"
            style={{
                paddingInline: "20px",
                paddingBlock: "16px",
                borderWidth: "2px",
                borderStyle: "solid",
                borderColor: selected ? "var(--component-main)" : "transparent",
                backgroundColor: selected ? "rgba(31, 169, 164, 0.08)" : "var(--component-background)",
            }}
        >
            <div className="flex items-center" style={{ gap: "12px" }}>
                <Icon
                    style={{
                        width: "24px",
                        height: "24px",
                        color: selected ? "var(--component-main)" : "var(--achromatic-500)",
                    }}
                />
                <div className="flex flex-col">
                    <span
                        className="title-3 tracking-[0.16px]"
                        style={{ color: selected ? "var(--component-main)" : "var(--achromatic-600)" }}
                    >
                        {label}
                    </span>
                    <span
                        className="body-3 tracking-[0.24px]"
                        style={{ color: selected ? "var(--component-main)" : "var(--achromatic-500)" }}
                    >
                        {description}
                    </span>
                </div>
            </div>
        </button>
    );
}

export default function PortfolioSettings({
    onBack,
    onSave,
    initialInvestmentAmount,
    initialInvestmentStyle,
    userId,
}: PortfolioSettingsProps) {
    const [investmentAmount, setInvestmentAmount] = useState<string>(
        typeof initialInvestmentAmount === "number" ? String(initialInvestmentAmount) : "",
    );
    const [selectedStyle, setSelectedStyle] = useState<string>(initialInvestmentStyle || "");
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (typeof initialInvestmentAmount === "number") {
            setInvestmentAmount(String(initialInvestmentAmount));
        }
    }, [initialInvestmentAmount]);

    useEffect(() => {
        if (initialInvestmentStyle) {
            setSelectedStyle(initialInvestmentStyle);
        }
    }, [initialInvestmentStyle]);

    const parsedInvestmentAmount = useMemo(() => {
        const parsed = Number(investmentAmount.replace(/,/g, ""));
        return Number.isFinite(parsed) && parsed > 0 ? parsed : null;
    }, [investmentAmount]);

    const handleInvestmentChange = (value: string) => {
        const trimmed = value.replace(/[^\d]/g, "");
        setInvestmentAmount(trimmed);
    };

    const handleSubmit = async () => {
        if (!parsedInvestmentAmount || !selectedStyle || !userId || submitting) return;
        setSubmitting(true);
        setError(null);
        try {
            await api.updatePortfolio(userId, {
                initial_investment: parsedInvestmentAmount,
                investment_style: selectedStyle,
            });
            if (onSave) {
                await onSave({ investmentAmount: parsedInvestmentAmount, investmentStyle: selectedStyle });
            }
        } catch (apiError) {
            console.error("포트폴리오 업데이트 실패:", apiError);
            setError("저장에 실패했습니다. 다시 시도해 주세요.");
        } finally {
            setSubmitting(false);
        }
    };

    const saveDisabled = !parsedInvestmentAmount || !selectedStyle || !userId || submitting;

    return (
        <div className="bg-white relative size-full min-h-screen" data-name="포트폴리오 관리">
            <div className="absolute content-stretch flex flex-col items-start left-1/2 top-[52px] translate-x-[-50%] w-full max-w-[375px]">
                <Header title="포트폴리오 관리" onBack={onBack} />

                <div
                    className="flex w-full flex-col px-0 py-4"
                    style={{ gap: "24px", marginTop: "16px", paddingInline: "20px" }}
                >
                    <section className="flex flex-col px-5" style={{ gap: "12px" }}>
                        <label
                            className="body-3 tracking-[0.14px]"
                            style={{ color: "var(--achromatic-500)" }}
                        >
                            투자금
                        </label>
                        <div className="flex items-center" style={{ gap: "10px" }}>
                            <div className="relative w-full">
                                <input
                                    type="text"
                                    inputMode="numeric"
                                    value={investmentAmount}
                                    onChange={(e) => handleInvestmentChange(e.target.value)}
                                    placeholder="예: 1,000,000"
                                    className="w-full rounded-[8px] label-1 text-achromatic-800 tracking-[0.14px] outline-none placeholder-body-2 placeholder-achromatic-500 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                                    style={{
                                        paddingInline: "12px",
                                        paddingBlock: "12px",
                                        paddingRight: "40px",
                                        backgroundColor: "var(--component-background)",
                                    }}
                                />
                                {investmentAmount && (
                                    <button
                                        type="button"
                                        onClick={() => setInvestmentAmount("")}
                                        aria-label="투자금 입력 값 지우기"
                                        className="flex items-center justify-center"
                                        style={{
                                            position: "absolute",
                                            top: "50%",
                                            right: "8px",
                                            transform: "translateY(-50%)",
                                        }}
                                    >
                                        <CloseCircleIcon
                                            style={{
                                                color: "var(--achromatic-500)",
                                                width: "20px",
                                                height: "20px",
                                            }}
                                        />
                                    </button>
                                )}
                            </div>
                            <span
                                className="title-1"
                                style={{ color: "var(--achromatic-500)" }}
                            >
                                원
                            </span>
                        </div>
                    </section>

                    <section className="flex flex-col px-5" style={{ gap: "12px" }}>
                        <p
                            className="body-3 tracking-[0.14px]"
                            style={{ color: "var(--achromatic-500)" }}
                        >
                            투자 성향
                        </p>
                        <div className="flex flex-col" style={{ gap: "12px" }}>
                            {STYLE_OPTIONS.map((option) => (
                                <StyleOptionCard
                                    key={option.id}
                                    {...option}
                                    selected={selectedStyle === option.id}
                                    onSelect={() => setSelectedStyle(option.id)}
                                />
                            ))}
                        </div>
                        {error && (
                            <p className="body-3" style={{ color: "var(--component-red)" }}>
                                {error}
                            </p>
                        )}
                    </section>
                </div>
            </div>

            <div className="absolute bottom-[50px] box-border content-stretch flex flex-col gap-[10px] items-start left-1/2 translate-x-[-50%] px-[20px] py-0 w-full max-w-[375px]">
                <button
                    onClick={handleSubmit}
                    disabled={saveDisabled}
                    className={`${
                        saveDisabled ? "bg-[#d0d1d4]" : "bg-[#1FA9A4]"
                    } relative rounded-[8px] shrink-0 w-full transition-colors`}
                >
                    <div className="flex flex-row items-center justify-center size-full">
                        <div className="box-border content-stretch flex gap-[2px] items-center justify-center px-[8px] py-[12px] relative w-full">
                            <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[16px] text-center text-nowrap text-white tracking-[0.16px]">
                                <p className="leading-[1.5] whitespace-pre">저장</p>
                            </div>
                        </div>
                    </div>
                </button>
            </div>
        </div>
    );
}
