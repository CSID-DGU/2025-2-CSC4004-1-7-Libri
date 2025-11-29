import svgPathsModal from "../imports/svg-ukmyver5y6";

interface IndicatorModalProps {
  indicator: {
    title: string;
    description: string;
    fullDescription: string;
    interpretationPoints: string[];
  } | null;
  onClose: () => void;
}

function ModalHandle() {
  return (
    <div className="bg-white relative rounded-tl-[24px] rounded-tr-[24px] shrink-0 w-full">
      <div className="flex flex-col items-center justify-center overflow-clip rounded-[inherit] size-full">
        <div className="box-border content-stretch flex flex-col gap-[10px] items-center justify-center pb-[12px] pt-[8px] px-[20px] relative w-full">
          <div className="bg-[#dededf] h-[4px] rounded-[80px] shrink-0 w-[48px]" />
        </div>
      </div>
    </div>
  );
}

function CloseIcon() {
  return (
    <div className="relative shrink-0 size-[24px]">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g>
          <path d={svgPathsModal.p1cde9880} fill="#A9ABAD" />
        </g>
      </svg>
    </div>
  );
}

function ModalHeader({ title, onClose }: { title: string; onClose: () => void }) {
  return (
    <div className="bg-white relative shrink-0 w-full">
      <div className="flex flex-row items-center justify-center size-full">
        <div className="box-border content-stretch flex gap-[16px] items-center justify-center px-[20px] py-[8px] relative w-full">
          <div className="basis-0 content-stretch flex flex-col gap-[4px] grow items-center justify-center min-h-px min-w-px relative shrink-0">
            <div className="content-stretch flex gap-[10px] items-center relative shrink-0 w-full">
              <div className="basis-0 flex flex-col grow justify-center leading-[0] min-h-px min-w-px not-italic overflow-ellipsis overflow-hidden relative shrink-0 text-[#1fa9a4] text-nowrap onboarding-top">
                <p className="[white-space-collapse:collapse] leading-[1.55] overflow-ellipsis overflow-hidden">{title}</p>
              </div>
            </div>
          </div>
          <div className="flex flex-row items-center self-stretch">
            <button onClick={onClose} className="box-border content-stretch flex flex-col h-full items-center justify-center overflow-clip p-[2px] relative shrink-0">
              <CloseIcon />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function ModalDivider() {
  return (
    <div className="bg-white box-border content-stretch flex h-px items-center justify-center px-[20px] py-0 relative shrink-0 w-full">
      <div className="basis-0 bg-[#f4f5f5] grow h-full min-h-px min-w-px shrink-0" />
    </div>
  );
}

function ModalHeaderSection({ title, onClose }: { title: string; onClose: () => void }) {
  return (
    <div className="content-stretch flex flex-col items-center justify-center relative shrink-0 w-full">
      <ModalHandle />
      <ModalHeader title={title} onClose={onClose} />
      <div className="bg-white box-border content-stretch flex flex-col gap-[10px] items-center justify-center pb-0 pt-[8px] px-0 relative shrink-0 w-full">
        <ModalDivider />
      </div>
    </div>
  );
}

function InterpretationPoints({ points }: { points: string[] }) {
  return (
    <div className="content-stretch flex flex-col gap-[16px] items-start leading-[0] not-italic relative shrink-0 text-[#444951] w-full">
      <div className="flex flex-col justify-center relative shrink-0 w-full home-stock-name">
        <p className="leading-[1.5]">💡 해석 포인트</p>
      </div>
      <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center relative shrink-0 text-[14px] tracking-[0.14px] w-full">
        <ul className="list-disc">
          {points.map((point, index) => (
            <li key={index} className={`ms-[21px] ${index === points.length - 1 ? '' : 'mb-0'}`}>
              <span className="leading-[1.45]">{point}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

function CloseButton({ onClose }: { onClose: () => void }) {
  return (
    <button onClick={onClose} className="bg-[#1fa9a4] relative rounded-[12px] shrink-0 w-full">
      <div className="flex flex-row items-center justify-center size-full">
        <div className="box-border content-stretch flex gap-[4px] items-center justify-center px-[8px] py-[12px] relative w-full">
          <div className="flex flex-col font-['Pretendard:SemiBold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[16px] text-center text-nowrap text-white tracking-[0.16px]">
            <p className="leading-[1.45] whitespace-pre">닫기</p>
          </div>
        </div>
      </div>
    </button>
  );
}

function ModalContent({ indicator, onClose }: { indicator: IndicatorModalProps['indicator']; onClose: () => void }) {
  if (!indicator) return null;

  return (
    <div className="bg-white relative shrink-0 w-full">
      <div className="flex flex-col items-center overflow-clip rounded-[inherit] size-full">
        <div className="box-border content-stretch flex flex-col gap-[30px] items-center pb-0 pt-[16px] px-[20px] relative w-full">
          <div className="content-stretch flex flex-col gap-[28px] items-start relative shrink-0 w-full">
            <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#444951] text-[14px] tracking-[0.14px] w-full">
              <p className="leading-[1.45]">{indicator.fullDescription}</p>
            </div>
            <InterpretationPoints points={indicator.interpretationPoints} />
          </div>
          <CloseButton onClose={onClose} />
        </div>
      </div>
    </div>
  );
}

export default function IndicatorModal({ indicator, onClose }: IndicatorModalProps) {
  if (!indicator) return null;

  return (
    <>
      {/* 오버레이 */}
      <div 
        className="fixed inset-0 bg-[rgba(0,0,0,0.3)] z-40"
        onClick={onClose}
      />
      
      {/* 모달 */}
      <div className="fixed bottom-0 left-0 right-0 z-50 animate-slide-up flex justify-center">
        <div className="content-stretch flex flex-col items-center relative w-[375px] bg-white rounded-tl-[24px] rounded-tr-[24px]">
          <ModalHeaderSection title={indicator.title} onClose={onClose} />
          <ModalContent indicator={indicator} onClose={onClose} />
        </div>
      </div>
    </>
  );
}
