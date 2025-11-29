import svgPaths from "./svg-g85yiot6ll";

function Frame11() {
  return (
    <div className="content-stretch flex gap-[4px] items-center justify-center relative shrink-0">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic overflow-ellipsis overflow-hidden relative shrink-0 text-[#a1a4a8] text-[16px] text-center text-nowrap tracking-[0.16px]">
        <p className="leading-[1.5] overflow-ellipsis overflow-hidden whitespace-pre">지표 분석</p>
      </div>
    </div>
  );
}

function Frame() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="flex flex-row items-center justify-center overflow-clip rounded-[inherit] size-full">
        <div className="box-border content-stretch flex items-center justify-center pb-[4px] pt-[8px] px-[8px] relative w-full">
          <Frame11 />
        </div>
      </div>
    </div>
  );
}

function Frame1() {
  return <div className="bg-[#e8e8e9] h-[2px] shrink-0 w-full" />;
}

function Tab1() {
  return (
    <div className="basis-0 content-stretch flex flex-col gap-[4px] grow items-center justify-center min-h-px min-w-px relative shrink-0" data-name="Tab 2">
      <Frame />
      <Frame1 />
    </div>
  );
}

function Ai() {
  return (
    <div className="relative shrink-0 size-[18px]" data-name="AI">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 18 18">
        <g id="AI">
          <path clipRule="evenodd" d={svgPaths.p1036f280} fill="var(--fill-0, #151B26)" fillRule="evenodd" id="Vector" />
        </g>
      </svg>
    </div>
  );
}

function Frame12() {
  return (
    <div className="content-stretch flex gap-[4px] items-center justify-center relative shrink-0">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic overflow-ellipsis overflow-hidden relative shrink-0 text-[#151b26] text-[16px] text-center text-nowrap tracking-[0.16px]">
        <p className="leading-[1.5] overflow-ellipsis overflow-hidden whitespace-pre">AI 거래 내역</p>
      </div>
    </div>
  );
}

function Frame2() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="flex flex-row items-center justify-center overflow-clip rounded-[inherit] size-full">
        <div className="box-border content-stretch flex gap-[4px] items-center justify-center pb-[4px] pt-[8px] px-[8px] relative w-full">
          <Ai />
          <Frame12 />
        </div>
      </div>
    </div>
  );
}

function Frame3() {
  return <div className="bg-[#151b26] h-[2px] shrink-0 w-full" />;
}

function Tab() {
  return (
    <div className="basis-0 content-stretch flex flex-col gap-[4px] grow items-center justify-center min-h-px min-w-px relative shrink-0" data-name="Tab 1">
      <Frame2 />
      <Frame3 />
    </div>
  );
}

function Component() {
  return (
    <div className="box-border content-stretch flex items-center justify-center px-[20px] py-0 relative shrink-0 w-[375px]" data-name="영역 고정 세그먼트 탭">
      <Tab1 />
      <Tab />
    </div>
  );
}

function Frame4() {
  return (
    <div className="basis-0 content-stretch flex gap-[4px] grow items-center min-h-px min-w-px relative shrink-0">
      <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[12px] text-nowrap tracking-[0.24px]">
        <p className="leading-[1.5] whitespace-pre">오늘</p>
      </div>
    </div>
  );
}

function Info() {
  return (
    <div className="relative shrink-0 size-[16px]" data-name="info">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 16 16">
        <g id="info">
          <g id="Vector">
            <path d={svgPaths.p2202000} fill="#A1A4A8" />
            <path d={svgPaths.p376400} fill="#A1A4A8" />
            <path clipRule="evenodd" d={svgPaths.p120eb380} fill="#A1A4A8" fillRule="evenodd" />
          </g>
        </g>
      </svg>
    </div>
  );
}

function Frame5() {
  return (
    <div className="content-stretch flex gap-[2px] items-center relative shrink-0">
      <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[12px] text-nowrap tracking-[0.24px]">
        <p className="leading-[1.5] whitespace-pre">AI 거래 내역 안내</p>
      </div>
      <Info />
    </div>
  );
}

function Frame6() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="flex flex-row items-center size-full">
        <div className="box-border content-stretch flex gap-[2px] items-center px-[20px] py-0 relative w-full">
          <Frame4 />
          <Frame5 />
        </div>
      </div>
    </div>
  );
}

function Frame33() {
  return (
    <div className="content-stretch flex font-['Pretendard:Bold',sans-serif] gap-[4px] items-start leading-[0] not-italic relative shrink-0 text-[#f3646f] text-[16px] text-nowrap tracking-[0.16px] w-full">
      <div className="flex flex-col justify-center relative shrink-0">
        <p className="leading-[1.5] text-nowrap whitespace-pre">+12,830원</p>
      </div>
      <div className="flex flex-col justify-center relative shrink-0">
        <p className="leading-[1.5] text-nowrap whitespace-pre">(22.3%)</p>
      </div>
    </div>
  );
}

function Frame34() {
  return (
    <div className="content-stretch flex flex-col items-start relative shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[16px] tracking-[0.16px] w-full">
        <p className="leading-[1.5]">10주 판매</p>
      </div>
      <Frame33 />
    </div>
  );
}

function Frame30() {
  return (
    <div className="content-stretch flex font-['Pretendard:SemiBold',sans-serif] items-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[11px] text-nowrap tracking-[0.22px]">
      <div className="flex flex-col justify-center relative shrink-0">
        <p className="leading-[1.45] text-nowrap whitespace-pre">{`{1주 판매 가격}`}</p>
      </div>
      <div className="flex flex-col justify-center relative shrink-0">
        <p className="leading-[1.45] text-nowrap whitespace-pre">원</p>
      </div>
    </div>
  );
}

function Frame31() {
  return (
    <div className="content-stretch flex gap-[4px] items-center relative shrink-0">
      <div className="flex flex-col font-['Pretendard:SemiBold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[11px] text-nowrap tracking-[0.22px]">
        <p className="leading-[1.45] whitespace-pre">1주당</p>
      </div>
      <Frame30 />
    </div>
  );
}

function Frame29() {
  return (
    <div className="content-stretch flex items-start relative shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:SemiBold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[11px] text-nowrap tracking-[0.22px]">
        <p className="leading-[1.45] whitespace-pre">14:22</p>
      </div>
      <div className="flex flex-col font-['Pretendard:SemiBold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[11px] text-nowrap tracking-[0.22px]">
        <p className="leading-[1.45] whitespace-pre">・</p>
      </div>
      <Frame31 />
    </div>
  );
}

function Frame14() {
  return (
    <div className="box-border content-stretch flex flex-col gap-[4px] items-start px-0 py-[8px] relative rounded-[16px] shrink-0 w-full">
      <Frame34 />
      <Frame29 />
    </div>
  );
}

function Frame26() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[8px] items-start px-[20px] py-0 relative w-full">
          <Frame14 />
        </div>
      </div>
    </div>
  );
}

function Component1() {
  return (
    <div className="bg-white h-px relative shrink-0 w-full" data-name="디바이더">
      <div className="flex flex-row items-center justify-center size-full">
        <div className="box-border content-stretch flex h-px items-center justify-center px-[20px] py-0 relative w-full">
          <div className="basis-0 bg-[#f4f5f5] grow h-full min-h-px min-w-px shrink-0" />
        </div>
      </div>
    </div>
  );
}

function Frame35() {
  return (
    <div className="content-stretch flex font-['Pretendard:SemiBold',sans-serif] items-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[11px] text-nowrap tracking-[0.22px]">
      <div className="flex flex-col justify-center relative shrink-0">
        <p className="leading-[1.45] text-nowrap whitespace-pre">{`{1주 구매 가격}`}</p>
      </div>
      <div className="flex flex-col justify-center relative shrink-0">
        <p className="leading-[1.45] text-nowrap whitespace-pre">원</p>
      </div>
    </div>
  );
}

function Frame36() {
  return (
    <div className="content-stretch flex gap-[4px] items-center relative shrink-0">
      <div className="flex flex-col font-['Pretendard:SemiBold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[11px] text-nowrap tracking-[0.22px]">
        <p className="leading-[1.45] whitespace-pre">1주당</p>
      </div>
      <Frame35 />
    </div>
  );
}

function Frame37() {
  return (
    <div className="content-stretch flex items-start relative shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:SemiBold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[11px] text-nowrap tracking-[0.22px]">
        <p className="leading-[1.45] whitespace-pre">14:22</p>
      </div>
      <div className="flex flex-col font-['Pretendard:SemiBold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[11px] text-nowrap tracking-[0.22px]">
        <p className="leading-[1.45] whitespace-pre">・</p>
      </div>
      <Frame36 />
    </div>
  );
}

function Frame15() {
  return (
    <div className="box-border content-stretch flex flex-col gap-[4px] items-start px-0 py-[8px] relative rounded-[16px] shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[16px] tracking-[0.16px] w-full">
        <p className="leading-[1.5]">10주 구매</p>
      </div>
      <Frame37 />
    </div>
  );
}

function Frame25() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[8px] items-start px-[20px] py-0 relative w-full">
          <Frame15 />
        </div>
      </div>
    </div>
  );
}

function Frame32() {
  return (
    <div className="content-stretch flex flex-col gap-[8px] items-start relative shrink-0 w-full">
      <Frame26 />
      <Component1 />
      <Frame25 />
      <Component1 />
    </div>
  );
}

function Frame20() {
  return (
    <div className="box-border content-stretch flex flex-col gap-[16px] items-start pb-0 pt-[12px] px-0 relative shrink-0 w-full">
      <Frame6 />
      <Frame32 />
    </div>
  );
}

function Frame7() {
  return (
    <div className="basis-0 content-stretch flex gap-[4px] grow items-center min-h-px min-w-px relative shrink-0">
      <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[12px] text-nowrap tracking-[0.24px]">
        <p className="leading-[1.5] whitespace-pre">어제</p>
      </div>
    </div>
  );
}

function Frame8() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="flex flex-row items-center size-full">
        <div className="box-border content-stretch flex gap-[2px] items-center px-[20px] py-0 relative w-full">
          <Frame7 />
        </div>
      </div>
    </div>
  );
}

function Frame38() {
  return (
    <div className="content-stretch flex font-['Pretendard:Bold',sans-serif] gap-[4px] items-start leading-[0] not-italic relative shrink-0 text-[#5c87f2] text-[16px] text-nowrap tracking-[0.16px] w-full">
      <div className="flex flex-col justify-center relative shrink-0">
        <p className="leading-[1.5] text-nowrap whitespace-pre">-12,830원</p>
      </div>
      <div className="flex flex-col justify-center relative shrink-0">
        <p className="leading-[1.5] text-nowrap whitespace-pre">(22.3%)</p>
      </div>
    </div>
  );
}

function Frame39() {
  return (
    <div className="content-stretch flex flex-col items-start relative shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[16px] tracking-[0.16px] w-full">
        <p className="leading-[1.5]">10주 판매</p>
      </div>
      <Frame38 />
    </div>
  );
}

function Frame40() {
  return (
    <div className="content-stretch flex font-['Pretendard:SemiBold',sans-serif] items-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[11px] text-nowrap tracking-[0.22px]">
      <div className="flex flex-col justify-center relative shrink-0">
        <p className="leading-[1.45] text-nowrap whitespace-pre">{`{1주 판매 가격}`}</p>
      </div>
      <div className="flex flex-col justify-center relative shrink-0">
        <p className="leading-[1.45] text-nowrap whitespace-pre">원</p>
      </div>
    </div>
  );
}

function Frame41() {
  return (
    <div className="content-stretch flex gap-[4px] items-center relative shrink-0">
      <div className="flex flex-col font-['Pretendard:SemiBold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[11px] text-nowrap tracking-[0.22px]">
        <p className="leading-[1.45] whitespace-pre">1주당</p>
      </div>
      <Frame40 />
    </div>
  );
}

function Frame42() {
  return (
    <div className="content-stretch flex items-start relative shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:SemiBold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[11px] text-nowrap tracking-[0.22px]">
        <p className="leading-[1.45] whitespace-pre">14:22</p>
      </div>
      <div className="flex flex-col font-['Pretendard:SemiBold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[11px] text-nowrap tracking-[0.22px]">
        <p className="leading-[1.45] whitespace-pre">・</p>
      </div>
      <Frame41 />
    </div>
  );
}

function Frame16() {
  return (
    <div className="box-border content-stretch flex flex-col gap-[4px] items-start px-0 py-[8px] relative rounded-[16px] shrink-0 w-full">
      <Frame39 />
      <Frame42 />
    </div>
  );
}

function Frame21() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[8px] items-start px-[20px] py-0 relative w-full">
          <Frame16 />
        </div>
      </div>
    </div>
  );
}

function Component2() {
  return (
    <div className="bg-white h-px relative shrink-0 w-full" data-name="디바이더">
      <div className="flex flex-row items-center justify-center size-full">
        <div className="box-border content-stretch flex h-px items-center justify-center px-[20px] py-0 relative w-full">
          <div className="basis-0 bg-[#f4f5f5] grow h-full min-h-px min-w-px shrink-0" />
        </div>
      </div>
    </div>
  );
}

function Frame43() {
  return (
    <div className="content-stretch flex font-['Pretendard:SemiBold',sans-serif] items-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[11px] text-nowrap tracking-[0.22px]">
      <div className="flex flex-col justify-center relative shrink-0">
        <p className="leading-[1.45] text-nowrap whitespace-pre">{`{1주 구매 가격}`}</p>
      </div>
      <div className="flex flex-col justify-center relative shrink-0">
        <p className="leading-[1.45] text-nowrap whitespace-pre">원</p>
      </div>
    </div>
  );
}

function Frame44() {
  return (
    <div className="content-stretch flex gap-[4px] items-center relative shrink-0">
      <div className="flex flex-col font-['Pretendard:SemiBold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[11px] text-nowrap tracking-[0.22px]">
        <p className="leading-[1.45] whitespace-pre">1주당</p>
      </div>
      <Frame43 />
    </div>
  );
}

function Frame45() {
  return (
    <div className="content-stretch flex items-start relative shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:SemiBold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[11px] text-nowrap tracking-[0.22px]">
        <p className="leading-[1.45] whitespace-pre">14:23</p>
      </div>
      <div className="flex flex-col font-['Pretendard:SemiBold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[11px] text-nowrap tracking-[0.22px]">
        <p className="leading-[1.45] whitespace-pre">・</p>
      </div>
      <Frame44 />
    </div>
  );
}

function Frame17() {
  return (
    <div className="box-border content-stretch flex flex-col gap-[4px] items-start px-0 py-[8px] relative rounded-[16px] shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[16px] tracking-[0.16px] w-full">
        <p className="leading-[1.5]">10주 구매</p>
      </div>
      <Frame45 />
    </div>
  );
}

function Frame27() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[8px] items-start px-[20px] py-0 relative w-full">
          <Frame17 />
        </div>
      </div>
    </div>
  );
}

function Frame46() {
  return (
    <div className="content-stretch flex flex-col gap-[8px] items-start relative shrink-0 w-full">
      <Frame21 />
      <Component2 />
      <Frame27 />
      <Component2 />
    </div>
  );
}

function Frame22() {
  return (
    <div className="box-border content-stretch flex flex-col gap-[16px] items-start pb-0 pt-[12px] px-0 relative shrink-0 w-full">
      <Frame8 />
      <Frame46 />
    </div>
  );
}

function Frame9() {
  return (
    <div className="basis-0 content-stretch flex gap-[4px] grow items-center min-h-px min-w-px relative shrink-0">
      <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[12px] text-nowrap tracking-[0.24px]">
        <p className="leading-[1.5] whitespace-pre">11월 19일</p>
      </div>
    </div>
  );
}

function Frame10() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="flex flex-row items-center size-full">
        <div className="box-border content-stretch flex gap-[2px] items-center px-[20px] py-0 relative w-full">
          <Frame9 />
        </div>
      </div>
    </div>
  );
}

function Frame47() {
  return (
    <div className="content-stretch flex font-['Pretendard:Bold',sans-serif] gap-[4px] items-start leading-[0] not-italic relative shrink-0 text-[#5c87f2] text-[16px] text-nowrap tracking-[0.16px] w-full">
      <div className="flex flex-col justify-center relative shrink-0">
        <p className="leading-[1.5] text-nowrap whitespace-pre">-12,830원</p>
      </div>
      <div className="flex flex-col justify-center relative shrink-0">
        <p className="leading-[1.5] text-nowrap whitespace-pre">(22.3%)</p>
      </div>
    </div>
  );
}

function Frame48() {
  return (
    <div className="content-stretch flex flex-col items-start relative shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[16px] tracking-[0.16px] w-full">
        <p className="leading-[1.5]">100주 판매</p>
      </div>
      <Frame47 />
    </div>
  );
}

function Frame49() {
  return (
    <div className="content-stretch flex font-['Pretendard:SemiBold',sans-serif] items-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[11px] text-nowrap tracking-[0.22px]">
      <div className="flex flex-col justify-center relative shrink-0">
        <p className="leading-[1.45] text-nowrap whitespace-pre">{`{1주 판매 가격}`}</p>
      </div>
      <div className="flex flex-col justify-center relative shrink-0">
        <p className="leading-[1.45] text-nowrap whitespace-pre">원</p>
      </div>
    </div>
  );
}

function Frame50() {
  return (
    <div className="content-stretch flex gap-[4px] items-center relative shrink-0">
      <div className="flex flex-col font-['Pretendard:SemiBold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[11px] text-nowrap tracking-[0.22px]">
        <p className="leading-[1.45] whitespace-pre">1주당</p>
      </div>
      <Frame49 />
    </div>
  );
}

function Frame51() {
  return (
    <div className="content-stretch flex items-start relative shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:SemiBold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[11px] text-nowrap tracking-[0.22px]">
        <p className="leading-[1.45] whitespace-pre">14:22</p>
      </div>
      <div className="flex flex-col font-['Pretendard:SemiBold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[11px] text-nowrap tracking-[0.22px]">
        <p className="leading-[1.45] whitespace-pre">・</p>
      </div>
      <Frame50 />
    </div>
  );
}

function Frame18() {
  return (
    <div className="box-border content-stretch flex flex-col gap-[4px] items-start px-0 py-[8px] relative rounded-[16px] shrink-0 w-full">
      <Frame48 />
      <Frame51 />
    </div>
  );
}

function Frame28() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[8px] items-start px-[20px] py-0 relative w-full">
          <Frame18 />
        </div>
      </div>
    </div>
  );
}

function Component3() {
  return (
    <div className="bg-white h-px relative shrink-0 w-full" data-name="디바이더">
      <div className="flex flex-row items-center justify-center size-full">
        <div className="box-border content-stretch flex h-px items-center justify-center px-[20px] py-0 relative w-full">
          <div className="basis-0 bg-[#f4f5f5] grow h-full min-h-px min-w-px shrink-0" />
        </div>
      </div>
    </div>
  );
}

function Frame52() {
  return (
    <div className="content-stretch flex font-['Pretendard:SemiBold',sans-serif] items-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[11px] text-nowrap tracking-[0.22px]">
      <div className="flex flex-col justify-center relative shrink-0">
        <p className="leading-[1.45] text-nowrap whitespace-pre">{`{1주 구매 가격}`}</p>
      </div>
      <div className="flex flex-col justify-center relative shrink-0">
        <p className="leading-[1.45] text-nowrap whitespace-pre">원</p>
      </div>
    </div>
  );
}

function Frame53() {
  return (
    <div className="content-stretch flex gap-[4px] items-center relative shrink-0">
      <div className="flex flex-col font-['Pretendard:SemiBold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[11px] text-nowrap tracking-[0.22px]">
        <p className="leading-[1.45] whitespace-pre">1주당</p>
      </div>
      <Frame52 />
    </div>
  );
}

function Frame54() {
  return (
    <div className="content-stretch flex items-start relative shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:SemiBold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[11px] text-nowrap tracking-[0.22px]">
        <p className="leading-[1.45] whitespace-pre">14:23</p>
      </div>
      <div className="flex flex-col font-['Pretendard:SemiBold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[11px] text-nowrap tracking-[0.22px]">
        <p className="leading-[1.45] whitespace-pre">・</p>
      </div>
      <Frame53 />
    </div>
  );
}

function Frame19() {
  return (
    <div className="box-border content-stretch flex flex-col gap-[4px] items-start px-0 py-[8px] relative rounded-[16px] shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[16px] tracking-[0.16px] w-full">
        <p className="leading-[1.5]">100주 구매</p>
      </div>
      <Frame54 />
    </div>
  );
}

function Frame24() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[8px] items-start px-[20px] py-0 relative w-full">
          <Frame19 />
        </div>
      </div>
    </div>
  );
}

function Frame55() {
  return (
    <div className="content-stretch flex flex-col gap-[8px] items-start relative shrink-0 w-full">
      <Frame28 />
      <Component3 />
      <Frame24 />
      <Component3 />
    </div>
  );
}

function Frame23() {
  return (
    <div className="box-border content-stretch flex flex-col gap-[16px] items-start pb-0 pt-[12px] px-0 relative shrink-0 w-full">
      <Frame10 />
      <Frame55 />
    </div>
  );
}

export default function Frame13() {
  return (
    <div className="content-stretch flex flex-col gap-[8px] items-center justify-center relative size-full">
      <Component />
      <Frame20 />
      <Frame22 />
      <Frame23 />
    </div>
  );
}