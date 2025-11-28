import svgPaths from "./svg-crvmew88jg";

function CaretLeft() {
  return (
    <div className="relative shrink-0 size-[24px]" data-name="caret-left">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g id="caret-left">
          <path d={svgPaths.p21f93bf0} fill="var(--fill-0, #686B6D)" id="Vector" />
        </g>
      </svg>
    </div>
  );
}

function Component() {
  return (
    <div className="box-border content-stretch flex gap-[10px] items-center p-[4px] relative shrink-0" data-name="상단 헤더 좌측 버튼">
      <CaretLeft />
    </div>
  );
}

function Frame() {
  return (
    <div className="content-stretch flex gap-[10px] items-center relative shrink-0 w-[68px]">
      <Component />
    </div>
  );
}

function Component1() {
  return (
    <div className="basis-0 grow min-h-px min-w-px relative shrink-0" data-name="헤더 타이틀">
      <div className="flex flex-row items-center justify-center size-full">
        <div className="box-border content-stretch flex gap-[10px] items-center justify-center px-[4px] py-[2px] relative w-full">
          <div className="basis-0 flex flex-col font-['Pretendard:Bold',sans-serif] grow justify-center leading-[0] min-h-px min-w-px not-italic overflow-ellipsis overflow-hidden relative shrink-0 text-[#3e3f40] text-[18px] text-center text-nowrap">
            <p className="[white-space-collapse:collapse] leading-[1.55] overflow-ellipsis overflow-hidden">시작하기</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function Component2() {
  return <div className="h-[32px] shrink-0 w-[68px]" data-name="상단 헤더 우측 버튼" />;
}

function Frame1() {
  return (
    <div className="absolute content-stretch flex items-center justify-center left-[16px] right-[16px] top-1/2 translate-y-[-50%]">
      <Frame />
      <Component1 />
      <Component2 />
    </div>
  );
}

function Component3() {
  return (
    <div className="bg-white h-[58px] relative shrink-0 w-[375px]" data-name="상단 헤더">
      <Frame1 />
    </div>
  );
}

function Frame2() {
  return (
    <div className="content-stretch flex flex-col gap-[4px] items-start justify-center leading-[0] not-italic relative shrink-0 text-nowrap w-full">
      <div className="flex flex-col justify-center relative shrink-0 text-[#151b26] onboaring-big">
        <p className="leading-[1.6] text-nowrap whitespace-pre">초기투자금을 입력해 주세요</p>
      </div>
      <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center relative shrink-0 text-[#a1a4a8] text-[12px] tracking-[0.24px]">
        <p className="leading-[1.5] text-nowrap whitespace-pre">AI가 맞춤형 분석을 제공하는 데에 필요한 정보예요.</p>
      </div>
    </div>
  );
}

function Frame3() {
  return (
    <div className="basis-0 content-stretch flex flex-col gap-[2px] grow items-start justify-center min-h-px min-w-px relative shrink-0">
      <Frame2 />
    </div>
  );
}

function Component4() {
  return (
    <div className="relative shrink-0 w-full" data-name="리스트 헤더">
      <div className="flex flex-row items-center justify-center size-full">
        <div className="box-border content-stretch flex gap-[16px] items-center justify-center px-[20px] py-0 relative w-full">
          <Frame3 />
        </div>
      </div>
    </div>
  );
}

function Frame9() {
  return (
    <div className="content-stretch flex gap-[6px] items-center relative shrink-0">
      <div className="flex flex-col font-['Pretendard:SemiBold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[14px] text-center text-nowrap tracking-[0.14px]">
        <p className="leading-[1.45] whitespace-pre">초기투자금</p>
      </div>
    </div>
  );
}

function Frame10() {
  return (
    <div className="content-stretch flex gap-[6px] items-center relative shrink-0">
      <Frame9 />
    </div>
  );
}

function Component5() {
  return (
    <div className="basis-0 bg-[#f2f4f8] grow min-h-px min-w-px relative rounded-[8px] shrink-0" data-name="영역 헤더 우측 버튼">
      <div className="flex flex-row items-center size-full">
        <div className="box-border content-stretch flex items-center p-[12px] relative w-full">
          <Frame10 />
        </div>
      </div>
    </div>
  );
}

function Frame6() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="flex flex-row items-center justify-center size-full">
        <div className="box-border content-stretch flex gap-[10px] items-center justify-center px-[20px] py-0 relative w-full">
          <Component5 />
          <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[21px] text-center text-nowrap">
            <p className="leading-[1.6] whitespace-pre">원</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function Frame8() {
  return (
    <div className="content-stretch flex flex-col gap-[20px] items-start relative shrink-0 w-full">
      <Component4 />
      <Frame6 />
    </div>
  );
}

function Frame5() {
  return (
    <div className="box-border content-stretch flex flex-col gap-[24px] items-center justify-center px-0 py-[16px] relative shrink-0 w-full">
      <Frame8 />
    </div>
  );
}

function Frame4() {
  return (
    <div className="absolute content-stretch flex flex-col items-start left-1/2 top-[52px] translate-x-[-50%] w-[375px]">
      <Component3 />
      <Frame5 />
    </div>
  );
}

function Component6() {
  return (
    <div className="bg-[#d0d1d4] relative rounded-[8px] shrink-0 w-full" data-name="영역 헤더 우측 버튼">
      <div className="flex flex-row items-center justify-center size-full">
        <div className="box-border content-stretch flex gap-[2px] items-center justify-center px-[8px] py-[12px] relative w-full">
          <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[16px] text-center text-nowrap text-white tracking-[0.16px]">
            <p className="leading-[1.5] whitespace-pre">다음</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function Frame7() {
  return (
    <div className="absolute bottom-[50px] box-border content-stretch flex flex-col gap-[10px] items-start left-0 px-[20px] py-0 w-[375px]">
      <Component6 />
    </div>
  );
}

function Bar() {
  return (
    <div className="absolute bottom-[8px] h-[5px] left-[120px] right-[121px]" data-name="Bar">
      <div className="absolute bg-[#151b26] inset-0 rounded-[10px]" data-name="Base" />
    </div>
  );
}

function IOsHomeBar() {
  return (
    <div className="absolute bottom-0 h-[34px] left-0 overflow-clip right-0" data-name="iOS_Home Bar">
      <Bar />
    </div>
  );
}

function Notch() {
  return <div className="absolute h-[30px] left-0 right-0 top-0" data-name="Notch" />;
}

function NetworkSignalLight() {
  return (
    <div className="h-[14px] relative shrink-0 w-[20px]" data-name="Network Signal / Light">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 20 14">
        <g id="Network Signal /Â Light">
          <path clipRule="evenodd" d={svgPaths.p1f162900} fill="var(--fill-0, #D1D1D6)" fillRule="evenodd" id="Path" />
          <path clipRule="evenodd" d={svgPaths.p1d5dbe40} fill="var(--fill-0, #D1D1D6)" fillRule="evenodd" id="Path_2" />
          <path clipRule="evenodd" d={svgPaths.p18019e00} fill="var(--fill-0, #D1D1D6)" fillRule="evenodd" id="Path_3" />
          <path clipRule="evenodd" d={svgPaths.p342c3400} fill="var(--fill-0, #3C3C43)" fillOpacity="0.18" fillRule="evenodd" id="Empty Bar" />
          <path clipRule="evenodd" d={svgPaths.p1f162900} fill="var(--fill-0, black)" fillRule="evenodd" id="Path_4" />
          <path clipRule="evenodd" d={svgPaths.p1d5dbe40} fill="var(--fill-0, black)" fillRule="evenodd" id="Path_5" />
          <path clipRule="evenodd" d={svgPaths.p18019e00} fill="var(--fill-0, black)" fillRule="evenodd" id="Path_6" />
        </g>
      </svg>
    </div>
  );
}

function WiFiSignalLight() {
  return (
    <div className="h-[14px] relative shrink-0 w-[16px]" data-name="WiFi Signal / Light">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 16 14">
        <g id="WiFi Signal / Light">
          <path d={svgPaths.p3dc48e00} fill="var(--fill-0, black)" id="Path" />
          <path d={svgPaths.p3b3c95f0} fill="var(--fill-0, black)" id="Path_2" />
          <path d={svgPaths.p932c700} fill="var(--fill-0, black)" id="Path_3" />
        </g>
      </svg>
    </div>
  );
}

function BatteryLight() {
  return (
    <div className="h-[14px] relative shrink-0 w-[25px]" data-name="Battery / Light">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 25 14">
        <g id="Battery / Light">
          <path d={svgPaths.p5709d00} fill="var(--fill-0, #3C3C43)" fillOpacity="0.6" id="Rectangle 23" />
          <path clipRule="evenodd" d={svgPaths.p2587880} fill="var(--fill-0, #3C3C43)" fillOpacity="0.6" fillRule="evenodd" id="Rectangle 21 (Stroke)" />
          <rect fill="var(--fill-0, black)" height="8" id="Rectangle 20" rx="1" width="19" x="2" y="3" />
        </g>
      </svg>
    </div>
  );
}

function StatusIcons() {
  return (
    <div className="absolute content-stretch flex gap-[4px] items-center right-[14px] top-[16px]" data-name="Status Icons">
      <NetworkSignalLight />
      <WiFiSignalLight />
      <BatteryLight />
    </div>
  );
}

function Indicator() {
  return (
    <div className="absolute right-[71px] size-[6px] top-[8px]" data-name="Indicator">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 6 6">
        <g id="Indicator"></g>
      </svg>
    </div>
  );
}

function Component8() {
  return (
    <div className="absolute h-[15px] left-[calc(50%+0.5px)] top-1/2 translate-x-[-50%] translate-y-[-50%] w-[33px]" data-name="9:41">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 33 15">
        <g id="9:41">
          <g id="9:41_2">
            <path d={svgPaths.p309cf100} fill="var(--fill-0, black)" />
            <path d={svgPaths.p1285b880} fill="var(--fill-0, black)" />
            <path d={svgPaths.pa9bea00} fill="var(--fill-0, black)" />
            <path d={svgPaths.p1d3f77f0} fill="var(--fill-0, black)" />
          </g>
        </g>
      </svg>
    </div>
  );
}

function TimeLight() {
  return (
    <div className="absolute h-[21px] left-[21px] overflow-clip rounded-[20px] top-[12px] w-[54px]" data-name="Time / Light">
      <Component8 />
    </div>
  );
}

function IOsStatusBar() {
  return (
    <div className="absolute bg-white h-[44px] left-0 overflow-clip right-0 top-0" data-name="iOS_Status Bar">
      <Notch />
      <StatusIcons />
      <Indicator />
      <TimeLight />
    </div>
  );
}

export default function Component7() {
  return (
    <div className="bg-white relative size-full" data-name="온보딩">
      <IOsStatusBar />
      <Frame4 />
      <Frame7 />
      <IOsHomeBar />
    </div>
  );
}