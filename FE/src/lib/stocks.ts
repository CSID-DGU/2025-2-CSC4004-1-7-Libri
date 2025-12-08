export const STOCK_NAME_TO_SYMBOL: Record<string, string> = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
};

export const SYMBOL_TO_STOCK_NAME: Record<string, string> = {
    "005930.KS": "삼성전자",
    "000660.KS": "SK하이닉스",
    "005930": "삼성전자",
    "000660": "SK하이닉스",
};

export function resolveStockSymbol(rawName: string): string {
    const trimmed = rawName?.trim();
    if (!trimmed) return "";

    const mappedSymbol = STOCK_NAME_TO_SYMBOL[trimmed];
    if (mappedSymbol) {
        return mappedSymbol;
    }

    if (/^\d{6}$/.test(trimmed)) {
        return `${trimmed}.KS`;
    }

    return trimmed.toUpperCase();
}

export function mapSymbolToDisplayName(symbol?: string | null): string {
    if (!symbol) return "";
    const trimmed = symbol.trim();
    return (
        SYMBOL_TO_STOCK_NAME[trimmed] ||
        SYMBOL_TO_STOCK_NAME[trimmed.toUpperCase()] ||
        trimmed
    );
}
