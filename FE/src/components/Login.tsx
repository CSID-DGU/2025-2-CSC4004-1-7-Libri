import { useState } from "react";
import Header from "@/components/layout/Header";
import CloseCircleIcon from "@/assets/icons/close-circle.svg?react";
import EyeIcon from "@/assets/icons/eye.svg?react";
import EyeSlashIcon from "@/assets/icons/eye-slash.svg?react";

interface LoginProps {
    onBack: () => void;
    onSubmit?: (data: { email: string; password: string }) => Promise<boolean> | boolean;
}

export default function Login({ onBack, onSubmit }: LoginProps) {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState("");
    const [submitting, setSubmitting] = useState(false);

    const canSubmit = email.trim().length > 0 && password.trim().length > 0 && !submitting;

    const handleSubmit = async () => {
        if (!canSubmit) return;
        setError("");
        setSubmitting(true);
        try {
            const result = await onSubmit?.({ email: email.trim(), password: password.trim() });
            if (result === false) {
                setError("이메일 주소 또는 비밀번호가 일치하지 않습니다.");
            }
        } catch {
            setError("이메일 주소 또는 비밀번호가 일치하지 않습니다.");
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="bg-white relative size-full min-h-screen" data-name="로그인">
            <div className="absolute content-stretch flex flex-col items-start left-1/2 top-[52px] translate-x-[-50%] w-full max-w-[375px]">
                <Header title="로그인" onBack={onBack} />

                <div
                    className="flex w-full flex-col"
                    style={{ gap: "24px", marginTop: "16px", paddingInline: "20px" }}
                >
                    <div className="flex flex-col" style={{ gap: "8px" }}>
                        <label
                            className="body-3"
                            htmlFor="login-email"
                            style={{ color: "var(--achromatic-500)" }}
                        >
                            이메일 주소
                        </label>
                        <div className="relative">
                            <input
                                id="login-email"
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="example@libri.com"
                                autoComplete="email"
                                className="w-full rounded-[8px] label-1 text-achromatic-800 tracking-[0.14px] outline-none placeholder-body-2 placeholder-achromatic-500"
                                style={{
                                    paddingInline: "12px",
                                    paddingBlock: "12px",
                                    paddingRight: "40px",
                                    backgroundColor: "var(--component-background)",
                                }}
                            />
                            {email.trim().length > 0 && (
                                <button
                                    type="button"
                                    onClick={() => setEmail("")}
                                    aria-label="입력 내용 지우기"
                                    className="flex items-center justify-center"
                                    style={{
                                        position: "absolute",
                                        top: "50%",
                                        right: "8px",
                                        transform: "translateY(-50%)",
                                    }}
                                >
                                    <CloseCircleIcon
                                        style={{
                                            color: "var(--achromatic-500)",
                                            width: "20px",
                                            height: "20px",
                                        }}
                                    />
                                </button>
                            )}
                        </div>
                    </div>
                    <div className="flex flex-col" style={{ gap: "8px" }}>
                        <label
                            className="body-3"
                            htmlFor="login-password"
                            style={{ color: "var(--achromatic-500)" }}
                        >
                            비밀번호
                        </label>
                        <div className="relative">
                            <input
                                id="login-password"
                                type={showPassword ? "text" : "password"}
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="비밀번호"
                                autoComplete="current-password"
                                className="w-full rounded-[8px] label-1 text-achromatic-800 tracking-[0.14px] outline-none placeholder-body-2 placeholder-achromatic-500"
                                style={{
                                    paddingInline: "12px",
                                    paddingBlock: "12px",
                                    paddingRight: "40px",
                                    backgroundColor: "var(--component-background)",
                                }}
                            />
                            {password.length > 0 && (
                                <button
                                    type="button"
                                    onClick={() => setShowPassword((prev) => !prev)}
                                    aria-label={showPassword ? "비밀번호 숨기기" : "비밀번호 표시"}
                                    className="flex items-center justify-center"
                                    style={{
                                        position: "absolute",
                                        top: "50%",
                                        right: "8px",
                                        transform: "translateY(-50%)",
                                    }}
                                >
                                    {showPassword ? (
                                        <EyeSlashIcon
                                            style={{ width: "20px", height: "20px", color: "var(--achromatic-500)" }}
                                        />
                                    ) : (
                                        <EyeIcon
                                            style={{ width: "20px", height: "20px", color: "var(--achromatic-500)" }}
                                        />
                                    )}
                                </button>
                            )}
                        </div>
                        {error && (
                            <p className="body-3" style={{ color: "var(--component-red)" }}>
                                {error}
                            </p>
                        )}
                    </div>
                </div>
            </div>

            <div className="absolute bottom-[50px] box-border content-stretch flex flex-col gap-[16px] items-start left-1/2 translate-x-[-50%] px-[20px] py-0 w-full max-w-[375px]">
                <button
                    onClick={handleSubmit}
                    disabled={!canSubmit}
                    className={`${
                        canSubmit ? "bg-[#1FA9A4]" : "bg-[#d0d1d4]"
                    } relative rounded-[8px] shrink-0 w-full transition-colors disabled:cursor-not-allowed`}
                >
                    <div className="flex flex-row items-center justify-center size-full">
                        <div className="box-border content-stretch flex gap-[2px] items-center justify-center px-[8px] py-[12px] relative w-full">
                            <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[16px] text-center text-nowrap text-white tracking-[0.16px]">
                                <p className="leading-[1.5] whitespace-pre">로그인</p>
                            </div>
                        </div>
                    </div>
                </button>
            </div>
        </div>
    );
}
