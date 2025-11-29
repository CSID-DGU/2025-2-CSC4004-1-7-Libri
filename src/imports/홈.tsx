import svgPaths from "./svg-lgulmg48dh";
import imgFrame26089667 from "figma:asset/bdac4e7d8d4f71d5aef6253221470dffe73bb6a6.png";

function Logo() {
  return (
    <div className="relative shrink-0 size-[28px]" data-name="Logo">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 28 28">
        <g id="Logo">
          <rect fill="var(--fill-0, #1FA9A4)" height="28" rx="8.75" width="28" />
          <path d={svgPaths.p34c52f00} fill="var(--fill-0, #F2F4F8)" id="Exclude" />
        </g>
      </svg>
    </div>
  );
}

function Settings() {
  return (
    <div className="relative shrink-0 size-[24px]" data-name="settings">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g id="settings">
          <path clipRule="evenodd" d={svgPaths.p5a876f0} fill="var(--fill-0, #A1A4A8)" fillRule="evenodd" id="Vector" />
        </g>
      </svg>
    </div>
  );
}

function Frame15() {
  return (
    <div className="content-stretch flex gap-[8px] items-center justify-center relative shrink-0 w-full">
      <Logo />
      <div className="basis-0 flex flex-col font-['Pretendard:Bold',sans-serif] grow justify-center leading-[0] min-h-px min-w-px not-italic relative shrink-0 text-[#3e3f40] text-[28px]">
        <p className="leading-[1.7]">리브리</p>
      </div>
      <Settings />
    </div>
  );
}

function Frame13() {
  return (
    <div className="basis-0 content-stretch flex flex-col grow h-full items-center justify-center min-h-px min-w-px relative shrink-0">
      <Frame15 />
    </div>
  );
}

function Frame14() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="flex flex-row items-center justify-center size-full">
        <div className="box-border content-stretch flex gap-[16px] items-center justify-center px-[20px] py-0 relative w-full">
          <div className="basis-0 flex flex-row grow items-center self-stretch shrink-0">
            <Frame13 />
          </div>
        </div>
      </div>
    </div>
  );
}

function Ai() {
  return (
    <div className="relative shrink-0 size-[18px]" data-name="AI">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 18 18">
        <g id="AI">
          <path clipRule="evenodd" d={svgPaths.p1036f280} fill="var(--fill-0, #1FA9A4)" fillRule="evenodd" id="Vector" />
        </g>
      </svg>
    </div>
  );
}

function Frame4() {
  return (
    <div className="content-stretch flex gap-[4px] items-center relative shrink-0 w-full">
      <Ai />
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#1fa9a4] text-[16px] text-nowrap tracking-[0.16px]">
        <p className="leading-[1.5] whitespace-pre">AI 투자 현황</p>
      </div>
    </div>
  );
}

function Frame5() {
  return (
    <div className="basis-0 content-stretch flex flex-col gap-[2px] grow items-start justify-center min-h-px min-w-px relative shrink-0">
      <Frame4 />
    </div>
  );
}

function Component() {
  return (
    <div className="content-stretch flex gap-[16px] items-center justify-center relative shrink-0 w-full" data-name="리스트 헤더">
      <Frame5 />
    </div>
  );
}

function Frame8() {
  return (
    <div className="basis-0 content-stretch flex font-['Pretendard:Medium',sans-serif] gap-[4px] grow items-center leading-[0] min-h-px min-w-px not-italic relative shrink-0 text-nowrap tracking-[0.16px]">
      <div className="flex flex-col justify-center relative shrink-0 text-[#151b26] text-[16px]">
        <p className="leading-[1.5] text-nowrap whitespace-pre">리브리가</p>
      </div>
      <div className="flex flex-col justify-center relative shrink-0 text-[#1fa9a4] text-[0px]">
        <p className="font-['Pretendard:Bold',sans-serif] leading-[1.5] not-italic text-[16px] text-nowrap tracking-[0.16px] whitespace-pre">10,000,000</p>
      </div>
      <div className="flex flex-col justify-center relative shrink-0 text-[#151b26] text-[16px]">
        <p className="leading-[1.5] text-nowrap whitespace-pre">으로</p>
      </div>
    </div>
  );
}

function Frame9() {
  return (
    <div className="content-stretch flex gap-[2px] items-center relative shrink-0 w-full">
      <Frame8 />
    </div>
  );
}

function Frame10() {
  return (
    <div className="basis-0 content-stretch flex font-['Pretendard:Medium',sans-serif] gap-[4px] grow items-center leading-[0] min-h-px min-w-px not-italic relative shrink-0 tracking-[0.16px]">
      <div className="flex flex-col justify-center relative shrink-0 text-[#151b26] text-[16px] text-nowrap">
        <p className="leading-[1.5] whitespace-pre">총 수익률</p>
      </div>
      <div className="flex flex-col justify-center relative shrink-0 text-[#f3646f] text-[0px] text-nowrap">
        <p className="font-['Pretendard:Bold',sans-serif] leading-[1.5] not-italic text-[16px] tracking-[0.16px] whitespace-pre">+46,043 (7.8%)</p>
      </div>
      <div className="basis-0 flex flex-col grow justify-center min-h-px min-w-px relative shrink-0 text-[#151b26] text-[16px]">
        <p className="leading-[1.5]">을 내고 있어요.</p>
      </div>
    </div>
  );
}

function Frame6() {
  return (
    <div className="content-stretch flex gap-[2px] items-center relative shrink-0 w-full">
      <Frame10 />
    </div>
  );
}

function Frame23() {
  return (
    <div className="content-stretch flex flex-col items-center justify-center relative shrink-0 w-full">
      <Frame9 />
      <Frame6 />
    </div>
  );
}

function Frame21() {
  return (
    <div className="bg-[rgba(31,169,164,0.08)] relative rounded-[16px] shrink-0 w-full">
      <div className="flex flex-col justify-center size-full">
        <div className="box-border content-stretch flex flex-col gap-[10px] items-start justify-center p-[20px] relative w-full">
          <Component />
          <Frame23 />
          <div className="flex flex-col font-['Pretendard:SemiBold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#b9bbbe] text-[11px] text-nowrap tracking-[0.22px]">
            <p className="leading-[1.45] whitespace-pre">*실제 투자 환경 데이터 기반, AI가 시뮬레이션한 수익률입니다.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function Component1() {
  return (
    <div className="relative shrink-0 w-full" data-name="리스트 헤더">
      <div className="flex flex-col items-center justify-center size-full">
        <div className="box-border content-stretch flex flex-col gap-[4px] items-center justify-center px-[20px] py-0 relative w-full">
          <Frame21 />
        </div>
      </div>
    </div>
  );
}

function Frame25() {
  return (
    <div className="content-stretch flex flex-col gap-[10px] items-start relative shrink-0 w-full">
      <Component1 />
    </div>
  );
}

function Frame11() {
  return (
    <div className="content-stretch flex gap-[4px] items-center relative shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[16px] text-nowrap tracking-[0.16px]">
        <p className="leading-[1.5] whitespace-pre">종목별 상세</p>
      </div>
    </div>
  );
}

function Frame12() {
  return (
    <div className="basis-0 content-stretch flex flex-col gap-[2px] grow items-start justify-center min-h-px min-w-px relative shrink-0">
      <Frame11 />
    </div>
  );
}

function Component2() {
  return (
    <div className="relative shrink-0 w-full" data-name="리스트 헤더">
      <div className="flex flex-row items-center justify-center size-full">
        <div className="box-border content-stretch flex gap-[16px] items-center justify-center px-[20px] py-0 relative w-full">
          <Frame12 />
        </div>
      </div>
    </div>
  );
}

function Frame17() {
  return (
    <div className="aspect-[36/36] relative rounded-[100px] self-stretch shrink-0">
      <img alt="" className="absolute inset-0 max-w-none object-50%-50% object-cover pointer-events-none rounded-[100px] size-full" src={imgFrame26089667} />
    </div>
  );
}

function Frame1() {
  return (
    <div className="content-stretch flex flex-col gap-[4px] items-start leading-[0] not-italic relative shrink-0 text-center text-nowrap">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center relative shrink-0 text-[#151b26] text-[16px] tracking-[0.16px]">
        <p className="leading-[1.5] text-nowrap whitespace-pre">삼성전자</p>
      </div>
      <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center relative shrink-0 text-[#a1a4a8] text-[12px] tracking-[0.24px]">
        <p className="leading-[1.5] text-nowrap whitespace-pre">30주</p>
      </div>
    </div>
  );
}

function Frame19() {
  return (
    <div className="content-stretch flex gap-[12px] items-start relative shrink-0">
      <Frame17 />
      <Frame1 />
    </div>
  );
}

function Frame2() {
  return (
    <div className="content-stretch flex gap-[4px] items-start relative shrink-0">
      <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#f3646f] text-[12px] text-center text-nowrap tracking-[0.24px]">
        <p className="leading-[1.5] whitespace-pre">+46,043 (7.8%)</p>
      </div>
    </div>
  );
}

function Frame18() {
  return (
    <div className="content-stretch flex flex-col gap-[4px] items-end justify-center relative shrink-0">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#444951] text-[16px] text-center text-nowrap tracking-[0.16px]">
        <p className="leading-[1.5] whitespace-pre">2,967,000원</p>
      </div>
      <Frame2 />
    </div>
  );
}

function Frame20() {
  return (
    <div className="content-stretch flex items-start justify-between relative shrink-0 w-full">
      <Frame19 />
      <Frame18 />
    </div>
  );
}

function Frame() {
  return (
    <div className="bg-[#f2f4f8] relative rounded-[16px] shrink-0 w-full">
      <div className="overflow-clip rounded-[inherit] size-full">
        <div className="box-border content-stretch flex flex-col gap-[8px] items-start px-[20px] py-[16px] relative w-full">
          <Frame20 />
        </div>
      </div>
    </div>
  );
}

function Frame3() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[12px] items-start px-[20px] py-0 relative w-full">
          <Frame />
        </div>
      </div>
    </div>
  );
}

function Frame26() {
  return (
    <div className="content-stretch flex flex-col gap-[10px] items-start relative shrink-0 w-full">
      <Component2 />
      <Frame3 />
    </div>
  );
}

function Plus() {
  return (
    <div className="relative shrink-0 size-[20px]" data-name="plus">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 20 20">
        <g id="plus">
          <path d={svgPaths.p35341400} fill="var(--fill-0, white)" id="Vector" />
        </g>
      </svg>
    </div>
  );
}

function Frame7() {
  return (
    <div className="box-border content-stretch flex gap-[8px] items-center justify-center p-[1.6px] relative shrink-0">
      <Plus />
    </div>
  );
}

function Component3() {
  return (
    <div className="bg-[#1fa9a4] relative rounded-[8px] shrink-0 w-full" data-name="영역 헤더 우측 버튼">
      <div className="flex flex-row items-center justify-center size-full">
        <div className="box-border content-stretch flex gap-[2px] items-center justify-center px-[8px] py-[12px] relative w-full">
          <Frame7 />
          <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[16px] text-center text-nowrap text-white tracking-[0.16px]">
            <p className="leading-[1.5] whitespace-pre">종목 추가</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function Frame24() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[10px] items-start px-[20px] py-0 relative w-full">
          <Component3 />
        </div>
      </div>
    </div>
  );
}

function Frame27() {
  return (
    <div className="content-stretch flex flex-col gap-[20px] items-start relative shrink-0 w-full">
      <Frame26 />
      <Frame24 />
    </div>
  );
}

function Frame16() {
  return (
    <div className="box-border content-stretch flex flex-col gap-[28px] items-center justify-center px-0 py-[16px] relative shrink-0 w-full">
      <Frame25 />
      <Frame27 />
    </div>
  );
}

function Frame22() {
  return (
    <div className="absolute content-stretch flex flex-col gap-[12px] items-start left-1/2 top-[64px] translate-x-[-50%] w-[375px]">
      <Frame14 />
      <Frame16 />
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

function Component5() {
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
      <Component5 />
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

export default function Component4() {
  return (
    <div className="bg-white relative size-full" data-name="홈">
      <IOsStatusBar />
      <Frame22 />
      <IOsHomeBar />
    </div>
  );
}