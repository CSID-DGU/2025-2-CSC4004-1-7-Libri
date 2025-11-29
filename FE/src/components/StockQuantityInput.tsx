import { useState } from "react";
import Header from "@/components/layout/Header";
import CloseCircleIcon from "@/assets/icons/close-circle.svg?react";

interface IntroSectionProps {
    stockName: string;
}

function IntroSection({ stockName }: IntroSectionProps) {
    return (
        <div className="flex flex-col px-5 text-nowrap">
            <div className="title-1 onboarding-big">
                <p className="leading-[1.6] whitespace-pre">보유 중인 개수를 입력해 주세요</p>
            </div>
            <div className="h-[2px]" />
            <div className="body-3 tracking-[0.24px] text-[#a1a4a8]">
                <p className="leading-[1.5] whitespace-pre">
                    보유 중이지 않아도 AI 분석 결과를 확인할 수 있어요.
                </p>
            </div>
        </div>
    );
}

interface StockQuantityInputProps {
    stockName: string;
    onBack?: () => void;
    onSubmit: (quantity: string) => void;
}

export default function StockQuantityInput({
    stockName,
    onBack,
    onSubmit,
}: StockQuantityInputProps) {
    const [quantity, setQuantity] = useState("");

    const hasValue = quantity.trim().length > 0;

    const handleQuantityChange = (value: string) => {
        const numericValue = value.replace(/[^\d]/g, "");
        setQuantity(numericValue);
    };

    const handleSubmit = () => {
        if (hasValue) {
            onSubmit(quantity.trim());
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
                    <IntroSection stockName={stockName} />

                    <div className="px-5">
                        <div className="flex items-center" style={{ gap: "10px" }}>
                            <div className="relative w-full">
                                <input
                                    type="text"
                                    inputMode="numeric"
                                    pattern="[0-9]*"
                                    value={quantity}
                                    onChange={(e) => handleQuantityChange(e.target.value)}
                                    onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
                                    placeholder="보유 개수"
                                    className="w-full rounded-[8px] label-1 text-achromatic-800 tracking-[0.14px] outline-none placeholder-body-2 placeholder-achromatic-500 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                                    style={{
                                        paddingInline: "12px",
                                        paddingBlock: "12px",
                                        paddingRight: "40px",
                                        backgroundColor: "var(--component-background)",
                                    }}
                                />
                                {hasValue && (
                                    <button
                                        type="button"
                                        onClick={() => setQuantity("")}
                                        aria-label="입력 내용 지우기"
                                        className="flex items-center justify-center"
                                        style={{
                                            position: "absolute",
                                            top: "50%",
                                            right: "8px",
                                            transform: "translateY(-50%)",
                                        }}
                                    >
                                        <CloseCircleIcon
                                            className="w-5 h-5"
                                            style={{ color: "var(--achromatic-500)" }}
                                        />
                                    </button>
                                )}
                            </div>
                            <span className="title-1 text-achromatic-800">주</span>
                        </div>
                    </div>
                </div>
            </div>

            <div className="absolute bottom-[50px] box-border content-stretch flex flex-col gap-[10px] items-start left-1/2 translate-x-[-50%] px-[20px] py-0 w-full max-w-[375px]">
                <button
                    onClick={handleSubmit}
                    disabled={!hasValue}
                    className={`${
                        hasValue ? "bg-[#1FA9A4]" : "bg-[#d0d1d4]"
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
