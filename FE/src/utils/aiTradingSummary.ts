import { api } from "@/api/client";
import { resolveStockSymbol } from "@/lib/stocks";
import {
    DayTrading,
    type SimulatedTrade,
    generateMockPriceSeries,
    generateRandomActions,
    simulateTradingHistory,
} from "@/utils/aiTradingSimulation";

const SUPPORTED_SYMBOLS = new Set(["005930.KS", "005930"]);
const SUPPORTED_NAMES = new Set(["삼성전자"]);

export function isStockSupported(stockName: string): boolean {
    const trimmed = stockName?.trim();
    if (SUPPORTED_NAMES.has(trimmed)) return true;
    const symbol = resolveStockSymbol(trimmed);
    if (!symbol) return false;
    return SUPPORTED_SYMBOLS.has(symbol);
}

export interface TradingSummary {
    netShares: number;
    averagePrice: number;
    lastTradePrice: number | null;
    realizedProfit: number;
    positionValue: number;
}

type HistoricalSignalEntry = {
    date: string;
    signal: number;
    daily_return?: number;
    strategy_return?: number;
};

interface TradingSignalCacheData {
    signals: HistoricalSignalEntry[];
    history: DayTrading[];
    summary: TradingSummary | null;
    lastFetchedDate?: string;
}

const AI_TRADING_SIGNAL_CACHE_PREFIX = "libri_ai_trading_signals_v1";
const DAY_MS = 24 * 60 * 60 * 1000;

export function getReferenceDate(now = new Date()) {
    const referenceDate = new Date(now);
    const cutoffHour = 20;
    const cutoffMinute = 30;
    const afterCutoff =
        now.getHours() > cutoffHour ||
        (now.getHours() === cutoffHour && now.getMinutes() >= cutoffMinute);
    if (!afterCutoff) {
        referenceDate.setDate(referenceDate.getDate() - 1);
    }
    return referenceDate;
}

export function safeParseDate(value?: string | null): Date | null {
    if (!value) return null;
    const parsed = new Date(value);
    if (Number.isNaN(parsed.getTime())) {
        return null;
    }
    return parsed;
}

export function toDateOnlyString(date: Date | null): string | null {
    if (!date) return null;
    return date.toISOString().split("T")[0];
}

export function subtractDays(date: Date, days: number) {
    const copy = new Date(date);
    copy.setDate(copy.getDate() - days);
    return copy;
}

export function addDays(date: Date, days: number) {
    const copy = new Date(date);
    copy.setDate(copy.getDate() + days);
    return copy;
}

function normalizeCacheKeyPart(value: string) {
    return value.replace(/[^a-zA-Z0-9]/g, "_").toLowerCase();
}

function buildTradingCacheKey(userId: number | null | undefined, stockName: string, modelType: string) {
    const idPart = userId ? String(userId) : "guest";
    const stockPart = normalizeCacheKeyPart(stockName || "stock");
    const modelPart = normalizeCacheKeyPart(modelType || "model");
    return `${AI_TRADING_SIGNAL_CACHE_PREFIX}_${idPart}_${stockPart}_${modelPart}`;
}

function loadTradingSignalCache(key: string): TradingSignalCacheData | null {
    try {
        const raw = localStorage.getItem(key);
        if (!raw) return null;
        const parsed = JSON.parse(raw);
        if (parsed && typeof parsed === "object") {
            parsed.signals = Array.isArray(parsed.signals) ? parsed.signals : [];
            parsed.history = Array.isArray(parsed.history) ? parsed.history : [];
            return parsed as TradingSignalCacheData;
        }
    } catch {
        // ignore
    }
    return null;
}

function saveTradingSignalCache(key: string, data: TradingSignalCacheData) {
    try {
        localStorage.setItem(key, JSON.stringify(data));
    } catch {
        // ignore
    }
}

function normalizeHistoricalSignals(signals: HistoricalSignalEntry[], limitDate?: string | null) {
    if (!Array.isArray(signals)) return [];
    return signals
        .map((entry) => {
            const dateOnly = entry.date?.split("T")[0] ?? entry.date;
            return dateOnly ? { ...entry, date: dateOnly } : null;
        })
        .filter((entry): entry is HistoricalSignalEntry => {
            if (!entry) return false;
            if (limitDate) {
                return entry.date <= limitDate;
            }
            return true;
        })
        .sort((a, b) => a.date.localeCompare(b.date));
}

function mergeHistoricalSignals(existing: HistoricalSignalEntry[], updates: HistoricalSignalEntry[]) {
    const map = new Map<string, HistoricalSignalEntry>();
    existing.forEach((entry) => {
        map.set(entry.date, entry);
    });
    updates.forEach((entry) => {
        map.set(entry.date, entry);
    });
    return Array.from(map.values()).sort((a, b) => a.date.localeCompare(b.date));
}

function getLastSignalDate(signals: HistoricalSignalEntry[]): string | null {
    if (!signals.length) return null;
    return signals[signals.length - 1].date;
}

function determineNextFetchDate(
    rangeStartStr: string | null,
    lastFetchedDateStr: string | null,
    rangeEndDate: Date | null,
): string | null {
    if (!rangeEndDate) {
        return rangeStartStr;
    }
    if (!lastFetchedDateStr) {
        return rangeStartStr;
    }
    const lastFetched = safeParseDate(lastFetchedDateStr);
    if (!lastFetched) {
        return rangeStartStr;
    }
    const nextDate = addDays(lastFetched, 1);
    if (nextDate > rangeEndDate) {
        return null;
    }
    return toDateOnlyString(nextDate);
}

function filterTradingHistoryToActionDays(history: DayTrading[]) {
    return history
        .map((day) => ({
            ...day,
            trades: day.trades.filter((trade) => trade.type === "buy" || trade.type === "sell"),
        }))
        .filter((day) => day.trades.length > 0);
}

export function calculateTradingHistory(
    aiHistory: Array<{ date: string; signal: number; daily_return?: number; strategy_return?: number }>,
    stockHistory: Array<{ date: string; open: number; high: number; low: number; close: number }>,
    initialCapital: number,
): DayTrading[] {
    const history: DayTrading[] = [];
    let cash = initialCapital;
    let shares = 0;
    let avgPrice = 0;

    const priceMap = new Map(stockHistory.map((item) => [item.date.split("T")[0], item]));

    aiHistory.forEach((signal) => {
        const dateStr = signal.date;
        const priceData = priceMap.get(dateStr);

        if (!priceData) return;

        const trades: SimulatedTrade[] = [];

        if (signal.signal === 0) {
            const buyPrice = priceData.low || priceData.close || priceData.open;
            const maxShares = Math.floor(cash / buyPrice);

            if (maxShares > 0) {
                const buyShares = maxShares;
                const cost = buyShares * buyPrice;

                if (shares > 0) {
                    avgPrice = ((avgPrice * shares) + cost) / (shares + buyShares);
                } else {
                    avgPrice = buyPrice;
                }

                shares += buyShares;
                cash -= cost;

                trades.push({
                    type: "buy",
                    quantity: buyShares,
                    pricePerShare: buyPrice,
                    time: dateStr,
                });
            } else {
                trades.push({
                    type: "hold",
                    quantity: 0,
                    pricePerShare: 0,
                    time: dateStr,
                    reason: "매수 자금이 부족합니다.",
                });
            }
        } else if (signal.signal === 1) {
            if (shares > 0) {
                const sellPrice = priceData.high || priceData.close || priceData.open;
                const sellShares = shares;
                const revenue = sellShares * sellPrice;
                const profit = revenue - (avgPrice * sellShares);
                const profitPercent = ((sellPrice - avgPrice) / avgPrice) * 100;

                cash += revenue;
                shares = 0;
                avgPrice = 0;

                trades.push({
                    type: "sell",
                    quantity: sellShares,
                    pricePerShare: sellPrice,
                    time: dateStr,
                    profit: Math.round(profit),
                    profitPercent: Math.round(profitPercent * 10) / 10,
                });
            } else {
                trades.push({
                    type: "hold",
                    quantity: 0,
                    pricePerShare: 0,
                    time: dateStr,
                    reason: "보유 중인 주식이 없습니다.",
                });
            }
        } else {
            trades.push({
                type: "hold",
                quantity: 0,
                pricePerShare: 0,
                time: dateStr,
                reason: "리브리 전략에 따라 변동이 없습니다.",
            });
        }

        if (trades.length > 0) {
            history.push({
                date: dateStr,
                trades,
            });
        }
    });

    return history;
}

export function summarizeTradingHistoryEntries(history: DayTrading[]): TradingSummary {
    let shares = 0;
    let totalCost = 0;
    let realizedProfit = 0;
    let lastTradePrice: number | null = null;

    history.forEach((day) => {
        day.trades.forEach((trade) => {
            if (trade.type === "buy") {
                const cost = trade.quantity * trade.pricePerShare;
                totalCost += cost;
                shares += trade.quantity;
                lastTradePrice = trade.pricePerShare;
            } else if (trade.type === "sell") {
                const sellQuantity = trade.quantity;
                const averageCost = shares > 0 ? totalCost / shares : 0;
                const costBasis = averageCost * sellQuantity;
                totalCost -= costBasis;
                shares -= sellQuantity;
                realizedProfit += trade.profit ?? 0;
                lastTradePrice = trade.pricePerShare;
            }
        });
    });

    if (shares < 0) shares = 0;
    if (totalCost < 0) totalCost = 0;
    const averagePrice = shares > 0 ? totalCost / shares : lastTradePrice ?? 0;
    const positionValue = shares > 0 ? shares * (lastTradePrice ?? averagePrice) : 0;

    return {
        netShares: shares,
        averagePrice,
        lastTradePrice,
        realizedProfit,
        positionValue,
    };
}

export interface FetchAiTradingSummaryParams {
    stockName: string;
    investmentStyle: "공격형" | "안정형";
    initialInvestment: number;
    userCreatedAt?: string | null;
    userId?: number | null;
}

export interface FetchAiTradingSummaryResult {
    history: DayTrading[];
    summary: TradingSummary | null;
    backendConnected: boolean;
}

export async function fetchAiTradingSummary({
    stockName,
    investmentStyle,
    initialInvestment,
    userCreatedAt,
    userId,
}: FetchAiTradingSummaryParams): Promise<FetchAiTradingSummaryResult> {
    if (!isStockSupported(stockName)) {
        return {
            history: [],
            summary: null,
            backendConnected: false,
        };
    }
    const referenceDate = getReferenceDate();
    const defaultStartDate = subtractDays(referenceDate, 30);
    const tradingRangeStartDate = safeParseDate(userCreatedAt) ?? defaultStartDate;
    const tradingRangeStartStr =
        toDateOnlyString(tradingRangeStartDate) ?? toDateOnlyString(defaultStartDate) ?? "2025-01-01";
    const tradingRangeEndStr = toDateOnlyString(referenceDate) ?? "2025-01-01";
    const tradingRangeEndDate = safeParseDate(tradingRangeEndStr);
    const modelType = investmentStyle === "공격형" ? "a2c" : "marl";
    const cacheKey = buildTradingCacheKey(userId ?? null, stockName, modelType);
    const symbol = resolveStockSymbol(stockName) || "005930.KS";

    let backendConnected = false;

    try {
        let signals: HistoricalSignalEntry[] = [];
        let lastFetchedDateStr: string | null = null;
        let cachedHistory: DayTrading[] = [];
        let cachedSummary: TradingSummary | null = null;

        if (cacheKey) {
            const cachedData = loadTradingSignalCache(cacheKey);
            if (cachedData) {
                signals = Array.isArray(cachedData.signals) ? cachedData.signals : [];
                lastFetchedDateStr = cachedData.lastFetchedDate ?? getLastSignalDate(signals);
                if (cachedData.history?.length) {
                    cachedHistory = cachedData.history;
                    cachedSummary =
                        cachedData.summary ?? summarizeTradingHistoryEntries(cachedData.history);
                }
            }
        }

        const rangeStartStr = tradingRangeStartStr || "2025-01-01";
        const rangeEndStr = tradingRangeEndStr || rangeStartStr;
        const nextFetchDateStr = determineNextFetchDate(rangeStartStr, lastFetchedDateStr, tradingRangeEndDate);

        if (nextFetchDateStr) {
            try {
                const fetchedSignals = await api.getAIHistory(modelType, nextFetchDateStr);
                backendConnected = true;
                const normalized = normalizeHistoricalSignals(
                    fetchedSignals as HistoricalSignalEntry[],
                    rangeEndStr,
                );
                if (normalized.length > 0) {
                    signals = mergeHistoricalSignals(signals, normalized);
                    lastFetchedDateStr = normalized[normalized.length - 1].date;
                }
            } catch (fetchError) {
                console.warn("AI 거래 히스토리 로딩 실패:", fetchError);
            }
        } else if (signals.length) {
            backendConnected = true;
        }

        signals = signals.filter((entry) => entry.date >= rangeStartStr && entry.date <= rangeEndStr);

        if (!signals.length) {
            return {
                history: cachedHistory,
                summary: cachedSummary,
                backendConnected,
            };
        }

        const startDateForHistory = safeParseDate(rangeStartStr) ?? safeParseDate(signals[0].date);
        const endDateForHistory = tradingRangeEndDate ?? safeParseDate(getLastSignalDate(signals) ?? "");
        const diffDays =
            startDateForHistory && endDateForHistory
                ? Math.max(
                      30,
                      Math.ceil((endDateForHistory.getTime() - startDateForHistory.getTime()) / DAY_MS) + 2,
                  )
                : 30;

        const stockHistory = await api.getStockHistory(symbol, diffDays);
        backendConnected = true;
        const history = calculateTradingHistory(signals, stockHistory, initialInvestment);
        const filteredHistory = filterTradingHistoryToActionDays(history);
        const summary = summarizeTradingHistoryEntries(history);

        if (cacheKey) {
            saveTradingSignalCache(cacheKey, {
                signals,
                history: filteredHistory,
                summary,
                lastFetchedDate: lastFetchedDateStr ?? rangeEndStr,
            });
        }

        return { history: filteredHistory, summary, backendConnected };
    } catch (error) {
        console.error("AI 거래 요약 로딩 실패, Mock 데이터 사용:", error);
        const priceSeries = generateMockPriceSeries(stockName);
        const actionPlan = generateRandomActions(stockName, priceSeries.length || 5);
        const { history } = simulateTradingHistory(initialInvestment, priceSeries, actionPlan);
        const today = new Date();
        const updatedHistory = history.map((day, index) => {
            const date = new Date(today);
            date.setDate(date.getDate() - index);
            return {
                ...day,
                date: date.toISOString().split("T")[0],
            };
        });

        const filteredFallback = filterTradingHistoryToActionDays(updatedHistory);
        const summary = summarizeTradingHistoryEntries(updatedHistory);
        return {
            history: filteredFallback,
            summary,
            backendConnected: false,
        };
    }
}
