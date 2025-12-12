import { useReducer, useEffect } from "react";
import StartScreen from "./components/StartScreen";
import Register from "./components/Register";
import Login from "./components/Login";
import Onboarding from "./components/StockName";
import StockQuantityInput from "./components/StockQuantityInput";
import StockPriceInput from "./components/StockPriceInput";
import InitialInvestmentInput from "./components/InitialInvestmentInput";
import InvestmentStyleSelection from "./components/InvestmentStyleSelection";
import Home from "./components/Home";
import Settings from "./components/Settings";
import { InvestmentStyle, InvestmentStyleProvider } from "./contexts/InvestmentStyleContext";
import { api } from "./api/client";
import {
    resolveStockSymbol,
    mapSymbolToDisplayName,
} from "./lib/stocks";

type Page =
    | "start"
    | "login"
    | "register"
    | "onboarding"
    | "quantity"
    | "price"
    | "investment"
    | "style"
    | "home"
    | "settings"
    | "add-stock"
    | "add-quantity"
    | "add-price";

interface Stock {
    name: string;
    quantity: number;
    averagePrice: number;
    totalValue: number;
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
    investmentStyle: InvestmentStyle | "";
    stocks: Stock[];
    onboardingForm: FormData;
    addStockForm: FormData;
    userId: number | null;
    userEmail: string | null;
    onboardingCompleted: boolean;
    userCreatedAt: string | null;
}

type Action =
    | { type: "SET_PAGE"; page: Page }
    | { type: "SET_ONBOARDING_FIELD"; field: keyof FormData; value: string }
    | { type: "SET_ADD_STOCK_FIELD"; field: keyof FormData; value: string }
    | { type: "SET_INITIAL_INVESTMENT"; value: string }
    | { type: "SET_INVESTMENT_STYLE"; style: InvestmentStyle | "" }
    | { type: "COMPLETE_ONBOARDING"; style: InvestmentStyle }
    | { type: "SET_STOCKS"; stocks: Stock[] }
    | { type: "ADD_STOCK" }
    | { type: "RESET_ADD_STOCK_FORM" }
    | { type: "SET_USER"; userId: number; email: string }
    | { type: "SET_USER_CREATED_AT"; createdAt: string | null }
    | { type: "SET_ONBOARDING_STATUS"; completed: boolean }
    | { type: "LOGOUT" }
    | { type: "HYDRATE_FROM_STORAGE"; payload: Partial<Pick<State, "initialInvestment" | "investmentStyle" | "stocks" | "onboardingForm" | "addStockForm" | "onboardingCompleted">> };

const initialState: State = {
    currentPage: "start",
    initialInvestment: "",
    investmentStyle: "",
    stocks: [],
    onboardingForm: { stockName: "", quantity: "", price: "" },
    addStockForm: { stockName: "", quantity: "", price: "" },
    userId: null,
    userEmail: null,
    onboardingCompleted: false,
    userCreatedAt: null,
};

function createStock(form: FormData, logoUrl?: string): Stock {
    const quantity = parseInt(form.quantity);
    const price = parseInt(form.price);
    return {
        name: form.stockName,
        quantity,
        averagePrice: price,
        totalValue: quantity * price,
        logoUrl,
    };
}

type BackendInvestmentStyle = "aggressive" | "conservative";

const BACKEND_TO_DISPLAY_STYLE: Record<BackendInvestmentStyle, InvestmentStyle> = {
    aggressive: "공격형",
    conservative: "안정형",
};

const DISPLAY_TO_BACKEND_STYLE: Record<InvestmentStyle, BackendInvestmentStyle> = {
    공격형: "aggressive",
    안정형: "conservative",
};

function mapBackendStyleToDisplay(style?: string | null): InvestmentStyle | "" {
    if (!style) return "";
    return BACKEND_TO_DISPLAY_STYLE[style as BackendInvestmentStyle] ?? "";
}

function mapDisplayStyleToBackend(style: string): BackendInvestmentStyle | null {
    return DISPLAY_TO_BACKEND_STYLE[style as InvestmentStyle] ?? null;
}

function parsePositiveInteger(value: string): number | null {
    const numericValue = parseInt(value, 10);
    if (Number.isNaN(numericValue) || numericValue <= 0) {
        return null;
    }
    return numericValue;
}


function mapHoldingsToStocks(holdings: any[]): Stock[] {
    return (holdings || []).map((holding: any) => {
        const rawQuantity = Number(holding?.quantity ?? 0);
        const rawAvgPrice = Number(holding?.avg_price ?? 0);
        const rawCurrentPrice = Number(holding?.current_price ?? holding?.avg_price ?? 0);

        const quantity = Number.isNaN(rawQuantity) ? 0 : rawQuantity;
        const averagePrice = Number.isNaN(rawAvgPrice) ? 0 : rawAvgPrice;
        const currentPrice = Number.isNaN(rawCurrentPrice) ? averagePrice : rawCurrentPrice;
        const displayName = mapSymbolToDisplayName(holding?.symbol) || holding?.symbol || "알 수 없음";

        return {
            name: displayName,
            quantity,
            averagePrice,
            totalValue: quantity * currentPrice,
            logoUrl: undefined,
        };
    });
}

function reducer(state: State, action: Action): State {
    switch (action.type) {
        case "SET_PAGE":
            return { ...state, currentPage: action.page };

        case "SET_ONBOARDING_FIELD":
            return {
                ...state,
                onboardingForm: { ...state.onboardingForm, [action.field]: action.value },
            };

        case "SET_ADD_STOCK_FIELD":
            return {
                ...state,
                addStockForm: { ...state.addStockForm, [action.field]: action.value },
            };

        case "SET_INITIAL_INVESTMENT":
            return { ...state, initialInvestment: action.value };

        case "SET_INVESTMENT_STYLE":
            return { ...state, investmentStyle: action.style };

        case "COMPLETE_ONBOARDING":
            return {
                ...state,
                investmentStyle: action.style,
                stocks: [createStock(state.onboardingForm)],
                currentPage: "home",
                onboardingCompleted: true,
            };

        case "SET_STOCKS":
            return { ...state, stocks: action.stocks };

        case "ADD_STOCK":
            return {
                ...state,
                stocks: [...state.stocks, createStock(state.addStockForm)],
                currentPage: "home",
            };

        case "RESET_ADD_STOCK_FORM":
            return {
                ...state,
                addStockForm: { stockName: "", quantity: "", price: "" },
            };
        case "SET_USER":
            return { ...state, userId: action.userId, userEmail: action.email };
        case "SET_ONBOARDING_STATUS":
            return { ...state, onboardingCompleted: action.completed };
        case "LOGOUT":
            return {
                ...initialState,
                onboardingForm: { ...initialState.onboardingForm },
                addStockForm: { ...initialState.addStockForm },
            };
        case "HYDRATE_FROM_STORAGE":
            return {
                ...state,
                initialInvestment: action.payload.initialInvestment ?? state.initialInvestment,
                investmentStyle: action.payload.investmentStyle ?? state.investmentStyle,
                stocks: action.payload.stocks ?? state.stocks,
                onboardingForm: action.payload.onboardingForm ?? state.onboardingForm,
                addStockForm: action.payload.addStockForm ?? state.addStockForm,
                onboardingCompleted: action.payload.onboardingCompleted ?? state.onboardingCompleted,
            };

        default:
            return state;
    }
}

const STORAGE_KEY = "libri_onboarding_state";

export default function App() {
    const [state, dispatch] = useReducer(reducer, initialState);

    const hydrateStateFromBackend = async (userId: number, existingUserInfo?: any) => {
        let userInfo = existingUserInfo;
        if (!userInfo) {
            try {
                userInfo = await api.getUser(userId);
            } catch (error) {
                console.error("사용자 정보를 불러오지 못했습니다:", error);
                return;
            }
        }

        const mappedStyle = mapBackendStyleToDisplay(userInfo?.investment_style);
        if (mappedStyle) {
            dispatch({ type: "SET_INVESTMENT_STYLE", style: mappedStyle });
        }

        if (typeof userInfo?.onboarding_completed === "boolean") {
            dispatch({ type: "SET_ONBOARDING_STATUS", completed: Boolean(userInfo.onboarding_completed) });
        }
        if (userInfo?.created_at) {
            dispatch({ type: "SET_USER_CREATED_AT", createdAt: userInfo.created_at });
        }

        try {
            const portfolio = await api.getPortfolio(userId);
            if (portfolio) {
                const mappedStocks = mapHoldingsToStocks(portfolio.holdings ?? []);
                dispatch({ type: "SET_STOCKS", stocks: mappedStocks });

                if (mappedStocks.length > 0) {
                    const firstStock = mappedStocks[0];
                    dispatch({ type: "SET_ONBOARDING_FIELD", field: "stockName", value: firstStock.name });
                    dispatch({
                        type: "SET_ONBOARDING_FIELD",
                        field: "quantity",
                        value: firstStock.quantity.toString(),
                    });
                    dispatch({
                        type: "SET_ONBOARDING_FIELD",
                        field: "price",
                        value: firstStock.averagePrice.toString(),
                    });
                }

                const initialValue =
                    typeof portfolio.total_asset === "number"
                        ? portfolio.total_asset
                        : portfolio.current_capital;

                if (typeof initialValue === "number" && !Number.isNaN(initialValue)) {
                    dispatch({
                        type: "SET_INITIAL_INVESTMENT",
                        value: Math.round(initialValue).toString(),
                    });
                }
            }
        } catch (error) {
            console.error("포트폴리오 정보를 불러오지 못했습니다:", error);
        }
    };

    const persistHoldingFromForm = async (userId: number, form: FormData) => {
        const symbol = resolveStockSymbol(form.stockName);
        const quantity = parsePositiveInteger(form.quantity);
        const avgPrice = parsePositiveInteger(form.price);

        if (!symbol || quantity === null || avgPrice === null) {
            return false;
        }

        try {
            await api.addHolding(userId, {
                symbol,
                quantity,
                avg_price: avgPrice,
            });
            return true;
        } catch (error) {
            console.error("보유 주식 정보를 저장하지 못했습니다:", error);
            return false;
        }
    };

    useEffect(() => {
        if (typeof window === "undefined") return;
        try {
            const stored = window.localStorage.getItem(STORAGE_KEY);
            if (!stored) return;
            const parsed = JSON.parse(stored);
            dispatch({ type: "HYDRATE_FROM_STORAGE", payload: parsed });
        } catch (error) {
            console.warn("저장된 온보딩 정보를 불러오지 못했습니다:", error);
        }
    }, []);

    useEffect(() => {
        if (typeof window === "undefined") return;
        const data = {
            initialInvestment: state.initialInvestment,
            investmentStyle: state.investmentStyle,
            stocks: state.stocks,
            onboardingForm: state.onboardingForm,
            addStockForm: state.addStockForm,
            onboardingCompleted: state.onboardingCompleted,
        };
        try {
            window.localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
        } catch (error) {
            console.warn("온보딩 정보를 저장하지 못했습니다:", error);
        }
    }, [
        state.initialInvestment,
        state.investmentStyle,
        state.stocks,
        state.onboardingForm,
        state.addStockForm,
        state.onboardingCompleted,
    ]);

    // 페이지 네비게이션 핸들러
    const goToPage = (page: Page) => dispatch({ type: "SET_PAGE", page });

    const handleStart = () => {
        goToPage("onboarding");
    };

    const handleGoToRegister = () => {
        goToPage("register");
    };

    const handleGoToLogin = () => {
        goToPage("login");
    };

    const handleLoginSuccess = async (user: { user_id: number; email: string }) => {
        dispatch({ type: "SET_USER", userId: user.user_id, email: user.email });
        try {
            const userInfo = await api.getUser(user.user_id);
            const completed = Boolean(userInfo?.onboarding_completed);
            dispatch({ type: "SET_ONBOARDING_STATUS", completed });
            if (userInfo?.created_at) {
                dispatch({ type: "SET_USER_CREATED_AT", createdAt: userInfo.created_at });
            }
            if (userInfo?.created_at) {
                dispatch({ type: "SET_USER_CREATED_AT", createdAt: userInfo.created_at });
            }

            if (!completed) {
                goToPage("onboarding");
                return;
            }

            await hydrateStateFromBackend(user.user_id, userInfo);
            goToPage("home");
        } catch (error) {
            console.error("사용자 정보를 불러오지 못했습니다:", error);
        }
    };

    const handleRegisterSuccess = (newUser?: { id: number; email: string; onboarding_completed?: boolean }) => {
        if (newUser?.id) {
            dispatch({ type: "SET_USER", userId: newUser.id, email: newUser.email });
            dispatch({ type: "SET_ONBOARDING_STATUS", completed: Boolean(newUser.onboarding_completed) });
        }
        goToPage("onboarding");
    };

    // 온보딩 플로우 핸들러
    const handleOnboardingStock = (stockName: string) => {
        dispatch({ type: "SET_ONBOARDING_FIELD", field: "stockName", value: stockName });
        goToPage("quantity");
    };

    const handleOnboardingQuantity = (quantity: string) => {
        dispatch({ type: "SET_ONBOARDING_FIELD", field: "quantity", value: quantity });
        goToPage("price");
    };

    const handleOnboardingPrice = (price: string) => {
        dispatch({ type: "SET_ONBOARDING_FIELD", field: "price", value: price });
        goToPage("investment");
    };

    const handleInitialInvestment = (investment: string) => {
        dispatch({ type: "SET_INITIAL_INVESTMENT", value: investment });
        goToPage("style");
    };

    const completeLocalOnboarding = (style: InvestmentStyle) => {
        dispatch({ type: "COMPLETE_ONBOARDING", style });
    };

    const handleStyleSelection = async (style: string) => {
        const selectedStyle = style as InvestmentStyle;
        dispatch({ type: "SET_INVESTMENT_STYLE", style: selectedStyle });

        if (!state.userId) {
            completeLocalOnboarding(selectedStyle);
            return;
        }

        try {
            const backendStyle = mapDisplayStyleToBackend(style);
            if (!backendStyle) {
                completeLocalOnboarding(selectedStyle);
                return;
            }

            // 온보딩 데이터 준비
            const symbol = resolveStockSymbol(state.onboardingForm.stockName);
            const quantity = parsePositiveInteger(state.onboardingForm.quantity);
            const avgPrice = parsePositiveInteger(state.onboardingForm.price);
            const initialInvestment = parsePositiveInteger(state.initialInvestment);

            if (!symbol || quantity === null || avgPrice === null || initialInvestment === null) {
                console.error("온보딩 데이터가 유효하지 않습니다.");
                completeLocalOnboarding(selectedStyle);
                return;
            }

            // 백엔드 온보딩 완료 API 호출
            await api.completeOnboarding(state.userId, {
                initial_investment: initialInvestment,
                investment_style: backendStyle,
                holdings: [{
                    symbol,
                    quantity,
                    avg_price: avgPrice,
                }],
            });

            // 백엔드에서 최신 데이터 가져오기
            await hydrateStateFromBackend(state.userId);
            dispatch({ type: "SET_ONBOARDING_STATUS", completed: true });
            goToPage("home");
        } catch (error) {
            console.error("온보딩 완료 처리 중 오류 발생:", error);
            completeLocalOnboarding(selectedStyle);
        }
    };

    const handleSettingsMenu = (menu: "portfolio" | "stocks" | "logout") => {
        if (menu === "logout") {
            dispatch({ type: "LOGOUT" });
            return;
        }
    };

    // 종목 추가 플로우 핸들러
    const handleAddStock = () => {
        dispatch({ type: "RESET_ADD_STOCK_FORM" });
        goToPage("add-stock");
    };

    const handleAddStockName = (stockName: string) => {
        dispatch({ type: "SET_ADD_STOCK_FIELD", field: "stockName", value: stockName });
        goToPage("add-quantity");
    };

    const handleAddStockQuantity = (quantity: string) => {
        dispatch({ type: "SET_ADD_STOCK_FIELD", field: "quantity", value: quantity });
        goToPage("add-price");
    };

    const handleAddStockPrice = async (price: string) => {
        dispatch({ type: "SET_ADD_STOCK_FIELD", field: "price", value: price });

        const pendingForm: FormData = {
            ...state.addStockForm,
            price,
        };

        if (state.userId) {
            await persistHoldingFromForm(state.userId, pendingForm);
            await hydrateStateFromBackend(state.userId);
        }

        dispatch({ type: "ADD_STOCK" });
    };

    const goBack = (page: Page) => goToPage(page);

    return (
        <div className="bg-white min-h-screen">
            <InvestmentStyleProvider investmentStyle={state.investmentStyle || "공격형"}>
                {state.currentPage === "start" && (
                    <StartScreen
                        onStart={handleStart}
                        onSignUp={handleGoToRegister}
                        onLogin={handleGoToLogin}
                    />
                )}
                {state.currentPage === "login" && (
                    <Login onBack={() => goBack("start")} onSuccess={handleLoginSuccess} />
                )}
                {state.currentPage === "register" && (
                    <Register onBack={() => goBack("start")} onSuccess={handleRegisterSuccess} />
                )}
                {state.currentPage === "onboarding" && (
                    <Onboarding
                        onSubmit={handleOnboardingStock}
                        initialValue={state.onboardingForm.stockName}
                    />
                )}
                {state.currentPage === "quantity" && (
                    <StockQuantityInput
                        stockName={state.onboardingForm.stockName}
                        onBack={() => goBack("onboarding")}
                        onSubmit={handleOnboardingQuantity}
                        initialValue={state.onboardingForm.quantity}
                    />
                )}
                {state.currentPage === "price" && (
                    <StockPriceInput
                        onBack={() => goBack("quantity")}
                        onSubmit={handleOnboardingPrice}
                        initialValue={state.onboardingForm.price}
                    />
                )}
                {state.currentPage === "investment" && (
                    <InitialInvestmentInput
                        onBack={() => goBack("price")}
                        onSubmit={handleInitialInvestment}
                        initialValue={state.initialInvestment}
                    />
                )}
                {state.currentPage === "style" && (
                    <InvestmentStyleSelection
                        onBack={() => goBack("investment")}
                        onSubmit={handleStyleSelection}
                        initialStyle={state.investmentStyle || ""}
                        onStyleChange={(style) =>
                            dispatch({
                                type: "SET_INVESTMENT_STYLE",
                                style: style as InvestmentStyle,
                            })
                        }
                    />
                )}
                {state.currentPage === "home" && (
                    <Home
                        initialInvestment={parseInt(state.initialInvestment) || 0}
                        stocks={state.stocks}
                        onAddStock={handleAddStock}
                        investmentStyle={(state.investmentStyle || "공격형") as InvestmentStyle}
                        onOpenSettings={() => goToPage("settings")}
                        userId={state.userId}
                        userCreatedAt={state.userCreatedAt}
                    />
                )}
                {state.currentPage === "settings" && (
                    <Settings onBack={() => goBack("home")} onSelectMenu={handleSettingsMenu} />
                )}
                {state.currentPage === "add-stock" && (
                    <Onboarding
                        onSubmit={handleAddStockName}
                        onBack={() => goBack("home")}
                        initialValue={state.addStockForm.stockName}
                        title="종목 추가"
                    />
                )}
                {state.currentPage === "add-quantity" && (
                    <StockQuantityInput
                        stockName={state.addStockForm.stockName}
                        onBack={() => goBack("add-stock")}
                        onSubmit={handleAddStockQuantity}
                        initialValue={state.addStockForm.quantity}
                        title="종목 추가"
                    />
                )}
                {state.currentPage === "add-price" && (
                    <StockPriceInput
                        onBack={() => goBack("add-quantity")}
                        onSubmit={handleAddStockPrice}
                        initialValue={state.addStockForm.price}
                        title="종목 추가"
                        submitLabel="완료"
                    />
                )}
            </InvestmentStyleProvider>
        </div>
    );
}
        case "SET_USER_CREATED_AT":
            return { ...state, userCreatedAt: action.createdAt };
