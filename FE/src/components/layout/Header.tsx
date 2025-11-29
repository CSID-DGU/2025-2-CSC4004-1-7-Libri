import { type ComponentType, type ReactNode, type SVGProps } from "react";
import CaretLeftIcon from "@/assets/icons/caret-left.svg?react";

type IconComponent = ComponentType<SVGProps<SVGSVGElement>>;

interface HeaderProps {
    title: string;
    onBack?: () => void;
    leftSlot?: ReactNode;
    rightSlot?: ReactNode;
    leftIcon?: IconComponent | null;
    rightIcon?: IconComponent | null;
    onLeftIconClick?: () => void;
    onRightIconClick?: () => void;
    leftIconAriaLabel?: string;
    rightIconAriaLabel?: string;
    className?: string;
}

function IconButton({
    Icon,
    onClick,
    ariaLabel,
    className,
}: {
    Icon: IconComponent;
    onClick?: () => void;
    ariaLabel?: string;
    className?: string;
}) {
    return (
        <button
            type="button"
            onClick={onClick}
            aria-label={ariaLabel}
            className="box-border flex items-center justify-center rounded-full p-1 transition-colors hover:bg-[#f2f4f8]"
        >
            <Icon className={className ?? "w-6 h-6 achromatic-600"} />
        </button>
    );
}

export function Header({
    title,
    onBack,
    leftSlot,
    rightSlot,
    leftIcon,
    rightIcon,
    onLeftIconClick,
    onRightIconClick,
    leftIconAriaLabel,
    rightIconAriaLabel,
    className = "",
}: HeaderProps) {
    const resolvedLeftIcon = leftIcon === undefined ? (onBack ? CaretLeftIcon : null) : leftIcon;

    const renderLeft = () => {
        if (leftSlot !== undefined) return leftSlot;
        if (!resolvedLeftIcon) return null;
        return (
            <IconButton
                Icon={resolvedLeftIcon}
                onClick={onLeftIconClick ?? onBack}
                ariaLabel={leftIconAriaLabel ?? "뒤로가기"}
            />
        );
    };

    const renderRight = () => {
        if (rightSlot !== undefined) return rightSlot;
        if (!rightIcon) return null;
        return (
            <IconButton
                Icon={rightIcon}
                onClick={onRightIconClick}
                ariaLabel={rightIconAriaLabel ?? "우측 버튼"}
            />
        );
    };

    return (
        <header className={`bg-white h-[58px] w-full ${className}`} data-name="상단 헤더">
            <div className="mx-auto flex size-full max-w-[375px] items-center justify-between px-4">
                <div className="flex w-[68px] justify-start">{renderLeft()}</div>
                <div className="flex flex-1 items-center justify-center px-1">
                    <p className="onboarding-top text-center text-[#3e3f40] leading-[1.55]">
                        {title}
                    </p>
                </div>
                <div className="flex w-[68px] justify-end">{renderRight()}</div>
            </div>
        </header>
    );
}

export default Header;
