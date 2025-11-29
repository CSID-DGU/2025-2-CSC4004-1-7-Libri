import { useState } from "react";
import { caretLeft } from "@/assets/icons";

function CaretLeft() {
    return (
        <div className="relative shrink-0 size-[24px]" data-name="caret-left">
            <img src={caretLeft} alt="Caret Left" className="block size-full text-[#686B6D]" />
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

function Frame() {
    return (
        <div className="content-stretch flex gap-[10px] items-center relative shrink-0 w-[68px]">
            <Component />
        </div>
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

function Frame1({ onBack }: { onBack: () => void }) {
    return (
        <div className="absolute content-stretch flex items-center justify-center left-[16px] right-[16px] top-1/2 translate-y-[-50%]">
            <button
                onClick={onBack}
                className="content-stretch flex gap-[10px] items-center relative shrink-0 w-[68px]"
            >
                <Component />
            </button>
            <Component1 />
            <Component2 />
        </div>
    );
}

function Component3({ onBack }: { onBack: () => void }) {
    return (
        <div className="bg-white h-[58px] relative shrink-0 w-full" data-name="상단 헤더">
            <Frame1 onBack={onBack} />
        </div>
    );
}

function Frame2() {
    return (
        <div className="content-stretch flex flex-col gap-[4px] items-start justify-center leading-[0] not-italic relative shrink-0 text-nowrap w-full">
            <div className="flex flex-col ustify-center relative shrink-0 text-[#151b26] onboarding-big">
                <p className="leading-[1.6] text-nowrap whitespace-pre">
                    보유 중인 개수를 입력해 주세요
                </p>
            </div>
            <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center relative shrink-0 text-[#a1a4a8] text-[12px] tracking-[0.24px]">
                <p className="leading-[1.5] text-nowrap whitespace-pre">
                    보유 중이지 않은 경우에도 AI의 분석 결과를 받을 수 있어요.
                </p>
            </div>
        </div>
    );
}

function Frame3() {
    return (
        <div className="basis-0 content-stretch flex flex-col gap-[2px] grow items-start justify-center min-h-px min-w-px relative shrink-0">
            <Frame2 />
        </div>
    );
}

function Component4() {
    return (
        <div className="relative shrink-0 w-full" data-name="리스트 헤더">
            <div className="flex flex-row items-center justify-center size-full">
                <div className="box-border content-stretch flex gap-[16px] items-center justify-center px-[20px] py-0 relative w-full">
                    <Frame3 />
                </div>
            </div>
        </div>
    );
}

function Frame6({
    quantity,
    setQuantity,
}: {
    quantity: string;
    setQuantity: (value: string) => void;
}) {
    return (
        <div className="relative shrink-0 w-full">
            <div className="flex flex-row items-center justify-center size-full">
                <div className="box-border content-stretch flex gap-[10px] items-center justify-center px-[20px] py-0 relative w-full">
                    <div className="basis-0 bg-[#f2f4f8] grow min-h-px min-w-px relative rounded-[8px] shrink-0">
                        <div className="flex flex-row items-center size-full">
                            <div className="box-border content-stretch flex items-center p-[12px] relative w-full">
                                <input
                                    type="number"
                                    inputMode="numeric"
                                    pattern="[0-9]*"
                                    value={quantity}
                                    onChange={(e) => setQuantity(e.target.value)}
                                    placeholder="보유 개수"
                                    className="w-full bg-transparent font-['Pretendard:SemiBold',sans-serif] text-[14px] tracking-[0.14px] outline-none placeholder:text-[#a1a4a8] text-[#151b26] [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                                />
                            </div>
                        </div>
                    </div>
                    <div className="flex flex-col justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-center text-nowrap onboarding-big">
                        <p className="leading-[1.6] whitespace-pre">주</p>
                    </div>
                </div>
            </div>
        </div>
    );
}

function Frame8({
    quantity,
    setQuantity,
}: {
    quantity: string;
    setQuantity: (value: string) => void;
}) {
    return (
        <div className="content-stretch flex flex-col gap-[20px] items-start relative shrink-0 w-full">
            <Component4 />
            <Frame6 quantity={quantity} setQuantity={setQuantity} />
        </div>
    );
}

function Frame5({
    quantity,
    setQuantity,
}: {
    quantity: string;
    setQuantity: (value: string) => void;
}) {
    return (
        <div className="box-border content-stretch flex flex-col gap-[24px] items-center justify-center px-0 py-[16px] relative shrink-0 w-full">
            <Frame8 quantity={quantity} setQuantity={setQuantity} />
        </div>
    );
}

interface StockQuantityInputProps {
    stockName: string;
    onBack: () => void;
    onSubmit: (quantity: string) => void;
}

export default function StockQuantityInput({
    stockName,
    onBack,
    onSubmit,
}: StockQuantityInputProps) {
    const [quantity, setQuantity] = useState("");

    const handleSubmit = () => {
        onSubmit(quantity);
    };

    return (
        <div className="bg-white relative size-full min-h-screen" data-name="온보딩">
            <div className="absolute content-stretch flex flex-col items-start left-1/2 top-[52px] translate-x-[-50%] w-full max-w-[375px]">
                <Component3 onBack={onBack} />
                <Frame5 quantity={quantity} setQuantity={setQuantity} />
            </div>

            <div className="absolute bottom-[50px] box-border content-stretch flex flex-col gap-[10px] items-start left-1/2 translate-x-[-50%] px-[20px] py-0 w-full max-w-[375px]">
                <button
                    onClick={handleSubmit}
                    className={`${
                        quantity.trim() ? "bg-[#1FA9A4]" : "bg-[#d0d1d4]"
                    } relative rounded-[8px] shrink-0 w-full transition-colors`}
                >
                    <div className="flex flex-row items-center justify-center size-full">
                        <div className="box-border content-stretch flex gap-[2px] items-center justify-center px-[8px] py-[12px] relative w-full">
                            <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[16px] text-center text-nowrap text-white tracking-[0.16px]">
                                <p className="leading-[1.5] whitespace-pre">다음</p>
                            </div>
                        </div>
                    </div>
                </button>
            </div>
        </div>
    );
}
