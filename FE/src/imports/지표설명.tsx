import svgPaths from "./svg-k8c8cle41f";

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

function Frame10() {
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

function Frame4() {
  return <div className="shrink-0 size-[32px]" />;
}

function Settings() {
  return (
    <div className="relative shrink-0 size-[24px]" data-name="settings">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g id="settings">
          <path clipRule="evenodd" d={svgPaths.p5a876f0} fill="var(--fill-0, #D0D1D4)" fillRule="evenodd" id="Vector" />
        </g>
      </svg>
    </div>
  );
}

function Frame5() {
  return (
    <div className="box-border content-stretch flex gap-[10px] items-center justify-center p-[4px] relative shrink-0">
      <Settings />
    </div>
  );
}

function Component2() {
  return (
    <div className="content-stretch flex gap-[4px] items-center justify-end relative shrink-0" data-name="상단 헤더 우측 버튼">
      <Frame4 />
      <Frame5 />
    </div>
  );
}

function Frame11() {
  return (
    <div className="absolute content-stretch flex items-center justify-center left-[16px] right-[16px] top-1/2 translate-y-[-50%]">
      <Frame10 />
      <Component1 />
      <Component2 />
    </div>
  );
}

function Component3() {
  return (
    <div className="h-[58px] relative shrink-0 w-[375px]" data-name="상단 헤더">
      <Frame11 />
    </div>
  );
}

function Frame1() {
  return (
    <div className="content-stretch flex font-['Pretendard:SemiBold',sans-serif] gap-[4px] items-start leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[10px] text-center text-nowrap tracking-[0.2px]">
      <div className="flex flex-col justify-center relative shrink-0">
        <p className="leading-[1.45] text-nowrap whitespace-pre">신뢰도</p>
      </div>
      <div className="flex flex-col justify-center relative shrink-0">
        <p className="leading-[1.45] text-nowrap whitespace-pre">70.0%</p>
      </div>
    </div>
  );
}

function Frame() {
  return (
    <div className="content-stretch flex flex-col gap-[4px] items-start relative shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:SemiBold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[12px] text-center text-nowrap tracking-[0.24px]">
        <p className="leading-[1.5] whitespace-pre">오늘의 추천 행동</p>
      </div>
      <div className="flex flex-col font-['Pretendard:ExtraBold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#1fa9a4] text-[36px] text-center text-nowrap tracking-[1.44px]">
        <p className="leading-[normal] whitespace-pre">매도</p>
      </div>
      <Frame1 />
    </div>
  );
}

function Frame2() {
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

function Frame35() {
  return (
    <div className="content-stretch flex gap-[4px] items-center relative shrink-0 w-full">
      <Ai />
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[18px] text-center text-nowrap">
        <p className="leading-[1.55] whitespace-pre">AI 설명</p>
      </div>
    </div>
  );
}

function Frame37() {
  return (
    <div className="content-stretch flex font-['Pretendard:SemiBold',sans-serif] gap-[4px] items-start leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[10px] text-center text-nowrap tracking-[0.2px]">
      <div className="flex flex-col justify-center relative shrink-0">
        <p className="leading-[1.45] text-nowrap whitespace-pre">상승 가능성</p>
      </div>
      <div className="flex flex-col justify-center relative shrink-0">
        <p className="leading-[1.45] text-nowrap whitespace-pre">35.0%</p>
      </div>
    </div>
  );
}

function Frame40() {
  return (
    <div className="relative self-stretch shrink-0 w-0">
      <div className="absolute bottom-0 left-[-0.5px] right-[-0.5px] top-0">
        <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 1 15">
          <g id="Frame 26089675">
            <path d="M0.5 2V13" id="Vector 8" stroke="var(--stroke-0, #A1A4A8)" />
          </g>
        </svg>
      </div>
    </div>
  );
}

function Frame38() {
  return (
    <div className="content-stretch flex font-['Pretendard:SemiBold',sans-serif] gap-[4px] items-start leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[10px] text-center text-nowrap tracking-[0.2px]">
      <div className="flex flex-col justify-center relative shrink-0">
        <p className="leading-[1.45] text-nowrap whitespace-pre">신뢰도</p>
      </div>
      <div className="flex flex-col justify-center relative shrink-0">
        <p className="leading-[1.45] text-nowrap whitespace-pre">70.0%</p>
      </div>
    </div>
  );
}

function Frame39() {
  return (
    <div className="content-stretch flex gap-[8px] items-start relative shrink-0 w-full">
      <Frame37 />
      <Frame40 />
      <Frame38 />
    </div>
  );
}

function Frame48() {
  return (
    <div className="content-stretch flex flex-col gap-[8px] items-start relative shrink-0 w-full">
      <Frame35 />
      <Frame39 />
      <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[14px] tracking-[0.14px] w-full">
        <p className="leading-[1.45]">기술적 분석에서 전반적으로 하락세를 유지하고 있으며, 주가는 추가 하락 가능성이 높습니다. 시장 상황에 대한 신중한 접근과 경계를 유지하여 변동성에 대비하는 것이 중요합니다.</p>
      </div>
    </div>
  );
}

function Frame36() {
  return (
    <div className="bg-[#f2f4f8] relative rounded-[16px] shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[20px] items-start p-[20px] relative w-full">
          <Frame />
          <Frame2 />
          <Component4 />
          <Frame48 />
        </div>
      </div>
    </div>
  );
}

function Frame31() {
  return (
    <div className="box-border content-stretch flex flex-col gap-[20px] items-start pb-[24px] pt-[16px] px-[16px] relative shrink-0 w-[375px]">
      <Frame36 />
    </div>
  );
}

function Frame26() {
  return (
    <div className="content-stretch flex gap-[4px] items-center justify-center relative shrink-0">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic overflow-ellipsis overflow-hidden relative shrink-0 text-[#151b26] text-[16px] text-center text-nowrap tracking-[0.16px]">
        <p className="leading-[1.5] overflow-ellipsis overflow-hidden whitespace-pre">추세 분석</p>
      </div>
    </div>
  );
}

function Frame6() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="flex flex-row items-center justify-center overflow-clip rounded-[inherit] size-full">
        <div className="box-border content-stretch flex items-center justify-center pb-[4px] pt-[8px] px-[8px] relative w-full">
          <Frame26 />
        </div>
      </div>
    </div>
  );
}

function Frame7() {
  return <div className="bg-[#151b26] h-[2px] shrink-0 w-full" />;
}

function Tab() {
  return (
    <div className="basis-0 content-stretch flex flex-col gap-[4px] grow items-center justify-center min-h-px min-w-px relative shrink-0" data-name="Tab 1">
      <Frame6 />
      <Frame7 />
    </div>
  );
}

function Frame25() {
  return (
    <div className="content-stretch flex gap-[4px] items-center justify-center relative shrink-0">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic overflow-ellipsis overflow-hidden relative shrink-0 text-[#b9bbbe] text-[16px] text-center text-nowrap tracking-[0.16px]">
        <p className="leading-[1.5] overflow-ellipsis overflow-hidden whitespace-pre">기술지표 분석</p>
      </div>
    </div>
  );
}

function Frame8() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="flex flex-row items-center justify-center overflow-clip rounded-[inherit] size-full">
        <div className="box-border content-stretch flex items-center justify-center pb-[4px] pt-[8px] px-[8px] relative w-full">
          <Frame25 />
        </div>
      </div>
    </div>
  );
}

function Frame9() {
  return <div className="bg-[#e8e8e9] h-[2px] shrink-0 w-full" />;
}

function Tab1() {
  return (
    <div className="basis-0 content-stretch flex flex-col gap-[4px] grow items-center justify-center min-h-px min-w-px relative shrink-0" data-name="Tab 2">
      <Frame8 />
      <Frame9 />
    </div>
  );
}

function Component5() {
  return (
    <div className="box-border content-stretch flex items-center justify-center px-[20px] py-0 relative shrink-0 w-[375px]" data-name="영역 고정 세그먼트 탭">
      <Tab />
      <Tab1 />
    </div>
  );
}

function Frame12() {
  return (
    <div className="content-stretch flex gap-[4px] items-center relative shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[16px] text-nowrap tracking-[0.16px]">
        <p className="leading-[1.5] whitespace-pre">분석 요약</p>
      </div>
    </div>
  );
}

function Frame13() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="flex flex-col justify-center size-full">
        <div className="box-border content-stretch flex flex-col gap-[2px] items-start justify-center px-[20px] py-0 relative w-full">
          <Frame12 />
        </div>
      </div>
    </div>
  );
}

function Frame46() {
  return (
    <div className="absolute content-stretch flex flex-col gap-[2px] items-center justify-center left-[79.5px] top-[-3.49px]">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#1fa9a4] text-[8px] text-nowrap">
        <p className="leading-[1.7] whitespace-pre">현재 위치</p>
      </div>
      <div className="relative shrink-0 size-[4px]" data-name="Section 2">
        <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 4 4">
          <circle cx="2" cy="2" fill="var(--fill-0, #1FA9A4)" id="Section 2" r="2" />
        </svg>
      </div>
    </div>
  );
}

function ProgressIndicatior() {
  return (
    <div className="h-[12px] relative rounded-[64px] shrink-0 w-full" data-name="Progress Indicatior">
      <div className="flex flex-row items-center size-full">
        <div className="h-[12px] w-full" />
      </div>
    </div>
  );
}

function Frame47() {
  return (
    <div className="content-stretch flex font-['Pretendard:Bold',sans-serif] items-start justify-between leading-[0] not-italic relative shrink-0 text-[8px] text-nowrap w-full">
      <div className="flex flex-col justify-center relative shrink-0 text-[#f3646f]">
        <p className="leading-[1.7] text-nowrap whitespace-pre">상승세</p>
      </div>
      <div className="flex flex-col justify-center relative shrink-0 text-[#5c87f2]">
        <p className="leading-[1.7] text-nowrap whitespace-pre">하락세</p>
      </div>
    </div>
  );
}

function Frame45() {
  return (
    <div className="box-border content-stretch flex flex-col gap-[5px] items-start pb-[12px] pt-[24px] px-0 relative shrink-0 w-full">
      <ProgressIndicatior />
      <Frame47 />
    </div>
  );
}

function Frame50() {
  return (
    <div className="content-stretch flex flex-col gap-[8px] items-start relative shrink-0 w-full">
      <Frame46 />
      <Frame45 />
      <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] min-w-full not-italic relative shrink-0 text-[#151b26] text-[14px] tracking-[0.14px] w-[min-content]">
        <p className="leading-[1.45]">단기 추세가 장기 추세를 상회하며 상승세를 유지하고 있고, 거래량도 꾸준히 늘고 있습니다. 다만 MACD가 하락 전환 신호를 보이기 시작해, 단기 조정 가능성은 염두에 두는 것이 좋습니다.</p>
      </div>
    </div>
  );
}

function Frame51() {
  return (
    <div className="bg-[#f2f4f8] relative rounded-[16px] shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[20px] items-start p-[20px] relative w-full">
          <Frame50 />
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
          <Frame51 />
        </div>
      </div>
    </div>
  );
}

function Component6() {
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

function Frame14() {
  return (
    <div className="content-stretch flex gap-[4px] items-center relative shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[16px] text-nowrap tracking-[0.16px]">
        <p className="leading-[1.5] whitespace-pre">추세 분석 상세</p>
      </div>
    </div>
  );
}

function Frame49() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="flex flex-col justify-center size-full">
        <div className="box-border content-stretch flex flex-col gap-[2px] items-start justify-center px-[20px] py-0 relative w-full">
          <Frame14 />
        </div>
      </div>
    </div>
  );
}

function Frame15() {
  return (
    <div className="content-stretch flex gap-[4px] items-center relative shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#1fa9a4] text-[0px] text-nowrap tracking-[0.16px]">
        <p className="[text-decoration-skip-ink:none] [text-underline-position:from-font] decoration-solid leading-[1.5] text-[16px] underline whitespace-pre">EMA (12/26)</p>
      </div>
    </div>
  );
}

function Frame16() {
  return (
    <div className="content-stretch flex flex-col gap-[2px] items-start justify-center relative shrink-0 w-full">
      <Frame15 />
    </div>
  );
}

function Frame53() {
  return (
    <div className="content-stretch flex flex-col gap-[8px] items-start relative shrink-0 w-full">
      <Frame16 />
      <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[14px] tracking-[0.14px] w-full">
        <p className="leading-[1.45]">단기 흐름이 장기 흐름보다 강해지며, 최근 주가가 상승세를 타고 있습니다.</p>
      </div>
    </div>
  );
}

function Frame54() {
  return (
    <div className="bg-[#f2f4f8] relative rounded-[16px] shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[20px] items-start p-[20px] relative w-full">
          <Frame53 />
        </div>
      </div>
    </div>
  );
}

function Frame41() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[8px] items-start px-[20px] py-0 relative w-full">
          <Frame54 />
        </div>
      </div>
    </div>
  );
}

function Frame17() {
  return (
    <div className="content-stretch flex gap-[4px] items-center relative shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#1fa9a4] text-[0px] text-nowrap tracking-[0.16px]">
        <p className="[text-decoration-skip-ink:none] [text-underline-position:from-font] decoration-solid leading-[1.5] text-[16px] underline whitespace-pre">SMA</p>
      </div>
    </div>
  );
}

function Frame18() {
  return (
    <div className="content-stretch flex flex-col gap-[2px] items-start justify-center relative shrink-0 w-full">
      <Frame17 />
    </div>
  );
}

function Frame56() {
  return (
    <div className="content-stretch flex flex-col gap-[8px] items-start relative shrink-0 w-full">
      <Frame18 />
      <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[14px] tracking-[0.14px] w-full">
        <p className="leading-[1.45]">현재 주가가 장기 이동평균선을 상회하며 중기적 상승 추세를 유지하고 있어요.</p>
      </div>
    </div>
  );
}

function Frame57() {
  return (
    <div className="bg-[#f2f4f8] relative rounded-[16px] shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[20px] items-start p-[20px] relative w-full">
          <Frame56 />
        </div>
      </div>
    </div>
  );
}

function Frame42() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[8px] items-start px-[20px] py-0 relative w-full">
          <Frame57 />
        </div>
      </div>
    </div>
  );
}

function Frame19() {
  return (
    <div className="content-stretch flex gap-[4px] items-center relative shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#1fa9a4] text-[0px] text-nowrap tracking-[0.16px]">
        <p className="[text-decoration-skip-ink:none] [text-underline-position:from-font] decoration-solid leading-[1.5] text-[16px] underline whitespace-pre">MACD</p>
      </div>
    </div>
  );
}

function Frame20() {
  return (
    <div className="content-stretch flex flex-col gap-[2px] items-start justify-center relative shrink-0 w-full">
      <Frame19 />
    </div>
  );
}

function Frame58() {
  return (
    <div className="content-stretch flex flex-col gap-[8px] items-start relative shrink-0 w-full">
      <Frame20 />
      <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[14px] tracking-[0.14px] w-full">
        <p className="leading-[1.45]">MACD가 시그널선을 하향 돌파하며 매도 신호가 강화되고 있습니다.</p>
      </div>
    </div>
  );
}

function Frame59() {
  return (
    <div className="bg-[#f2f4f8] relative rounded-[16px] shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[20px] items-start p-[20px] relative w-full">
          <Frame58 />
        </div>
      </div>
    </div>
  );
}

function Frame43() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[8px] items-start px-[20px] py-0 relative w-full">
          <Frame59 />
        </div>
      </div>
    </div>
  );
}

function Frame21() {
  return (
    <div className="content-stretch flex gap-[4px] items-center relative shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#1fa9a4] text-[0px] text-nowrap tracking-[0.16px]">
        <p className="[text-decoration-skip-ink:none] [text-underline-position:from-font] decoration-solid leading-[1.5] text-[16px] underline whitespace-pre">거래량</p>
      </div>
    </div>
  );
}

function Frame22() {
  return (
    <div className="content-stretch flex flex-col gap-[2px] items-start justify-center relative shrink-0 w-full">
      <Frame21 />
    </div>
  );
}

function Frame60() {
  return (
    <div className="content-stretch flex flex-col gap-[8px] items-start relative shrink-0 w-full">
      <Frame22 />
      <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[14px] tracking-[0.14px] w-full">
        <p className="leading-[1.45]">거래량이 평균 대비 증가하며 추세에 대한 시장 참여도가 높습니다.</p>
      </div>
    </div>
  );
}

function Frame61() {
  return (
    <div className="bg-[#f2f4f8] relative rounded-[16px] shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[20px] items-start p-[20px] relative w-full">
          <Frame60 />
        </div>
      </div>
    </div>
  );
}

function Frame44() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[8px] items-start px-[20px] py-0 relative w-full">
          <Frame61 />
        </div>
      </div>
    </div>
  );
}

function Frame23() {
  return (
    <div className="content-stretch flex gap-[4px] items-center relative shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#1fa9a4] text-[0px] text-nowrap tracking-[0.16px]">
        <p className="[text-decoration-skip-ink:none] [text-underline-position:from-font] decoration-solid leading-[1.5] text-[16px] underline whitespace-pre">주가 지수</p>
      </div>
    </div>
  );
}

function Frame24() {
  return (
    <div className="content-stretch flex flex-col gap-[2px] items-start justify-center relative shrink-0 w-full">
      <Frame23 />
    </div>
  );
}

function Frame62() {
  return (
    <div className="content-stretch flex flex-col gap-[8px] items-start relative shrink-0 w-full">
      <Frame24 />
      <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[14px] tracking-[0.14px] w-full">
        <p className="leading-[1.45]">시장 지수 대비 상대적으로 강세를 보이며, 시장 평균보다 높은 상승 탄력을 유지하고 있습니다.</p>
      </div>
    </div>
  );
}

function Frame63() {
  return (
    <div className="bg-[#f2f4f8] relative rounded-[16px] shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[20px] items-start p-[20px] relative w-full">
          <Frame62 />
        </div>
      </div>
    </div>
  );
}

function Frame64() {
  return (
    <div className="relative shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[8px] items-start px-[20px] py-0 relative w-full">
          <Frame63 />
        </div>
      </div>
    </div>
  );
}

function Frame65() {
  return (
    <div className="box-border content-stretch flex flex-col gap-[16px] items-start px-0 py-[12px] relative shrink-0 w-full">
      <Frame13 />
      <Frame52 />
      <Component6 />
      <Frame49 />
      <Frame41 />
      <Frame42 />
      <Frame43 />
      <Frame44 />
      <Frame64 />
    </div>
  );
}

function Frame33() {
  return (
    <div className="content-stretch flex flex-col gap-[8px] items-center justify-center relative shrink-0 w-full">
      <Component5 />
      <Frame65 />
    </div>
  );
}

function Frame32() {
  return (
    <div className="box-border content-stretch flex flex-col items-start px-0 py-[16px] relative shrink-0 w-[375px]">
      <Frame33 />
    </div>
  );
}

function Frame34() {
  return (
    <div className="absolute content-stretch flex flex-col items-start left-0 top-[-569px]">
      <Component3 />
      <Frame31 />
      <Frame32 />
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

function Component14() {
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
      <Component14 />
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

function Frame66() {
  return <div className="absolute bg-[rgba(0,0,0,0.3)] h-[812px] left-1/2 top-1/2 translate-x-[-50%] translate-y-[-50%] w-[375px]" />;
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
    <div className="absolute bg-white bottom-0 h-[34px] left-0 overflow-clip right-0" data-name="iOS_Home Bar">
      <Bar />
    </div>
  );
}

function Component7() {
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

function Frame3() {
  return (
    <div className="content-stretch flex gap-[10px] items-center relative shrink-0 w-full">
      <div className="basis-0 flex flex-col font-['Pretendard:Bold',sans-serif] grow justify-center leading-[0] min-h-px min-w-px not-italic overflow-ellipsis overflow-hidden relative shrink-0 text-[#1fa9a4] text-[18px] text-nowrap">
        <p className="[white-space-collapse:collapse] leading-[1.55] overflow-ellipsis overflow-hidden">EMA (12/26)</p>
      </div>
    </div>
  );
}

function Frame28() {
  return (
    <div className="basis-0 content-stretch flex flex-col gap-[4px] grow items-center justify-center min-h-px min-w-px relative shrink-0">
      <Frame3 />
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

function Frame27() {
  return (
    <div className="box-border content-stretch flex flex-col h-full items-center justify-center overflow-clip p-[2px] relative shrink-0">
      <Close />
    </div>
  );
}

function Component8() {
  return (
    <div className="bg-white relative shrink-0 w-full" data-name="모달 상단 텍스트">
      <div className="flex flex-row items-center justify-center size-full">
        <div className="box-border content-stretch flex gap-[16px] items-center justify-center px-[20px] py-[8px] relative w-full">
          <Frame28 />
          <div className="flex flex-row items-center self-stretch">
            <Frame27 />
          </div>
        </div>
      </div>
    </div>
  );
}

function Component9() {
  return (
    <div className="bg-white box-border content-stretch flex h-px items-center justify-center px-[20px] py-0 relative shrink-0 w-[375px]" data-name="디바이더">
      <div className="basis-0 bg-[#f4f5f5] grow h-full min-h-px min-w-px shrink-0" />
    </div>
  );
}

function Component10() {
  return (
    <div className="bg-white box-border content-stretch flex flex-col gap-[10px] items-center justify-center pb-0 pt-[8px] px-0 relative shrink-0 w-full" data-name="모달 상단 구분선">
      <Component9 />
    </div>
  );
}

function Component11() {
  return (
    <div className="content-stretch flex flex-col items-center justify-center relative shrink-0 w-full" data-name="모달 상단">
      <Component7 />
      <Component8 />
      <Component10 />
    </div>
  );
}

function Frame55() {
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

function Frame67() {
  return (
    <div className="content-stretch flex flex-col gap-[28px] items-start relative shrink-0 w-full">
      <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#444951] text-[14px] tracking-[0.14px] w-full">
        <p className="leading-[1.45]">EMA(지수이동평균선)은 최근 가격에 더 큰 비중을 두고 계산한 평균선이에요. 숫자(12, 26)는 며칠 동안의 평균을 의미합니다.</p>
      </div>
      <Frame55 />
    </div>
  );
}

function Component12() {
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

function Frame29() {
  return (
    <div className="bg-white relative shrink-0 w-full">
      <div className="flex flex-col items-center overflow-clip rounded-[inherit] size-full">
        <div className="box-border content-stretch flex flex-col gap-[30px] items-center pb-0 pt-[16px] px-[20px] relative w-full">
          <Frame67 />
          <Component12 />
        </div>
      </div>
    </div>
  );
}

function Frame30() {
  return (
    <div className="absolute bottom-[34px] content-stretch flex flex-col items-center left-1/2 translate-x-[-50%] w-[375px]">
      <Component11 />
      <Frame29 />
    </div>
  );
}

export default function Component13() {
  return (
    <div className="bg-white relative size-full" data-name="지표 설명">
      <Frame66 />
      <IOsHomeBar />
      <Frame30 />
      <Frame34 />
      <IOsStatusBar />
    </div>
  );
}