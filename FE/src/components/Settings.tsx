import Header from "@/components/layout/Header";
import SmallCaretRightIcon from "@/assets/icons/small-caret-right.svg?react";

interface SettingsProps {
    onBack?: () => void;
    onSelectMenu?: (menu: "portfolio" | "stocks" | "logout") => void;
}

interface MenuItem {
    label: string;
    key: "portfolio" | "stocks" | "logout";
}

const menus: MenuItem[] = [
    { label: "포트폴리오 관리", key: "portfolio" },
    { label: "종목 관리", key: "stocks" },
    { label: "로그아웃", key: "logout" },
];

function Divider() {
    return (
        <div className="px-[20px]">
            <div className="h-px w-full" style={{ backgroundColor: "#f6f8fb" }} />
        </div>
    );
}

function MenuButton({ label, onClick }: { label: string; onClick: () => void }) {
    return (
        <button
            type="button"
            onClick={onClick}
            className="flex w-full items-center justify-between transition-colors hover:text-[#1fa9a4]"
            style={{ paddingInline: "20px", paddingBlock: "20px" }}
        >
            <span className="title-3 text-[#151b26]">{label}</span>
            <SmallCaretRightIcon className="h-5 w-5 text-[#151b26]" />
        </button>
    );
}

export default function Settings({ onBack, onSelectMenu }: SettingsProps) {
    const handleSelect = (menu: MenuItem["key"]) => {
        onSelectMenu?.(menu);
    };

    return (
        <div className="relative min-h-screen w-full bg-white">
            <div className="absolute content-stretch flex flex-col items-start left-1/2 top-[52px] translate-x-[-50%] w-full max-w-[375px]">
                <div className="flex w-full flex-col" style={{ gap: "12px" }}>
                    <Header title="설정" onBack={onBack} />
                    <div className="w-full px-5 pb-6">
                        <div className="rounded-2xl border border-[#f0f1f3] bg-[#fdfefe] px-4">
                            {menus.map((item, index) => (
                                <div key={item.key}>
                                    <MenuButton label={item.label} onClick={() => handleSelect(item.key)} />
                                    {index < menus.length - 1 && <Divider />}
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
