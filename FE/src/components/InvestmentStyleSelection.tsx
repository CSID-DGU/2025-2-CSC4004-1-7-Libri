import { useState } from "react";
import { default as CaretLeftIcon } from "@/assets/icons/caret-left.svg?react";
import { default as LightningIcon } from "@/assets/icons/lightning.svg?react";
import { default as ShieldIcon } from "@/assets/icons/shield.svg?react";

function CaretLeft() {
    return (
        <div className="relative shrink-0 size-[24px]" data-name="caret-left">
            <CaretLeftIcon style={{ color: "var(--achromatic-600)" }} />
        </div>
    );
}

function Component() {
    return (
        <div
            className="box-border content-stretch flex gap-[10px] items-center p-[4px] relative shrink-0"
            data-name="상단 헤더 좌측 버튼"
        >
            <CaretLeft />
        </div>
    );
}

function Frame5({ onBack }: { onBack: () => void }) {
    return (
        <button
            onClick={onBack}
            className="content-stretch flex gap-[10px] items-center relative shrink-0 w-[68px]"
        >
            <Component />
        </button>
    );
}

function Component1() {
    return (
        <div className="basis-0 grow min-h-px min-w-px relative shrink-0" data-name="헤더 타이틀">
            <div className="flex flex-row items-center justify-center size-full">
                <div className="box-border content-stretch flex gap-[10px] items-center justify-center px-[4px] py-[2px] relative w-full">
                    <div className="basis-0 flex flex-col grow justify-center leading-[0] min-h-px min-w-px not-italic overflow-ellipsis overflow-hidden relative shrink-0 text-[#3e3f40] text-center text-nowrap onboarding-top">
                        <p className="[white-space-collapse:collapse] leading-[1.55] overflow-ellipsis overflow-hidden">
                            시작하기
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

function Component2() {
    return <div className="h-[32px] shrink-0 w-[68px]" data-name="상단 헤더 우측 버튼" />;
}

function Frame6({ onBack }: { onBack: () => void }) {
    return (
        <div className="absolute content-stretch flex items-center justify-center left-[16px] right-[16px] top-1/2 translate-y-[-50%]">
            <Frame5 onBack={onBack} />
            <Component1 />
            <Component2 />
        </div>
    );
}

function Component3({ onBack }: { onBack: () => void }) {
    return (
        <div className="bg-white h-[58px] relative shrink-0 w-full" data-name="상단 헤더">
            <Frame6 onBack={onBack} />
        </div>
    );
}

function Frame7() {
    return (
        <div className="content-stretch flex flex-col gap-[4px] items-start justify-center leading-[0] not-italic relative shrink-0 text-nowrap w-full">
            <div className="flex flex-col justify-center relative shrink-0 text-[#151b26] onboarding-big">
                <p className="leading-[1.6] text-nowrap whitespace-pre">
                    투자 성향을 선택해 주세요
                </p>
            </div>
            <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center relative shrink-0 text-[#a1a4a8] text-[12px] tracking-[0.24px]">
                <p className="leading-[1.5] text-nowrap whitespace-pre">
                    AI가 맞춤형 분석을 제공하는 데에 필요한 정보예요.
                </p>
            </div>
        </div>
    );
}

function Frame8() {
    return (
        <div className="basis-0 content-stretch flex flex-col gap-[2px] grow items-start justify-center min-h-px min-w-px relative shrink-0">
            <Frame7 />
        </div>
    );
}

function Component4() {
    return (
        <div className="relative shrink-0 w-full" data-name="리스트 헤더">
            <div className="flex flex-row items-center justify-center size-full">
                <div className="box-border content-stretch flex gap-[16px] items-center justify-center px-[20px] py-0 relative w-full">
                    <Frame8 />
                </div>
            </div>
        </div>
    );
}

function Lightning({ isSelected }: { isSelected: boolean }) {
    const color = isSelected ? "#1FA9A4" : "#A1A4A8";
    return (
        <div className="relative shrink-0 size-[24px]" data-name="lightning">
            <LightningIcon style={{ color: "var(--achromatic-500)" }} />
        </div>
    );
}

function Frame1({ isSelected }: { isSelected: boolean }) {
    return (
        <div className="content-stretch flex flex-col gap-[2px] items-start leading-[0] not-italic relative shrink-0 text-center text-nowrap">
            <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center relative shrink-0 text-[#151b26] text-[16px] tracking-[0.16px]">
                <p className="leading-[1.5] text-nowrap whitespace-pre">공격형</p>
            </div>
            <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center relative shrink-0 text-[#a1a4a8] text-[12px] tracking-[0.24px]">
                <p className="leading-[1.5] text-nowrap whitespace-pre">
                    높은 리스크, 높은 수익 추구형
                </p>
            </div>
        </div>
    );
}

function AggressiveOption({ isSelected, onClick }: { isSelected: boolean; onClick: () => void }) {
    return (
        <button
            onClick={onClick}
            className={`${
                isSelected
                    ? "bg-[#E6F7F6] border-2 border-[#1FA9A4]"
                    : "bg-[#f2f4f8] border-2 border-transparent"
            } relative rounded-[16px] shrink-0 w-full transition-all`}
        >
            <div className="flex flex-row items-center overflow-clip rounded-[inherit] size-full">
                <div className="box-border content-stretch flex gap-[12px] items-center px-[20px] py-[16px] relative w-full">
                    <Lightning isSelected={isSelected} />
                    <Frame1 isSelected={isSelected} />
                </div>
            </div>
        </button>
    );
}

function Shield({ isSelected }: { isSelected: boolean }) {
    const opacity = isSelected ? "opacity-100" : "opacity-60";
    return (
        <div className="relative shrink-0 size-[24px]" data-name="shield">
            <ShieldIcon style={{ color: "var(--achromatic-500)" }} />
        </div>
    );
}

function Frame3({ isSelected }: { isSelected: boolean }) {
    return (
        <div className="content-stretch flex flex-col gap-[2px] items-start leading-[0] not-italic relative shrink-0 text-center text-nowrap">
            <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center relative shrink-0 text-[#151b26] text-[16px] tracking-[0.16px]">
                <p className="leading-[1.5] text-nowrap whitespace-pre">안정형</p>
            </div>
            <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center relative shrink-0 text-[#a1a4a8] text-[12px] tracking-[0.24px]">
                <p className="leading-[1.5] text-nowrap whitespace-pre">
                    낮은 리스크, 낮은 수익 추구형
                </p>
            </div>
        </div>
    );
}

function StableOption({ isSelected, onClick }: { isSelected: boolean; onClick: () => void }) {
    return (
        <button
            onClick={onClick}
            className={`${
                isSelected
                    ? "bg-[#E6F7F6] border-2 border-[#1FA9A4]"
                    : "bg-[#f2f4f8] border-2 border-transparent"
            } relative rounded-[16px] shrink-0 w-full transition-all`}
        >
            <div className="flex flex-row items-center overflow-clip rounded-[inherit] size-full">
                <div className="box-border content-stretch flex gap-[12px] items-center px-[20px] py-[16px] relative w-full">
                    <Shield isSelected={isSelected} />
                    <Frame3 isSelected={isSelected} />
                </div>
            </div>
        </button>
    );
}

function Frame4({
    selectedStyle,
    setSelectedStyle,
}: {
    selectedStyle: string | null;
    setSelectedStyle: (style: string) => void;
}) {
    return (
        <div className="relative shrink-0 w-full">
            <div className="size-full">
                <div className="box-border content-stretch flex flex-col gap-[12px] items-start px-[20px] py-0 relative w-full">
                    <AggressiveOption
                        isSelected={selectedStyle === "공격형"}
                        onClick={() => setSelectedStyle("공격형")}
                    />
                    <StableOption
                        isSelected={selectedStyle === "안정형"}
                        onClick={() => setSelectedStyle("안정형")}
                    />
                </div>
            </div>
        </div>
    );
}

function Frame12({
    selectedStyle,
    setSelectedStyle,
}: {
    selectedStyle: string | null;
    setSelectedStyle: (style: string) => void;
}) {
    return (
        <div className="content-stretch flex flex-col gap-[20px] items-start relative shrink-0 w-full">
            <Component4 />
            <Frame4 selectedStyle={selectedStyle} setSelectedStyle={setSelectedStyle} />
        </div>
    );
}

function Frame10({
    selectedStyle,
    setSelectedStyle,
}: {
    selectedStyle: string | null;
    setSelectedStyle: (style: string) => void;
}) {
    return (
        <div className="box-border content-stretch flex flex-col gap-[24px] items-center justify-center px-0 py-[16px] relative shrink-0 w-full">
            <Frame12 selectedStyle={selectedStyle} setSelectedStyle={setSelectedStyle} />
        </div>
    );
}

interface InvestmentStyleSelectionProps {
    onBack: () => void;
    onSubmit: (style: string) => void;
}

export default function InvestmentStyleSelection({
    onBack,
    onSubmit,
}: InvestmentStyleSelectionProps) {
    const [selectedStyle, setSelectedStyle] = useState<string | null>(null);

    const handleSubmit = () => {
        if (selectedStyle) {
            onSubmit(selectedStyle);
        }
    };

    return (
        <div className="bg-white relative size-full min-h-screen" data-name="온보딩">
            <div className="absolute content-stretch flex flex-col items-start left-1/2 top-[52px] translate-x-[-50%] w-full max-w-[375px]">
                <Component3 onBack={onBack} />
                <Frame10 selectedStyle={selectedStyle} setSelectedStyle={setSelectedStyle} />
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
