import type { InvestmentStyle } from "@/contexts/InvestmentStyleContext";

export type BackendInvestmentStyle = "aggressive" | "conservative";

const BACKEND_TO_DISPLAY_STYLE: Record<BackendInvestmentStyle, InvestmentStyle> = {
    aggressive: "공격형",
    conservative: "안정형",
};

const DISPLAY_TO_BACKEND_STYLE: Record<InvestmentStyle, BackendInvestmentStyle> = {
    공격형: "aggressive",
    안정형: "conservative",
};

export function mapBackendStyleToDisplay(style?: string | null): InvestmentStyle | "" {
    if (!style) return "";
    if (style === "공격형" || style === "안정형") {
        return style;
    }
    return BACKEND_TO_DISPLAY_STYLE[style as BackendInvestmentStyle] ?? "";
}

export function mapDisplayStyleToBackend(style?: string | null): BackendInvestmentStyle | null {
    if (!style) return null;
    if (style === "aggressive" || style === "conservative") {
        return style as BackendInvestmentStyle;
    }
    return DISPLAY_TO_BACKEND_STYLE[style as InvestmentStyle] ?? null;
}
