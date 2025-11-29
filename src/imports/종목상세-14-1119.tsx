import svgPaths from "./svg-5pzvvonb4j";

function CaretLeft() {
  return (
    <div className="relative shrink-0 size-[24px]" data-name="caret-left">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g id="caret-left">
          <path d={svgPaths.p21f93bf0} fill="var(--fill-0, #151B26)" id="Vector" />
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

function Frame7() {
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
          <div className="basis-0 flex flex-col font-['Pretendard:Bold',sans-serif] grow justify-center leading-[0] min-h-px min-w-px not-italic overflow-ellipsis overflow-hidden relative shrink-0 text-[#151b26] text-[18px] text-center text-nowrap">
            <p className="[white-space-collapse:collapse] leading-[1.55] overflow-ellipsis overflow-hidden">삼성전자</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function Frame1() {
  return <div className="shrink-0 size-[32px]" />;
}

function Frame2() {
  return <div className="box-border content-stretch flex gap-[10px] items-center justify-center p-[4px] shrink-0" />;
}

function Component2() {
  return (
    <div className="content-stretch flex gap-[4px] items-center justify-end relative shrink-0" data-name="상단 헤더 우측 버튼">
      <Frame1 />
      <Frame2 />
    </div>
  );
}

function Frame8() {
  return (
    <div className="absolute content-stretch flex items-center justify-center left-[16px] right-[16px] top-1/2 translate-y-[-50%]">
      <Frame7 />
      <Component1 />
      <Component2 />
    </div>
  );
}

function Component3() {
  return (
    <div className="h-[58px] relative shrink-0 w-[375px]" data-name="상단 헤더">
      <Frame8 />
    </div>
  );
}

function Frame48() {
  return (
    <div className="basis-0 content-stretch flex flex-col gap-[4px] grow items-start leading-[0] min-h-px min-w-px not-italic relative shrink-0 text-center text-nowrap">
      <div className="flex flex-col font-['Pretendard:SemiBold',sans-serif] justify-center relative shrink-0 text-[#151b26] text-[12px] tracking-[0.24px]">
        <p className="leading-[1.5] text-nowrap whitespace-pre">오늘의 추천 행동</p>
      </div>
      <div className="flex flex-col font-['Pretendard:ExtraBold',sans-serif] justify-center relative shrink-0 text-[#1fa9a4] text-[36px] tracking-[1.44px]">
        <p className="leading-[normal] text-nowrap whitespace-pre">매도</p>
      </div>
    </div>
  );
}

function Info() {
  return (
    <div className="relative shrink-0 size-[24px]" data-name="info">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g id="info">
          <g id="Vector">
            <path d={svgPaths.p2a2e8f80} fill="#D0D1D4" />
            <path d={svgPaths.p3f621100} fill="#D0D1D4" />
            <path clipRule="evenodd" d={svgPaths.p1137c370} fill="#D0D1D4" fillRule="evenodd" />
          </g>
        </g>
      </svg>
    </div>
  );
}

function Frame88() {
  return (
    <div className="content-stretch flex gap-[20px] items-start relative shrink-0 w-full">
      <Frame48 />
      <Info />
    </div>
  );
}

function Frame() {
  return (
    <div className="box-border content-stretch flex flex-col gap-[10px] items-start px-0 py-[8px] relative shrink-0 w-full">
      <div className="aspect-[284.59/37.0933] relative shrink-0 w-full">
        <div className="absolute inset-[-2.92%_-0.17%_-3.46%_-0.23%]">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 305 43">
            <path d={svgPaths.p1c90c83e} id="Vector 7" stroke="var(--stroke-0, #1FA9A4)" strokeWidth="2" />
          </svg>
        </div>
      </div>
    </div>
  );
}

function Component4() {
  return (
    <div className="bg-white content-stretch flex h-px items-center justify-center relative shrink-0 w-full" data-name="디바이더">
      <div className="basis-0 bg-[#d0d1d4] grow h-[0.5px] min-h-px min-w-px shrink-0" />
    </div>
  );
}

function Ai() {
  return (
    <div className="relative shrink-0 size-[24px]" data-name="AI">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g id="AI">
          <path clipRule="evenodd" d={svgPaths.p19b55300} fill="var(--fill-0, #151B26)" fillRule="evenodd" id="Vector" />
        </g>
      </svg>
    </div>
  );
}

function Frame44() {
  return (
    <div className="content-stretch flex gap-[4px] items-center relative shrink-0 w-full">
      <Ai />
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[18px] text-center text-nowrap">
        <p className="leading-[1.55] whitespace-pre">AI 설명</p>
      </div>
    </div>
  );
}

function Frame49() {
  return (
    <div className="content-stretch flex flex-col gap-[8px] items-start relative shrink-0 w-full">
      <Frame44 />
      <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[14px] tracking-[0.14px] w-full">
        <p className="leading-[1.45]">기술적 분석에서 전반적으로 하락세를 유지하고 있으며, 주가는 추가 하락 가능성이 높습니다. 시장 상황에 대한 신중한 접근과 경계를 유지하여 변동성에 대비하는 것이 중요합니다.</p>
      </div>
    </div>
  );
}

function Frame45() {
  return (
    <div className="bg-[#f2f4f8] relative rounded-[16px] shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[20px] items-start p-[20px] relative w-full">
          <Frame88 />
          <Frame />
          <Component4 />
          <Frame49 />
        </div>
      </div>
    </div>
  );
}

function Frame41() {
  return (
    <div className="box-border content-stretch flex flex-col gap-[20px] items-start pb-[24px] pt-[16px] px-[16px] relative shrink-0 w-[375px]">
      <Frame45 />
    </div>
  );
}

function Frame38() {
  return (
    <div className="content-stretch flex gap-[4px] items-center justify-center relative shrink-0">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic overflow-ellipsis overflow-hidden relative shrink-0 text-[#151b26] text-[16px] text-center text-nowrap tracking-[0.16px]">
        <p className="leading-[1.5] overflow-ellipsis overflow-hidden whitespace-pre">지표 분석</p>
      </div>
    </div>
  );
}

function Frame3() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="flex flex-row items-center justify-center overflow-clip rounded-[inherit] size-full">
        <div className="box-border content-stretch flex items-center justify-center pb-[4px] pt-[8px] px-[8px] relative w-full">
          <Frame38 />
        </div>
      </div>
    </div>
  );
}

function Frame6() {
  return <div className="bg-[#151b26] h-[2px] shrink-0 w-full" />;
}

function Tab1() {
  return (
    <div className="basis-0 content-stretch flex flex-col gap-[4px] grow items-center justify-center min-h-px min-w-px relative shrink-0" data-name="Tab 2">
      <Frame3 />
      <Frame6 />
    </div>
  );
}

function Ai1() {
  return (
    <div className="relative shrink-0 size-[18px]" data-name="AI">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 18 18">
        <g id="AI">
          <path clipRule="evenodd" d={svgPaths.p1036f280} fill="var(--fill-0, #A1A4A8)" fillRule="evenodd" id="Vector" />
        </g>
      </svg>
    </div>
  );
}

function Frame39() {
  return (
    <div className="content-stretch flex gap-[4px] items-center justify-center relative shrink-0">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic overflow-ellipsis overflow-hidden relative shrink-0 text-[#a1a4a8] text-[16px] text-center text-nowrap tracking-[0.16px]">
        <p className="leading-[1.5] overflow-ellipsis overflow-hidden whitespace-pre">AI 거래 내역</p>
      </div>
    </div>
  );
}

function Frame4() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="flex flex-row items-center justify-center overflow-clip rounded-[inherit] size-full">
        <div className="box-border content-stretch flex gap-[4px] items-center justify-center pb-[4px] pt-[8px] px-[8px] relative w-full">
          <Ai1 />
          <Frame39 />
        </div>
      </div>
    </div>
  );
}

function Frame5() {
  return <div className="bg-[#e8e8e9] h-[2px] shrink-0 w-full" />;
}

function Tab() {
  return (
    <div className="basis-0 content-stretch flex flex-col gap-[4px] grow items-center justify-center min-h-px min-w-px relative shrink-0" data-name="Tab 1">
      <Frame4 />
      <Frame5 />
    </div>
  );
}

function Component5() {
  return (
    <div className="box-border content-stretch flex items-center justify-center px-[20px] py-0 relative shrink-0 w-[375px]" data-name="영역 고정 세그먼트 탭">
      <Tab1 />
      <Tab />
    </div>
  );
}

function Frame9() {
  return (
    <div className="basis-0 content-stretch flex gap-[4px] grow items-center min-h-px min-w-px relative shrink-0">
      <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[12px] text-nowrap tracking-[0.24px]">
        <p className="leading-[1.5] whitespace-pre">오늘 기준</p>
      </div>
    </div>
  );
}

function Info1() {
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

function Frame10() {
  return (
    <div className="content-stretch flex gap-[2px] items-center relative shrink-0">
      <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[12px] text-nowrap tracking-[0.24px]">
        <p className="leading-[1.5] whitespace-pre">지표 분석 안내</p>
      </div>
      <Info1 />
    </div>
  );
}

function Frame11() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="flex flex-row items-center size-full">
        <div className="box-border content-stretch flex gap-[2px] items-center px-[20px] py-0 relative w-full">
          <Frame9 />
          <Frame10 />
        </div>
      </div>
    </div>
  );
}

function Frame12() {
  return (
    <div className="content-stretch flex gap-[4px] items-center relative shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#1fa9a4] text-[0px] text-nowrap tracking-[0.16px]">
        <p className="[text-decoration-skip-ink:none] [text-underline-position:from-font] decoration-solid leading-[1.5] text-[16px] underline whitespace-pre">거래량</p>
      </div>
    </div>
  );
}

function Frame13() {
  return (
    <div className="content-stretch flex flex-col gap-[2px] items-start justify-center relative shrink-0 w-full">
      <Frame12 />
    </div>
  );
}

function Frame47() {
  return (
    <div className="content-stretch flex flex-col gap-[8px] items-start relative shrink-0 w-full">
      <Frame13 />
      <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[14px] tracking-[0.14px] w-full">
        <p className="leading-[1.45]">거래량이 평균 대비 증가하며 추세에 대한 시장 참여도가 높습니다.</p>
      </div>
    </div>
  );
}

function Frame46() {
  return (
    <div className="bg-[#f2f4f8] relative rounded-[16px] shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[20px] items-start p-[20px] relative w-full">
          <Frame47 />
        </div>
      </div>
    </div>
  );
}

function Frame67() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[8px] items-start px-[20px] py-0 relative w-full">
          <Frame46 />
        </div>
      </div>
    </div>
  );
}

function Frame14() {
  return (
    <div className="content-stretch flex gap-[4px] items-center relative shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#1fa9a4] text-[0px] text-nowrap tracking-[0.16px]">
        <p className="[text-decoration-skip-ink:none] [text-underline-position:from-font] decoration-solid leading-[1.5] text-[16px] underline whitespace-pre">RSI</p>
      </div>
    </div>
  );
}

function Frame15() {
  return (
    <div className="content-stretch flex flex-col gap-[2px] items-start justify-center relative shrink-0 w-full">
      <Frame14 />
    </div>
  );
}

function Frame55() {
  return (
    <div className="content-stretch flex flex-col gap-[8px] items-start relative shrink-0 w-full">
      <Frame15 />
      <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[14px] tracking-[0.14px] w-full">
        <p className="leading-[1.45]">RSI가 과매수 구간(70 이상)에 진입하여 단기 조정 가능성이 있습니다.</p>
      </div>
    </div>
  );
}

function Frame56() {
  return (
    <div className="bg-[#f2f4f8] relative rounded-[16px] shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[20px] items-start p-[20px] relative w-full">
          <Frame55 />
        </div>
      </div>
    </div>
  );
}

function Frame50() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[8px] items-start px-[20px] py-0 relative w-full">
          <Frame56 />
        </div>
      </div>
    </div>
  );
}

function Frame16() {
  return (
    <div className="content-stretch flex gap-[4px] items-center relative shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#1fa9a4] text-[0px] text-nowrap tracking-[0.16px]">
        <p className="[text-decoration-skip-ink:none] [text-underline-position:from-font] decoration-solid leading-[1.5] text-[16px] underline whitespace-pre">Stoch_K</p>
      </div>
    </div>
  );
}

function Frame17() {
  return (
    <div className="content-stretch flex flex-col gap-[2px] items-start justify-center relative shrink-0 w-full">
      <Frame16 />
    </div>
  );
}

function Frame57() {
  return (
    <div className="content-stretch flex flex-col gap-[8px] items-start relative shrink-0 w-full">
      <Frame17 />
      <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[14px] tracking-[0.14px] w-full">
        <p className="leading-[1.45]">스토캐스틱이 과매수 구간(80 이상)에 머물며 하락 반전 가능성이 있습니다.</p>
      </div>
    </div>
  );
}

function Frame58() {
  return (
    <div className="bg-[#f2f4f8] relative rounded-[16px] shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[20px] items-start p-[20px] relative w-full">
          <Frame57 />
        </div>
      </div>
    </div>
  );
}

function Frame51() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[8px] items-start px-[20px] py-0 relative w-full">
          <Frame58 />
        </div>
      </div>
    </div>
  );
}

function Frame18() {
  return (
    <div className="content-stretch flex gap-[4px] items-center relative shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#1fa9a4] text-[0px] text-nowrap tracking-[0.16px]">
        <p className="[text-decoration-skip-ink:none] [text-underline-position:from-font] decoration-solid leading-[1.5] text-[16px] underline whitespace-pre">Stoch_D</p>
      </div>
    </div>
  );
}

function Frame19() {
  return (
    <div className="content-stretch flex flex-col gap-[2px] items-start justify-center relative shrink-0 w-full">
      <Frame18 />
    </div>
  );
}

function Frame59() {
  return (
    <div className="content-stretch flex flex-col gap-[8px] items-start relative shrink-0 w-full">
      <Frame19 />
      <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[14px] tracking-[0.14px] w-full">
        <p className="leading-[1.45]">스토캐스틱이 과매수 구간(80 이상)에 머물며 하락 반전 가능성이 있습니다.</p>
      </div>
    </div>
  );
}

function Frame60() {
  return (
    <div className="bg-[#f2f4f8] relative rounded-[16px] shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[20px] items-start p-[20px] relative w-full">
          <Frame59 />
        </div>
      </div>
    </div>
  );
}

function Frame70() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[8px] items-start px-[20px] py-0 relative w-full">
          <Frame60 />
        </div>
      </div>
    </div>
  );
}

function Frame20() {
  return (
    <div className="content-stretch flex gap-[4px] items-center relative shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#1fa9a4] text-[0px] text-nowrap tracking-[0.16px]">
        <p className="[text-decoration-skip-ink:none] [text-underline-position:from-font] decoration-solid leading-[1.5] text-[16px] underline whitespace-pre">ATR</p>
      </div>
    </div>
  );
}

function Frame21() {
  return (
    <div className="content-stretch flex flex-col gap-[2px] items-start justify-center relative shrink-0 w-full">
      <Frame20 />
    </div>
  );
}

function Frame61() {
  return (
    <div className="content-stretch flex flex-col gap-[8px] items-start relative shrink-0 w-full">
      <Frame21 />
      <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[14px] tracking-[0.14px] w-full">
        <p className="leading-[1.45]">ATR이 상승하며 가격 변동성이 확대되고 있습니다.</p>
      </div>
    </div>
  );
}

function Frame62() {
  return (
    <div className="bg-[#f2f4f8] relative rounded-[16px] shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[20px] items-start p-[20px] relative w-full">
          <Frame61 />
        </div>
      </div>
    </div>
  );
}

function Frame53() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[8px] items-start px-[20px] py-0 relative w-full">
          <Frame62 />
        </div>
      </div>
    </div>
  );
}

function Frame22() {
  return (
    <div className="content-stretch flex gap-[4px] items-center relative shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#1fa9a4] text-[0px] text-nowrap tracking-[0.16px]">
        <p className="[text-decoration-skip-ink:none] [text-underline-position:from-font] decoration-solid leading-[1.5] text-[16px] underline whitespace-pre">Bollinger Band_B</p>
      </div>
    </div>
  );
}

function Frame23() {
  return (
    <div className="content-stretch flex flex-col gap-[2px] items-start justify-center relative shrink-0 w-full">
      <Frame22 />
    </div>
  );
}

function Frame63() {
  return (
    <div className="content-stretch flex flex-col gap-[8px] items-start relative shrink-0 w-full">
      <Frame23 />
      <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[14px] tracking-[0.14px] w-full">
        <p className="leading-[1.45]">볼린저 밴드가 수축하며 변동성이 낮은 구간에 진입했습니다. 추후 급등락 가능성에 유의해야 합니다.</p>
      </div>
    </div>
  );
}

function Frame64() {
  return (
    <div className="bg-[#f2f4f8] relative rounded-[16px] shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[20px] items-start p-[20px] relative w-full">
          <Frame63 />
        </div>
      </div>
    </div>
  );
}

function Frame52() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[8px] items-start px-[20px] py-0 relative w-full">
          <Frame64 />
        </div>
      </div>
    </div>
  );
}

function Frame24() {
  return (
    <div className="content-stretch flex gap-[4px] items-center relative shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#1fa9a4] text-[0px] text-nowrap tracking-[0.16px]">
        <p className="[text-decoration-skip-ink:none] [text-underline-position:from-font] decoration-solid leading-[1.5] text-[16px] underline whitespace-pre">SMA20</p>
      </div>
    </div>
  );
}

function Frame25() {
  return (
    <div className="content-stretch flex flex-col gap-[2px] items-start justify-center relative shrink-0 w-full">
      <Frame24 />
    </div>
  );
}

function Frame72() {
  return (
    <div className="content-stretch flex flex-col gap-[8px] items-start relative shrink-0 w-full">
      <Frame25 />
      <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[14px] tracking-[0.14px] w-full">
        <p className="leading-[1.45]">현재 주가가 장기 이동평균선을 상회하며 중기적 상승 추세를 유지하고 있어요.</p>
      </div>
    </div>
  );
}

function Frame74() {
  return (
    <div className="bg-[#f2f4f8] relative rounded-[16px] shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[20px] items-start p-[20px] relative w-full">
          <Frame72 />
        </div>
      </div>
    </div>
  );
}

function Frame65() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[8px] items-start px-[20px] py-0 relative w-full">
          <Frame74 />
        </div>
      </div>
    </div>
  );
}

function Frame26() {
  return (
    <div className="content-stretch flex gap-[4px] items-center relative shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#1fa9a4] text-[0px] text-nowrap tracking-[0.16px]">
        <p className="[text-decoration-skip-ink:none] [text-underline-position:from-font] decoration-solid leading-[1.5] text-[16px] underline whitespace-pre">MACD</p>
      </div>
    </div>
  );
}

function Frame27() {
  return (
    <div className="content-stretch flex flex-col gap-[2px] items-start justify-center relative shrink-0 w-full">
      <Frame26 />
    </div>
  );
}

function Frame75() {
  return (
    <div className="content-stretch flex flex-col gap-[8px] items-start relative shrink-0 w-full">
      <Frame27 />
      <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[14px] tracking-[0.14px] w-full">
        <p className="leading-[1.45]">MACD가 시그널선을 하향 돌파하며 매도 신호가 강화되고 있습니다.</p>
      </div>
    </div>
  );
}

function Frame76() {
  return (
    <div className="bg-[#f2f4f8] relative rounded-[16px] shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[20px] items-start p-[20px] relative w-full">
          <Frame75 />
        </div>
      </div>
    </div>
  );
}

function Frame66() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[8px] items-start px-[20px] py-0 relative w-full">
          <Frame76 />
        </div>
      </div>
    </div>
  );
}

function Frame28() {
  return (
    <div className="content-stretch flex gap-[4px] items-center relative shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#1fa9a4] text-[0px] text-nowrap tracking-[0.16px]">
        <p className="[text-decoration-skip-ink:none] [text-underline-position:from-font] decoration-solid leading-[1.5] text-[16px] underline whitespace-pre">MACD_Signal</p>
      </div>
    </div>
  );
}

function Frame29() {
  return (
    <div className="content-stretch flex flex-col gap-[2px] items-start justify-center relative shrink-0 w-full">
      <Frame28 />
    </div>
  );
}

function Frame77() {
  return (
    <div className="content-stretch flex flex-col gap-[8px] items-start relative shrink-0 w-full">
      <Frame29 />
      <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[14px] tracking-[0.14px] w-full">
        <p className="leading-[1.45]">MACD가 시그널선을 하향 돌파하며 매도 신호가 강화되고 있습니다.</p>
      </div>
    </div>
  );
}

function Frame78() {
  return (
    <div className="bg-[#f2f4f8] relative rounded-[16px] shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[20px] items-start p-[20px] relative w-full">
          <Frame77 />
        </div>
      </div>
    </div>
  );
}

function Frame71() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[8px] items-start px-[20px] py-0 relative w-full">
          <Frame78 />
        </div>
      </div>
    </div>
  );
}

function Frame30() {
  return (
    <div className="content-stretch flex gap-[4px] items-center relative shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#1fa9a4] text-[0px] text-nowrap tracking-[0.16px]">
        <p className="[text-underline-position:from-font] decoration-solid leading-[1.5] text-[16px] underline whitespace-pre">VIX</p>
      </div>
    </div>
  );
}

function Frame31() {
  return (
    <div className="content-stretch flex flex-col gap-[2px] items-start justify-center relative shrink-0 w-full">
      <Frame30 />
    </div>
  );
}

function Frame79() {
  return (
    <div className="content-stretch flex flex-col gap-[8px] items-start relative shrink-0 w-full">
      <Frame31 />
      <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[14px] tracking-[0.14px] w-full">
        <p className="leading-[1.45]">거래량이 평균 대비 증가하며 추세에 대한 시장 참여도가 높습니다.</p>
      </div>
    </div>
  );
}

function Frame80() {
  return (
    <div className="bg-[#f2f4f8] relative rounded-[16px] shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[20px] items-start p-[20px] relative w-full">
          <Frame79 />
        </div>
      </div>
    </div>
  );
}

function Frame73() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[8px] items-start px-[20px] py-0 relative w-full">
          <Frame80 />
        </div>
      </div>
    </div>
  );
}

function Frame32() {
  return (
    <div className="content-stretch flex gap-[4px] items-center relative shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#1fa9a4] text-[0px] text-nowrap tracking-[0.16px]">
        <p className="[text-underline-position:from-font] decoration-solid leading-[1.5] text-[16px] underline whitespace-pre">ROA</p>
      </div>
    </div>
  );
}

function Frame33() {
  return (
    <div className="content-stretch flex flex-col gap-[2px] items-start justify-center relative shrink-0 w-full">
      <Frame32 />
    </div>
  );
}

function Frame81() {
  return (
    <div className="content-stretch flex flex-col gap-[8px] items-start relative shrink-0 w-full">
      <Frame33 />
      <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[14px] tracking-[0.14px] w-full">
        <p className="leading-[1.45]">단기 흐름이 장기 흐름보다 강해지며, 최근 주가가 상승세를 타고 있습니다.</p>
      </div>
    </div>
  );
}

function Frame82() {
  return (
    <div className="bg-[#f2f4f8] relative rounded-[16px] shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[20px] items-start p-[20px] relative w-full">
          <Frame81 />
        </div>
      </div>
    </div>
  );
}

function Frame69() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[8px] items-start px-[20px] py-0 relative w-full">
          <Frame82 />
        </div>
      </div>
    </div>
  );
}

function Frame34() {
  return (
    <div className="content-stretch flex gap-[4px] items-center relative shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#1fa9a4] text-[0px] text-nowrap tracking-[0.16px]">
        <p className="[text-underline-position:from-font] decoration-solid leading-[1.5] text-[16px] underline whitespace-pre">DebtRatio</p>
      </div>
    </div>
  );
}

function Frame35() {
  return (
    <div className="content-stretch flex flex-col gap-[2px] items-start justify-center relative shrink-0 w-full">
      <Frame34 />
    </div>
  );
}

function Frame83() {
  return (
    <div className="content-stretch flex flex-col gap-[8px] items-start relative shrink-0 w-full">
      <Frame35 />
      <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[14px] tracking-[0.14px] w-full">
        <p className="leading-[1.45]">시장 지수 대비 상대적으로 강세를 보이며, 시장 평균보다 높은 상승 탄력을 유지하고 있습니다.</p>
      </div>
    </div>
  );
}

function Frame84() {
  return (
    <div className="bg-[#f2f4f8] relative rounded-[16px] shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[20px] items-start p-[20px] relative w-full">
          <Frame83 />
        </div>
      </div>
    </div>
  );
}

function Frame68() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[8px] items-start px-[20px] py-0 relative w-full">
          <Frame84 />
        </div>
      </div>
    </div>
  );
}

function Frame36() {
  return (
    <div className="content-stretch flex gap-[4px] items-center relative shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#1fa9a4] text-[0px] text-nowrap tracking-[0.16px]">
        <p className="[text-decoration-skip-ink:none] [text-underline-position:from-font] decoration-solid leading-[1.5] text-[16px] underline whitespace-pre">AnalystRating</p>
      </div>
    </div>
  );
}

function Frame37() {
  return (
    <div className="content-stretch flex flex-col gap-[2px] items-start justify-center relative shrink-0 w-full">
      <Frame36 />
    </div>
  );
}

function Frame85() {
  return (
    <div className="content-stretch flex flex-col gap-[8px] items-start relative shrink-0 w-full">
      <Frame37 />
      <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[14px] tracking-[0.14px] w-full">
        <p className="leading-[1.45]">V-KOSPI가 상승하며 시장 불확실성이 커지고 있습니다. 보수적인 접근이 필요합니다.</p>
      </div>
    </div>
  );
}

function Frame86() {
  return (
    <div className="bg-[#f2f4f8] relative rounded-[16px] shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[20px] items-start p-[20px] relative w-full">
          <Frame85 />
        </div>
      </div>
    </div>
  );
}

function Frame54() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[8px] items-start px-[20px] py-0 relative w-full">
          <Frame86 />
        </div>
      </div>
    </div>
  );
}

function Frame87() {
  return (
    <div className="box-border content-stretch flex flex-col gap-[16px] items-start px-0 py-[12px] relative shrink-0 w-full">
      <Frame11 />
      <Frame67 />
      <Frame50 />
      <Frame51 />
      <Frame70 />
      <Frame53 />
      <Frame52 />
      <Frame65 />
      <Frame66 />
      <Frame71 />
      <Frame73 />
      <Frame69 />
      <Frame68 />
      <Frame54 />
    </div>
  );
}

function Frame42() {
  return (
    <div className="content-stretch flex flex-col gap-[8px] items-center justify-center relative shrink-0 w-full">
      <Component5 />
      <Frame87 />
    </div>
  );
}

function Frame40() {
  return (
    <div className="box-border content-stretch flex flex-col items-start px-0 py-[16px] relative shrink-0 w-[375px]">
      <Frame42 />
    </div>
  );
}

function Frame43() {
  return (
    <div className="absolute content-stretch flex flex-col items-start left-0 top-[44px]">
      <Component3 />
      <Frame41 />
      <Frame40 />
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

function Component7() {
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
      <Component7 />
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

export default function Component6() {
  return (
    <div className="bg-white relative size-full" data-name="종목 상세">
      <IOsStatusBar />
      <Frame43 />
      <IOsHomeBar />
    </div>
  );
}