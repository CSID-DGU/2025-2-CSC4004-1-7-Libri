import Header from "@/components/layout/Header";
import CaretLeftIcon from "@/assets/icons/caret-left.svg?react";

interface SettingsProps {
    onBack?: () => void;
    onSelectMenu?: (menu: "portfolio" | "stocks" | "logout") => void;
}

interface MenuItem {
    label: string;
    key: "portfolio" | "stocks" | "logout";
}

const menus: MenuItem[] = [
    { label: "내 포트폴리오 관리", key: "portfolio" },
    { label: "종목 관리", key: "stocks" },
    { label: "로그아웃", key: "logout" },
];

function Divider() {
    return <div className="h-px w-full bg-[#ebecef]" />;
}

function MenuButton({ label, onClick }: { label: string; onClick: () => void }) {
    return (
        <button
            type="button"
            onClick={onClick}
            className="flex w-full items-center justify-between px-1 py-4 transition-colors hover:text-[#1fa9a4]"
        >
            <span className="title-3 text-[#151b26]">{label}</span>
            <CaretLeftIcon className="h-5 w-5 text-[#c9cbd0] rotate-180" />
        </button>
    );
}

export default function Settings({ onBack, onSelectMenu }: SettingsProps) {
    const handleSelect = (menu: MenuItem["key"]) => {
        onSelectMenu?.(menu);
    };

    return (
        <div className="relative min-h-screen w-full bg-white">
            <Header title="설정" onBack={onBack} />
            <div className="mx-auto flex w-full max-w-[375px] flex-col gap-0 px-5 py-6">
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
    );
}
