import { createContext, useContext, ReactNode } from "react";

export type InvestmentStyle = "공격형" | "안정형";

export const getModelType = (style: InvestmentStyle): string => {
    switch (style) {
        case "공격형":
            return "model2"; // 공격형 - a2c 모델 사용
        case "안정형":
            return "model3"; // 안정형 - marl_3agent 모델 사용
        default:
            return "model2"; // 기본값
    }
};

interface InvestmentStyleContextType {
    investmentStyle: InvestmentStyle;
    modelType: string;
}

const InvestmentStyleContext = createContext<InvestmentStyleContextType | undefined>(undefined);

export function InvestmentStyleProvider({
    children,
    investmentStyle,
}: {
    children: ReactNode;
    investmentStyle: InvestmentStyle;
}) {
    const modelType = getModelType(investmentStyle);

    return (
        <InvestmentStyleContext.Provider value={{ investmentStyle, modelType }}>
            {children}
        </InvestmentStyleContext.Provider>
    );
}

export function useInvestmentStyle() {
    const context = useContext(InvestmentStyleContext);
    if (context === undefined) {
        throw new Error("useInvestmentStyle must be used within an InvestmentStyleProvider");
    }
    return context;
}
