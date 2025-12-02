export type TradeAction = "buy" | "sell" | "hold";

export interface PriceDay {
    label: string;
    high: number;
    low: number;
    close: number;
    highTime: string;
    lowTime: string;
}

export interface SimulatedTrade {
    type: "buy" | "sell" | "hold";
    quantity: number;
    pricePerShare: number;
    time: string;
    profit?: number;
    profitPercent?: number;
    reason?: string;
}

export interface DayTrading {
    date: string;
    trades: SimulatedTrade[];
}

const ACTION_CHOICES: TradeAction[] = ["buy", "sell", "hold"];

function hashStringToSeed(value: string) {
    let hash = 0;
    for (let i = 0; i < value.length; i += 1) {
        hash = (hash << 5) - hash + value.charCodeAt(i);
        hash |= 0;
    }
    return Math.abs(hash) + 1;
}

function pseudoRandom(seed: number) {
    const x = Math.sin(seed) * 10000;
    return x - Math.floor(x);
}

function generateIntradayTime(seed: number) {
    const tradingStartMinutes = 9 * 60;
    const tradingEndMinutes = 15 * 60 + 30;
    const range = tradingEndMinutes - tradingStartMinutes;
    const randomMinutes = Math.floor(pseudoRandom(seed) * (range + 1));
    const totalMinutes = tradingStartMinutes + randomMinutes;
    const hours = String(Math.floor(totalMinutes / 60)).padStart(2, "0");
    const minutes = String(totalMinutes % 60).padStart(2, "0");
    return `${hours}:${minutes}`;
}

export function formatRelativeDayLabel(offset: number) {
    if (offset === 0) return "오늘";
    if (offset === 1) return "어제";
    const date = new Date();
    date.setDate(date.getDate() - offset);
    const month = date.getMonth() + 1;
    const day = date.getDate();
    return `${month}월 ${day}일`;
}

export function generateMockPriceSeries(stockName: string, days = 30, basePrice = 70000): PriceDay[] {
    const seedBase = hashStringToSeed(stockName);
    let priceCursor = basePrice;
    const series: PriceDay[] = [];

    for (let i = 0; i < days; i += 1) {
        const daySeed = seedBase + i * 13.37;
        const drift = (pseudoRandom(daySeed) - 0.5) * 4000;
        priceCursor = Math.max(30000, priceCursor + drift);
        const dailyLow = Math.max(25000, Math.round(priceCursor - pseudoRandom(daySeed + 1) * 2500));
        const dailyHigh = Math.round(priceCursor + pseudoRandom(daySeed + 2) * 2800);
        const dailyClose = Math.round(dailyLow + (dailyHigh - dailyLow) * pseudoRandom(daySeed + 3));
        series.push({
            label: formatRelativeDayLabel(i),
            high: dailyHigh,
            low: dailyLow,
            close: dailyClose,
            highTime: generateIntradayTime(daySeed + 4),
            lowTime: generateIntradayTime(daySeed + 5),
        });
    }

    return series;
}

export function generateRandomActions(stockName: string, length: number): TradeAction[] {
    const seedBase = hashStringToSeed(`${stockName}-actions`);
    return Array.from({ length }, (_, index) => {
        const pr = pseudoRandom(seedBase + index * 7.17);
        const choiceIndex = Math.floor(pr * ACTION_CHOICES.length) % ACTION_CHOICES.length;
        return ACTION_CHOICES[choiceIndex];
    });
}

export function simulateTradingHistory(
    initialInvestment: number,
    priceSeries: PriceDay[],
    actions: TradeAction[],
): { history: DayTrading[]; totalProfit: number } {
    let cash = initialInvestment;
    let holdings = 0;
    let totalCost = 0;
    let realizedProfit = 0;

    const history = priceSeries.map((day, index) => {
        const action = actions[index] ?? "hold";
        const trades: SimulatedTrade[] = [];

        if (action === "buy") {
            const maxAffordable = Math.floor(cash / day.low);
            if (maxAffordable > 0) {
                const cost = maxAffordable * day.low;
                cash -= cost;
                holdings += maxAffordable;
                totalCost += cost;
                trades.push({
                    type: "buy",
                    quantity: maxAffordable,
                    pricePerShare: day.low,
                    time: day.lowTime,
                });
            } else {
                trades.push({
                    type: "hold",
                    quantity: 0,
                    pricePerShare: day.low,
                    time: day.lowTime,
                    reason: "투자 가능 금액이 부족해 거래 내역 변화 없음",
                });
            }
        } else if (action === "sell") {
            const sellQuantity = holdings;
            if (sellQuantity > 0) {
                const averageCostPerShare = holdings > 0 ? totalCost / holdings : 0;
                const costBasis = averageCostPerShare * sellQuantity;
                const revenue = sellQuantity * day.high;
                const profit = revenue - costBasis;
                const profitPercent =
                    averageCostPerShare > 0 ? ((day.high - averageCostPerShare) / averageCostPerShare) * 100 : 0;

                cash += revenue;
                holdings -= sellQuantity;
                totalCost -= costBasis;
                realizedProfit += profit;

                trades.push({
                    type: "sell",
                    quantity: sellQuantity,
                    pricePerShare: day.high,
                    time: day.highTime,
                    profit: Math.round(profit),
                    profitPercent: parseFloat(profitPercent.toFixed(1)),
                });
            } else {
                trades.push({
                    type: "hold",
                    quantity: 0,
                    pricePerShare: day.high,
                    time: day.highTime,
                    reason: "보유 수량이 없어 '매수' 의견이 나올 때까지 거래 내역 변화 없음",
                });
            }
        } else {
            trades.push({
                type: "hold",
                quantity: holdings,
                pricePerShare: day.close,
                time: day.lowTime,
                reason: "리브리가 보유 전략을 유지했습니다. 거래 내역 변화 없음",
            });
        }

        return {
            date: day.label,
            trades,
        };
    });

    return { history, totalProfit: Math.round(realizedProfit) };
}
