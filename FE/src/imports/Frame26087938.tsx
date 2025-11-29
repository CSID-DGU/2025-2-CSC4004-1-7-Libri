import svgPaths from "./svg-ukmyver5y6";

function Component() {
  return (
    <div className="bg-white relative rounded-tl-[24px] rounded-tr-[24px] shrink-0 w-full" data-name="모달 상단 엘리먼트">
      <div className="flex flex-col items-center justify-center overflow-clip rounded-[inherit] size-full">
        <div className="box-border content-stretch flex flex-col gap-[10px] items-center justify-center pb-[12px] pt-[8px] px-[20px] relative w-full">
          <div className="bg-[#dededf] h-[4px] rounded-[80px] shrink-0 w-[48px]" />
        </div>
      </div>
    </div>
  );
}

function Frame() {
  return (
    <div className="content-stretch flex gap-[10px] items-center relative shrink-0 w-full">
      <div className="basis-0 flex flex-col font-['Pretendard:Bold',sans-serif] grow justify-center leading-[0] min-h-px min-w-px not-italic overflow-ellipsis overflow-hidden relative shrink-0 text-[#1fa9a4] text-[18px] text-nowrap">
        <p className="[white-space-collapse:collapse] leading-[1.55] overflow-ellipsis overflow-hidden">EMA (12/26)</p>
      </div>
    </div>
  );
}

function Frame2() {
  return (
    <div className="basis-0 content-stretch flex flex-col gap-[4px] grow items-center justify-center min-h-px min-w-px relative shrink-0">
      <Frame />
    </div>
  );
}

function Close() {
  return (
    <div className="relative shrink-0 size-[24px]" data-name="close">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g>
          <path d={svgPaths.p1cde9880} fill="var(--fill-0, #A9ABAD)" id="Vector" />
        </g>
      </svg>
    </div>
  );
}

function Frame1() {
  return (
    <div className="box-border content-stretch flex flex-col h-full items-center justify-center overflow-clip p-[2px] relative shrink-0">
      <Close />
    </div>
  );
}

function Component1() {
  return (
    <div className="bg-white relative shrink-0 w-full" data-name="모달 상단 텍스트">
      <div className="flex flex-row items-center justify-center size-full">
        <div className="box-border content-stretch flex gap-[16px] items-center justify-center px-[20px] py-[8px] relative w-full">
          <Frame2 />
          <div className="flex flex-row items-center self-stretch">
            <Frame1 />
          </div>
        </div>
      </div>
    </div>
  );
}

function Component2() {
  return (
    <div className="bg-white box-border content-stretch flex h-px items-center justify-center px-[20px] py-0 relative shrink-0 w-[375px]" data-name="디바이더">
      <div className="basis-0 bg-[#f4f5f5] grow h-full min-h-px min-w-px shrink-0" />
    </div>
  );
}

function Component3() {
  return (
    <div className="bg-white box-border content-stretch flex flex-col gap-[10px] items-center justify-center pb-0 pt-[8px] px-0 relative shrink-0 w-full" data-name="모달 상단 구분선">
      <Component2 />
    </div>
  );
}

function Component4() {
  return (
    <div className="content-stretch flex flex-col items-center justify-center relative shrink-0 w-full" data-name="모달 상단">
      <Component />
      <Component1 />
      <Component3 />
    </div>
  );
}

function Frame5() {
  return (
    <div className="content-stretch flex flex-col gap-[16px] items-start leading-[0] not-italic relative shrink-0 text-[#444951] w-full">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center relative shrink-0 text-[16px] tracking-[0.16px] w-full">
        <p className="leading-[1.5]">💡 해석 포인트</p>
      </div>
      <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center relative shrink-0 text-[14px] tracking-[0.14px] w-full">
        <ul className="list-disc">
          <li className="mb-0 ms-[21px]">
            <span className="leading-[1.45]">단기(EMA12)가 장기(EMA26)를 뚫으면 상승 신호</span>
          </li>
          <li className="ms-[21px]">
            <span className="leading-[1.45]">반대로 내려가면 하락 신호</span>
          </li>
        </ul>
      </div>
    </div>
  );
}

function Frame6() {
  return (
    <div className="content-stretch flex flex-col gap-[28px] items-start relative shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#444951] text-[14px] tracking-[0.14px] w-full">
        <p className="leading-[1.45]">EMA(지수이동평균선)은 최근 가격에 더 큰 비중을 두고 계산한 평균선이에요. 숫자(12, 26)는 며칠 동안의 평균을 의미합니다.</p>
      </div>
      <Frame5 />
    </div>
  );
}

function Component5() {
  return (
    <div className="bg-[#1fa9a4] relative rounded-[12px] shrink-0 w-full" data-name="영역 헤더 우측 버튼">
      <div className="flex flex-row items-center justify-center size-full">
        <div className="box-border content-stretch flex gap-[4px] items-center justify-center px-[8px] py-[12px] relative w-full">
          <div className="flex flex-col font-['Pretendard:SemiBold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[16px] text-center text-nowrap text-white tracking-[0.16px]">
            <p className="leading-[1.45] whitespace-pre">닫기</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function Frame3() {
  return (
    <div className="bg-white relative shrink-0 w-full">
      <div className="flex flex-col items-center overflow-clip rounded-[inherit] size-full">
        <div className="box-border content-stretch flex flex-col gap-[30px] items-center pb-0 pt-[16px] px-[20px] relative w-full">
          <Frame6 />
          <Component5 />
        </div>
      </div>
    </div>
  );
}

export default function Frame4() {
  return (
    <div className="content-stretch flex flex-col items-center relative size-full">
      <Component4 />
      <Frame3 />
    </div>
  );
}