import { useEffect, useMemo, useState } from "react";
import Header from "@/components/layout/Header";
import CloseCircleIcon from "@/assets/icons/close-circle.svg?react";
import { api } from "@/api/client";
import { resolveStockSymbol } from "@/lib/stocks";
import type { ManagedStock } from "./StockManagement";

interface StockManagementDetailProps {
    stock?: ManagedStock;
    onBack?: () => void;
    onSave?: (data: { quantity: number; averagePrice: number }) => Promise<void> | void;
    userId?: number | null;
}

export default function StockManagementDetail({
    stock,
    onBack,
    onSave,
    userId,
}: StockManagementDetailProps) {
    const [quantity, setQuantity] = useState<string>(stock?.quantity ? String(stock.quantity) : "");
    const [averagePrice, setAveragePrice] = useState<string>(
        stock?.averagePrice ? String(stock.averagePrice) : "",
    );
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (typeof stock?.quantity === "number") {
            setQuantity(String(stock.quantity));
        }
        if (typeof stock?.averagePrice === "number") {
            setAveragePrice(String(stock.averagePrice));
        }
    }, [stock]);

    const parsedQuantity = useMemo(() => {
        if (quantity === "") return null;
        const parsed = Number(quantity.replace(/[^\d]/g, ""));
        return Number.isFinite(parsed) ? parsed : null;
    }, [quantity]);

    const parsedAveragePrice = useMemo(() => {
        const parsed = Number(averagePrice.replace(/[^\d]/g, ""));
        return Number.isFinite(parsed) && parsed > 0 ? parsed : null;
    }, [averagePrice]);

    const handleSave = async () => {
        if (parsedQuantity === null || parsedAveragePrice === null || submitting) return;
        if (!userId) {
            setError("사용자 정보를 찾을 수 없습니다.");
            return;
        }
        if (!stock) {
            setError("종목 정보를 찾을 수 없습니다.");
            return;
        }

        const symbol = resolveStockSymbol(stock.name);
        if (!symbol) {
            setError("유효한 종목이 아닙니다.");
            return;
        }

        const currentQuantity = stock.quantity ?? 0;
        const currentAveragePrice = stock.averagePrice ?? 0;

        if (parsedQuantity === currentQuantity && parsedAveragePrice === currentAveragePrice) {
            setError("변경된 내용이 없습니다.");
            return;
        }

        const sellStock = async (sellQuantity: number, priceReference: number) => {
            if (sellQuantity <= 0) return;
            await api.sellHolding(userId, {
                symbol,
                quantity: sellQuantity,
                sell_price: priceReference > 0 ? priceReference : 1,
            });
        };

        const buyStock = async (buyQuantity: number, price: number) => {
            if (buyQuantity <= 0) return;
            await api.addHolding(userId, {
                symbol,
                quantity: buyQuantity,
                avg_price: price,
            });
        };

        setSubmitting(true);
        setError(null);
        try {
            if (parsedAveragePrice !== currentAveragePrice) {
                if (currentQuantity > 0) {
                    await sellStock(currentQuantity, parsedAveragePrice);
                }
                if (parsedQuantity > 0) {
                    await buyStock(parsedQuantity, parsedAveragePrice);
                }
            } else {
                const quantityDiff = parsedQuantity - currentQuantity;
                if (quantityDiff > 0) {
                    await buyStock(quantityDiff, currentAveragePrice || parsedAveragePrice);
                } else if (quantityDiff < 0) {
                    await sellStock(Math.abs(quantityDiff), currentAveragePrice || parsedAveragePrice);
                }
            }

            if (onSave) {
                await onSave({ quantity: parsedQuantity, averagePrice: parsedAveragePrice });
            }
            onBack?.();
        } catch (saveError) {
            console.error("종목 정보를 저장하지 못했습니다:", saveError);
            const message =
                saveError instanceof Error
                    ? saveError.message
                    : "저장에 실패했습니다.";
            setError(message);
        } finally {
            setSubmitting(false);
        }
    };

    const saveDisabled =
        parsedQuantity === null ||
        parsedAveragePrice === null ||
        (parsedQuantity === stock?.quantity && parsedAveragePrice === stock?.averagePrice) ||
        submitting;

    const renderEmptyState = () => (
        <div className="flex h-full flex-col items-center justify-center gap-4 px-5 text-center">
            <p className="body-2 text-[#a1a4a8]">선택된 종목이 없습니다.</p>
            <button
                type="button"
                onClick={onBack}
                className="rounded-[8px] bg-[#1fa9a4] px-6 py-2 text-white title-3 tracking-[0.16px]"
            >
                목록으로 돌아가기
            </button>
        </div>
    );

    if (!stock) {
        return (
            <div className="relative min-h-screen w-full bg-white">
                <div className="absolute left-1/2 top-[52px] flex w-full max-w-[375px] -translate-x-1/2 flex-col">
                    <Header title="종목 관리" onBack={onBack} />
                    {renderEmptyState()}
                </div>
            </div>
        );
    }

    return (
        <div className="bg-white relative size-full min-h-screen" data-name="종목 관리 상세">
            <div className="absolute content-stretch flex flex-col items-start left-1/2 top-[52px] translate-x-[-50%] w-full max-w-[375px]">
                <Header title={stock.name} onBack={onBack} />
                <div
                    className="flex w-full flex-col px-0 py-4"
                    style={{ gap: "24px", marginTop: "16px", paddingInline: "20px" }}
                >
                    <section className="flex flex-col px-5" style={{ gap: "12px" }}>
                        <label
                            className="body-3 tracking-[0.14px]"
                            style={{ color: "var(--achromatic-500)" }}
                        >
                            보유 중인 개수
                        </label>
                        <div className="flex items-center" style={{ gap: "10px" }}>
                            <div className="relative w-full">
                                <input
                                    type="text"
                                    inputMode="numeric"
                                    value={quantity}
                                    onChange={(e) => setQuantity(e.target.value.replace(/[^\d]/g, ""))}
                                    placeholder="보유 개수"
                                    className="w-full rounded-[8px] label-1 text-achromatic-800 tracking-[0.14px] outline-none placeholder-body-2 placeholder-achromatic-500 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                                    style={{
                                        paddingInline: "12px",
                                        paddingBlock: "12px",
                                        paddingRight: "40px",
                                        backgroundColor: "var(--component-background)",
                                    }}
                                />
                                {quantity && (
                                    <button
                                        type="button"
                                        onClick={() => setQuantity("")}
                                        aria-label="보유 개수 입력 값 지우기"
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
                            <span className="title-1" style={{ color: "var(--achromatic-800)" }}>
                                주
                            </span>
                        </div>
                    </section>

                    <section className="flex flex-col px-5" style={{ gap: "12px" }}>
                        <label
                            className="body-3 tracking-[0.14px]"
                            style={{ color: "var(--achromatic-500)" }}
                        >
                            평균 단가
                        </label>
                        <div className="flex items-center" style={{ gap: "10px" }}>
                            <div className="relative w-full">
                                <input
                                    type="text"
                                    inputMode="numeric"
                                    value={averagePrice}
                                    onChange={(e) => setAveragePrice(e.target.value.replace(/[^\d]/g, ""))}
                                    placeholder="평균 단가"
                                    className="w-full rounded-[8px] label-1 text-achromatic-800 tracking-[0.14px] outline-none placeholder-body-2 placeholder-achromatic-500 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                                    style={{
                                        paddingInline: "12px",
                                        paddingBlock: "12px",
                                        paddingRight: "40px",
                                        backgroundColor: "var(--component-background)",
                                    }}
                                />
                                {averagePrice && (
                                    <button
                                        type="button"
                                        onClick={() => setAveragePrice("")}
                                        aria-label="평균 단가 입력 값 지우기"
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
                            <span className="title-1" style={{ color: "var(--achromatic-800)" }}>
                                원
                            </span>
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
                    type="button"
                    onClick={handleSave}
                    disabled={saveDisabled}
                    className={`${
                        saveDisabled ? "bg-[#d0d1d4]" : "bg-[#1FA9A4]"
                    } relative rounded-[8px] shrink-0 w-full transition-colors`}
                >
                    <div className="flex flex-row items-center justify-center size-full">
                        <div className="box-border content-stretch flex gap-[2px] items-center justify-center px-[8px] py-[12px] relative w-full">
                            <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[16px] text-center text-nowrap text-white tracking-[0.16px]">
                                <p className="leading-[1.5] whitespace-pre">
                                    {submitting ? "저장 중..." : "저장"}
                                </p>
                            </div>
                        </div>
                    </div>
                </button>
            </div>
        </div>
    );
}
