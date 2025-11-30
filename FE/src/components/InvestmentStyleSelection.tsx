import { useEffect, useState, type ComponentType, type SVGProps } from "react";
import Header from "@/components/layout/Header";
import LightningIcon from "@/assets/icons/lightning.svg?react";
import ShieldIcon from "@/assets/icons/shield.svg?react";

const ACTIVE_OPTION_BACKGROUND = "rgba(31, 169, 164, 0.2)";

function IntroSection() {
    return (
        <div className="flex flex-col px-5 text-nowrap">
            <div className="title-1 onboarding-big">
                <p className="leading-[1.6] whitespace-pre">투자 성향을 선택해 주세요</p>
            </div>
            <div className="h-[2px]" />
            <div className="body-3 tracking-[0.24px] text-[#a1a4a8]">
                <p className="leading-[1.5] whitespace-pre">
                    두 가지 중 현재 본인에게 가까운 스타일을 골라 주세요.
                </p>
            </div>
        </div>
    );
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

interface OptionCardProps extends StyleOption {
    selected: boolean;
    onSelect: () => void;
}

function OptionCard({ label, description, Icon, selected, onSelect }: OptionCardProps) {
    return (
        <button
            type="button"
            onClick={onSelect}
            aria-pressed={selected}
            className="w-full rounded-[16px] transition-all"
            style={{
                paddingInline: "20px",
                paddingBlock: "16px",
                borderRadius: "16px",
                borderWidth: "2px",
                borderStyle: "solid",
                borderColor: selected ? "var(--component-main)" : "transparent",
                backgroundColor: selected
                    ? ACTIVE_OPTION_BACKGROUND
                    : "var(--component-background)",
            }}
        >
            <div className="flex items-center" style={{ gap: "12px" }}>
                <Icon
                    style={{
                        color: selected ? "var(--component-main)" : "var(--achromatic-500)",
                        width: "24px",
                        height: "24px",
                    }}
                />
                <div className="flex flex-col text-left">
                    <span
                        className="title-3 tracking-[0.16px]"
                        style={{
                            color: selected ? "var(--component-main)" : "var(--achromatic-500)",
                        }}
                    >
                        {label}
                    </span>
                    <span
                        className="body-3 tracking-[0.24px]"
                        style={{
                            color: selected ? "var(--component-main)" : "var(--achromatic-500)",
                        }}
                    >
                        {description}
                    </span>
                </div>
            </div>
        </button>
    );
}

interface InvestmentStyleSelectionProps {
    onBack?: () => void;
    onSubmit: (style: string) => void;
    initialStyle?: string;
    onStyleChange?: (style: string) => void;
}

export default function InvestmentStyleSelection({
    onBack,
    onSubmit,
    initialStyle = "",
    onStyleChange,
}: InvestmentStyleSelectionProps) {
    const [selectedStyle, setSelectedStyle] = useState<string | null>(
        initialStyle || null
    );

    useEffect(() => {
        setSelectedStyle(initialStyle || null);
    }, [initialStyle]);

    const handleSelect = (style: string) => {
        setSelectedStyle(style);
        onStyleChange?.(style);
    };

    const handleSubmit = () => {
        if (selectedStyle) {
            onSubmit(selectedStyle);
        }
    };

    return (
        <div className="bg-white relative size-full min-h-screen" data-name="온보딩">
            <div className="absolute content-stretch flex flex-col items-start left-1/2 top-[52px] translate-x-[-50%] w-full max-w-[375px]">
                <Header title="시작하기" onBack={onBack} />

                <div
                    className="flex w-full flex-col px-0 py-4"
                    style={{ gap: "20px", marginTop: "16px", paddingInline: "20px" }}
                >
                    <IntroSection />

                    <div className="px-5">
                        <div className="flex flex-col" style={{ gap: "12px" }}>
                            {STYLE_OPTIONS.map((option) => (
                                <OptionCard
                                    key={option.id}
                                    {...option}
                                    selected={selectedStyle === option.id}
                                    onSelect={() => handleSelect(option.id)}
                                />
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            <div className="absolute bottom-[50px] box-border content-stretch flex flex-col gap-[10px] items-start left-1/2 translate-x-[-50%] px-[20px] py-0 w-full max-w-[375px]">
                <button
                    onClick={handleSubmit}
                    disabled={!selectedStyle}
                    className={`${
                        selectedStyle ? "bg-[#1FA9A4]" : "bg-[#d0d1d4]"
                    } relative rounded-[8px] shrink-0 w-full transition-colors`}
                >
                    <div className="flex flex-row items-center justify-center size-full">
                        <div className="box-border content-stretch flex gap-[2px] items-center justify-center px-[8px] py-[12px] relative w-full">
                            <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[16px] text-center text-nowrap text-white tracking-[0.16px]">
                                <p className="leading-[1.5] whitespace-pre">완료</p>
                            </div>
                        </div>
                    </div>
                </button>
            </div>
        </div>
    );
}
