import LogoIcon from "@/assets/icons/logo.svg?react";

interface StartScreenProps {
    onStart: () => void;
    onSignUp?: () => void;
    onLogin?: () => void;
}

export default function StartScreen({ onStart, onSignUp, onLogin }: StartScreenProps) {
    return (
        <div className="bg-white relative size-full min-h-screen flex flex-col items-center px-6 pt-12 pb-[140px]">
            <div className="flex-1 flex flex-col items-center justify-center gap-4 text-center w-full max-w-[375px]">
                <LogoIcon style={{ width: 100, height: 100 }} />
                <p
                    className="component-main leading-[1.2]"
                    style={{ fontSize: 40, fontWeight: 600, marginTop: 24 }}
                >
                    리브리
                </p>
                <p
                    className="font-semibold"
                    style={{ fontSize: 18, color: "var(--achromatic-500)", marginTop: 8 }}
                >
                    AI 주식 예측 서비스
                </p>
            </div>
            <div className="absolute bottom-[50px] left-1/2 translate-x-[-50%] w-full max-w-[375px] px-6">
                <button
                    type="button"
                    onClick={onLogin ?? onStart}
                    className="relative rounded-[8px] shrink-0 w-full transition-colors bg-[#1FA9A4]"
                    style={{ width: "calc(100% - 40px)", marginInline: 20 }}
                >
                    <div className="flex flex-row items-center justify-center size-full">
                        <div className="box-border content-stretch flex gap-[2px] items-center justify-center px-[8px] py-[12px] relative w-full">
                            <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[16px] text-center text-nowrap text-white tracking-[0.16px]">
                                <p className="leading-[1.5] title-3 whitespace-pre">로그인</p>
                            </div>
                        </div>
                    </div>
                </button>
                <button
                    type="button"
                    onClick={onSignUp}
                    className="underline title-3 text-center w-full"
                    style={{
                        color: "var(--achromatic-500)",
                        marginTop: 16,
                        width: "calc(100% - 40px)",
                        marginInline: 20,
                    }}
                >
                    회원가입하기
                </button>
            </div>
        </div>
    );
}
