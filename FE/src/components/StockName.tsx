import { useState } from "react";
import Header from "@/components/layout/Header";
import CloseCircleIcon from "@/assets/icons/close-circle.svg?react";

function IntroSection() {
    return (
        <div className="flex flex-col px-5 text-nowrap">
            <div className="title-1 onboarding-big">
                <p className="leading-[1.6] whitespace-pre">주식 종목을 입력해 주세요</p>
            </div>
            <div className="h-[2px]" />
            <div className="body-3 tracking-[0.24px] text-[#a1a4a8]">
                <p className="leading-[1.5] whitespace-pre">
                    AI 주식 분석을 확인하고 싶은 종목을 추가해 주세요.
                </p>
            </div>
        </div>
    );
}

interface StockNameProps {
    onSubmit: (stockName: string) => void;
    onBack?: () => void;
}

export default function StockNameScreen({ onSubmit, onBack }: StockNameProps) {
    const [stockInput, setStockInput] = useState("");

    const handleSubmit = () => {
        if (stockInput.trim()) {
            onSubmit(stockInput.trim());
        }
    };

    const hasValue = stockInput.trim().length > 0;

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
                        <div className="relative">
                            <input
                                type="text"
                                value={stockInput}
                                onChange={(e) => setStockInput(e.target.value)}
                                onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
                                placeholder="주식 종목명"
                                className="w-full rounded-[8px] label-1 text-achromatic-800 tracking-[0.14px] outline-none placeholder-body-2 placeholder-achromatic-500"
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
                                    onClick={() => setStockInput("")}
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
                    </div>
                </div>
            </div>

            <div className="absolute bottom-[50px] box-border content-stretch flex flex-col gap-[10px] items-start left-1/2 translate-x-[-50%] px-[20px] py-0 w-full max-w-[375px]">
                <button
                    onClick={handleSubmit}
                    disabled={!stockInput.trim()}
                    className={`${
                        stockInput.trim() ? "bg-[#1FA9A4]" : "bg-[#d0d1d4]"
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
