import { useReducer } from 'react';
import Onboarding from './components/Onboarding';
import StockQuantityInput from './components/StockQuantityInput';
import StockPriceInput from './components/StockPriceInput';
import InitialInvestmentInput from './components/InitialInvestmentInput';
import InvestmentStyleSelection from './components/InvestmentStyleSelection';
import Home from './components/Home';
import imgFrame26089667 from "figma:asset/bdac4e7d8d4f71d5aef6253221470dffe73bb6a6.png";
import { InvestmentStyle, InvestmentStyleProvider } from './contexts/InvestmentStyleContext';

type Page = 'onboarding' | 'quantity' | 'price' | 'investment' | 'style' | 'home' | 'add-stock' | 'add-quantity' | 'add-price';

interface Stock {
  name: string;
  quantity: number;
  averagePrice: number;
  totalValue: number;
  profit: number;
  profitRate: number;
  logoUrl?: string;
}

interface FormData {
  stockName: string;
  quantity: string;
  price: string;
}

interface State {
  currentPage: Page;
  initialInvestment: string;
  investmentStyle: InvestmentStyle | '';
  stocks: Stock[];
  onboardingForm: FormData;
  addStockForm: FormData;
}

type Action =
  | { type: 'SET_PAGE'; page: Page }
  | { type: 'SET_ONBOARDING_FIELD'; field: keyof FormData; value: string }
  | { type: 'SET_ADD_STOCK_FIELD'; field: keyof FormData; value: string }
  | { type: 'SET_INITIAL_INVESTMENT'; value: string }
  | { type: 'COMPLETE_ONBOARDING'; style: InvestmentStyle }
  | { type: 'ADD_STOCK' }
  | { type: 'RESET_ADD_STOCK_FORM' };

const initialState: State = {
  currentPage: 'onboarding',
  initialInvestment: '',
  investmentStyle: '',
  stocks: [],
  onboardingForm: { stockName: '', quantity: '', price: '' },
  addStockForm: { stockName: '', quantity: '', price: '' }
};

function createStock(form: FormData, logoUrl: string): Stock {
  const quantity = parseInt(form.quantity);
  const price = parseInt(form.price);
  return {
    name: form.stockName,
    quantity,
    averagePrice: price,
    totalValue: quantity * price,
    profit: 0, // 백엔드에서 계산 예정
    profitRate: 0, // 백엔드에서 계산 예정
    logoUrl
  };
}

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'SET_PAGE':
      return { ...state, currentPage: action.page };
    
    case 'SET_ONBOARDING_FIELD':
      return {
        ...state,
        onboardingForm: { ...state.onboardingForm, [action.field]: action.value }
      };
    
    case 'SET_ADD_STOCK_FIELD':
      return {
        ...state,
        addStockForm: { ...state.addStockForm, [action.field]: action.value }
      };
    
    case 'SET_INITIAL_INVESTMENT':
      return { ...state, initialInvestment: action.value };
    
    case 'COMPLETE_ONBOARDING':
      return {
        ...state,
        investmentStyle: action.style,
        stocks: [createStock(state.onboardingForm, imgFrame26089667)],
        currentPage: 'home'
      };
    
    case 'ADD_STOCK':
      return {
        ...state,
        stocks: [...state.stocks, createStock(state.addStockForm, imgFrame26089667)],
        currentPage: 'home'
      };
    
    case 'RESET_ADD_STOCK_FORM':
      return {
        ...state,
        addStockForm: { stockName: '', quantity: '', price: '' }
      };
    
    default:
      return state;
  }
}

export default function App() {
  const [state, dispatch] = useReducer(reducer, initialState);

  // 페이지 네비게이션 핸들러
  const goToPage = (page: Page) => dispatch({ type: 'SET_PAGE', page });

  // 온보딩 플로우 핸들러
  const handleOnboardingStock = (stockName: string) => {
    dispatch({ type: 'SET_ONBOARDING_FIELD', field: 'stockName', value: stockName });
    goToPage('quantity');
  };

  const handleOnboardingQuantity = (quantity: string) => {
    dispatch({ type: 'SET_ONBOARDING_FIELD', field: 'quantity', value: quantity });
    goToPage('price');
  };

  const handleOnboardingPrice = (price: string) => {
    dispatch({ type: 'SET_ONBOARDING_FIELD', field: 'price', value: price });
    goToPage('investment');
  };

  const handleInitialInvestment = (investment: string) => {
    dispatch({ type: 'SET_INITIAL_INVESTMENT', value: investment });
    goToPage('style');
  };

  const handleStyleSelection = (style: string) => {
    dispatch({ type: 'COMPLETE_ONBOARDING', style: style as InvestmentStyle });
  };

  // 종목 추가 플로우 핸들러
  const handleAddStock = () => {
    dispatch({ type: 'RESET_ADD_STOCK_FORM' });
    goToPage('add-stock');
  };

  const handleAddStockName = (stockName: string) => {
    dispatch({ type: 'SET_ADD_STOCK_FIELD', field: 'stockName', value: stockName });
    goToPage('add-quantity');
  };

  const handleAddStockQuantity = (quantity: string) => {
    dispatch({ type: 'SET_ADD_STOCK_FIELD', field: 'quantity', value: quantity });
    goToPage('add-price');
  };

  const handleAddStockPrice = (price: string) => {
    dispatch({ type: 'SET_ADD_STOCK_FIELD', field: 'price', value: price });
    dispatch({ type: 'ADD_STOCK' });
  };

  // 뒤로 가기 핸들러 - 상태 초기화와 함께
  const goBackWithReset = (page: Page, resetField?: { type: 'onboarding' | 'addStock'; field: keyof FormData }) => {
    if (resetField) {
      const actionType = resetField.type === 'onboarding' ? 'SET_ONBOARDING_FIELD' : 'SET_ADD_STOCK_FIELD';
      dispatch({ type: actionType as any, field: resetField.field, value: '' });
    }
    goToPage(page);
  };

  return (
    <div className="bg-white min-h-screen">
      <InvestmentStyleProvider investmentStyle={state.investmentStyle as InvestmentStyle}>
        {state.currentPage === 'onboarding' && (
          <Onboarding onSubmit={handleOnboardingStock} />
        )}
      {state.currentPage === 'quantity' && (
        <StockQuantityInput
          stockName={state.onboardingForm.stockName}
          onBack={() => goBackWithReset('onboarding', { type: 'onboarding', field: 'stockName' })}
          onSubmit={handleOnboardingQuantity}
        />
      )}
      {state.currentPage === 'price' && (
        <StockPriceInput
          onBack={() => goBackWithReset('quantity', { type: 'onboarding', field: 'quantity' })}
          onSubmit={handleOnboardingPrice}
        />
      )}
      {state.currentPage === 'investment' && (
        <InitialInvestmentInput
          onBack={() => goBackWithReset('price', { type: 'onboarding', field: 'price' })}
          onSubmit={handleInitialInvestment}
        />
      )}
      {state.currentPage === 'style' && (
        <InvestmentStyleSelection
          onBack={() => goBackWithReset('investment')}
          onSubmit={handleStyleSelection}
        />
      )}
      {state.currentPage === 'home' && (
        <Home
          initialInvestment={parseInt(state.initialInvestment) || 0}
          stocks={state.stocks}
          onAddStock={handleAddStock}
          investmentStyle={state.investmentStyle as InvestmentStyle}
        />
      )}
      {state.currentPage === 'add-stock' && (
        <Onboarding 
          onSubmit={handleAddStockName}
          onBack={() => goToPage('home')}
        />
      )}
      {state.currentPage === 'add-quantity' && (
        <StockQuantityInput
          stockName={state.addStockForm.stockName}
          onBack={() => goBackWithReset('add-stock', { type: 'addStock', field: 'stockName' })}
          onSubmit={handleAddStockQuantity}
        />
      )}
      {state.currentPage === 'add-price' && (
        <StockPriceInput
          onBack={() => goBackWithReset('add-quantity', { type: 'addStock', field: 'quantity' })}
          onSubmit={handleAddStockPrice}
        />
      )}
      </InvestmentStyleProvider>
    </div>
  );
}
