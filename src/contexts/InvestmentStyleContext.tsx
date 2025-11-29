import { createContext, useContext, ReactNode } from 'react';

export type InvestmentStyle = '공격형' | '중간형' | '안정형';

export const getModelType = (style: InvestmentStyle): string => {
  switch (style) {
    case '공격형':
      return 'marl_4agent'; // 공격형 - marl_4agent 사용
    case '중간형':
      return 'marl_4agent'; // 중간형 - marl_4agent 사용
    case '안정형':
      return 'marl_3agent'; // 안정형 - marl_3agent 사용
    default:
      return 'marl_4agent'; // 기본값
  }
};

interface InvestmentStyleContextType {
  investmentStyle: InvestmentStyle;
  modelType: string;
}

const InvestmentStyleContext = createContext<InvestmentStyleContextType | undefined>(undefined);

export function InvestmentStyleProvider({ 
  children, 
  investmentStyle 
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
    throw new Error('useInvestmentStyle must be used within an InvestmentStyleProvider');
  }
  return context;
}
