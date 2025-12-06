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
}

type Action =
    | { type: "SET_PAGE"; page: Page }
    | { type: "SET_ONBOARDING_FIELD"; field: keyof FormData; value: string }
    | { type: "SET_ADD_STOCK_FIELD"; field: keyof FormData; value: string }
    | { type: "SET_INITIAL_INVESTMENT"; value: string }
    | { type: "SET_INVESTMENT_STYLE"; style: InvestmentStyle | "" }
    | { type: "COMPLETE_ONBOARDING"; style: InvestmentStyle }
    | { type: "ADD_STOCK" }
    | { type: "RESET_ADD_STOCK_FORM" }
    | { type: "SET_USER"; userId: number; email: string }
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
        } catch (error) {
            console.error("사용자 정보를 불러오지 못했습니다:", error);
        } finally {
            goToPage("home");
        }
    };

    const handleRegisterSuccess = () => {
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

    const handleStyleSelection = (style: string) => {
        dispatch({ type: "COMPLETE_ONBOARDING", style: style as InvestmentStyle });
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

    const handleAddStockPrice = (price: string) => {
        dispatch({ type: "SET_ADD_STOCK_FIELD", field: "price", value: price });
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
                    />
                )}
            </InvestmentStyleProvider>
        </div>
    );
}
