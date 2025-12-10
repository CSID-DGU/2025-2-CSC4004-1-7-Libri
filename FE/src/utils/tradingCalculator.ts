// 거래 내역 계산 유틸리티
export interface TradingResult {
    totalProfit: number;
    profitRate: number;
    finalCash: number;
    finalShares: number;
}

export function calculateTradingProfit(
    aiHistory: Array<{ date: string; signal: number; daily_return?: number; strategy_return?: number }>,
    stockHistory: Array<{ date: string; open: number; high: number; low: number; close: number }>,
    initialCapital: number
): TradingResult {
    let totalProfit = 0;
    let cash = initialCapital;
    let shares = 0;
    let avgPrice = 0;

    // 주가 데이터를 날짜별로 매핑
    const priceMap = new Map(
        stockHistory.map(item => [item.date.split('T')[0], item])
    );

    aiHistory.forEach((signal) => {
        const dateStr = signal.date;
        const priceData = priceMap.get(dateStr);
        
        if (!priceData) return;

        // signal: 0 = BUY (Long), 1 = SELL (Short), 2 = HOLD
        if (signal.signal === 0) {
            // 매수 시그널
            const buyPrice = priceData.low || priceData.close || priceData.open; // 당일 최저가로 매수
            const maxShares = Math.floor(cash / buyPrice);

            if (maxShares > 0) {
                // 매수 가능
                const buyShares = maxShares;
                const cost = buyShares * buyPrice;
                
                // 평균 단가 계산
                if (shares > 0) {
                    avgPrice = ((avgPrice * shares) + cost) / (shares + buyShares);
                } else {
                    avgPrice = buyPrice;
                }
                
                shares += buyShares;
                cash -= cost;
            }
        } else if (signal.signal === 1) {
            // 매도 시그널
            if (shares > 0) {
                const sellPrice = priceData.high || priceData.close || priceData.open; // 당일 최고가로 매도
                const sellShares = shares;
                const revenue = sellShares * sellPrice;
                const profit = revenue - (avgPrice * sellShares);

                totalProfit += profit;
                cash += revenue;
                shares = 0;
                avgPrice = 0;
            }
        }
        // signal === 2 (HOLD)인 경우는 아무것도 하지 않음
    });

    // 현재 보유 중인 주식의 평가 손익도 포함
    if (shares > 0 && stockHistory.length > 0) {
        const currentPrice = stockHistory[stockHistory.length - 1].close;
        const unrealizedProfit = (currentPrice - avgPrice) * shares;
        totalProfit += unrealizedProfit;
    }

    const profitRate = initialCapital > 0 
        ? (totalProfit / initialCapital) * 100 
        : 0;

    return {
        totalProfit,
        profitRate,
        finalCash: cash,
        finalShares: shares
    };
}