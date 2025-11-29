import svgPaths from "../imports/svg-jt07di20lr";
import svgPathsTrading from "../imports/svg-g85yiot6ll";
import { useEffect, useRef, useState, useContext } from 'react';
import { useInvestmentStyle } from '../contexts/InvestmentStyleContext';
import { createChart } from 'lightweight-charts';
import IndicatorModal from './IndicatorModal';
import { getIndicatorsByStyle } from '../data/indicatorsByStyle';
import { type InvestmentStyle } from '../contexts/InvestmentStyleContext';

type TabType = 'analysis' | 'trading';

interface IndicatorInfo {
  title: string;
  description: string;
  fullDescription: string;
  interpretationPoints: string[];
}

const indicatorData: Record<string, IndicatorInfo> = {
  'EMA 12': {
    title: 'EMA 12',
    description: '단기 흐름이 장기 흐름보다 강해지며, 최근 주가가 상승세를 타고 있습니다.',
    fullDescription: 'EMA(지수이동평균선)은 최근 가격에 더 큰 비중을 두고 계산한 평균선이에요. 숫자(12)는 12일 동안의 평균을 의미합니다.',
    interpretationPoints: [
      '단기(EMA12)가 장기(EMA26)를 뚫으면 상승 신호',
      '반대로 내려가면 하락 신호'
    ]
  },
  'EMA 26': {
    title: 'EMA 26',
    description: '장기 추세를 나타내며, 현재 안정적인 상승세를 보이고 있습니다.',
    fullDescription: 'EMA(지수이동평균선)은 최근 가격에 더 큰 비중을 두고 계산한 평균선이에요. 숫자(26)는 26일 동안의 평균을 의미합니다.',
    interpretationPoints: [
      '장기 추세를 확인하는 지표로 활용',
      'EMA12와 함께 보면서 추세 전환 시점 파악'
    ]
  },
  'MACD': {
    title: 'MACD',
    description: 'MACD가 시그널선을 하향 돌파하며 매도 신호가 강화되고 있습니다.',
    fullDescription: 'MACD(이동평균수렴확산)는 단기와 장기 이동평균선의 차이를 이용한 추세 추종 지표입니다. 추세의 방향과 강도를 동시에 파악할 수 있어요.',
    interpretationPoints: [
      'MACD선이 시그널선을 상향 돌파하면 매수 신호',
      'MACD선이 시그널선을 하향 돌파하면 매도 신호',
      '0선 위에 있으면 상승 추세, 아래면 하락 추세'
    ]
  },
  '거래량': {
    title: '거래량',
    description: '거래량이 평균 대비 증가하며 추세에 대한 시장 참여도가 높습니다.',
    fullDescription: '거래량은 특정 기간 동안 거래된 주식의 수량을 나타냅니다. 가격 변동과 함께 분석하면 추세의 신뢰도를 확인할 수 있어요.',
    interpretationPoints: [
      '상승과 함께 거래량 증가는 강한 상승 신호',
      '하락과 함께 거래량 증가는 강한 하락 신호',
      '거래량 없는 가격 변동은 신뢰도가 낮음'
    ]
  },
  'KOSPI': {
    title: 'KOSPI',
    description: '시장 지수 대비 상대적으로 강세를 보이며, 시장 평균보다 높은 상승 탄력을 유지하고 있습니다.',
    fullDescription: 'KOSPI는 한국 종합주가지수로, 전체 시장의 흐름을 나타냅니다. 개별 종목이 시장 대비 얼마나 강한지 비교할 수 있어요.',
    interpretationPoints: [
      '시장이 상승하는데 종목도 상승하면 강세',
      '시장이 하락하는데 종목이 상승하면 매우 강세',
      '시장 대비 상대적 강도로 투자 판단'
    ]
  },
  'SMA20': {
    title: 'SMA20',
    description: '현재 주가가 장기 이동평균선을 상회하며 중기적 상승 추세를 유지하고 있어요.',
    fullDescription: 'SMA(단순이동평균선)는 일정 기간 동안의 종가를 산술 평균한 값입니다. 20일 평균은 중기 추세를 나타내요.',
    interpretationPoints: [
      '주가가 SMA20 위에 있으면 상승 추세',
      '주가가 SMA20 아래로 떨어지면 하락 신호',
      '장기 투자 시 중요한 지지/저항선으로 활용'
    ]
  },
  'RSI': {
    title: 'RSI',
    description: 'RSI가 과매수 구간(70 이상)에 진입하여 단기 조정 가능성이 있습니다.',
    fullDescription: 'RSI(상대강도지수)는 가격의 상승과 하락 강도를 비교하여 과매수/과매도 상태를 판단하는 지표입니다. 0~100 사이의 값을 가져요.',
    interpretationPoints: [
      'RSI 70 이상은 과매수 구간, 조정 가능성',
      'RSI 30 이하는 과매도 구간, 반등 가능성',
      '50을 기준으로 상승/하락 추세 판단'
    ]
  },
  'STOCH_%K': {
    title: 'STOCH_%K',
    description: '스토캐스틱이 과매수 구간에서 하락 전환하며 단기 조정 신호를 보이고 있습니다.',
    fullDescription: '스토캐스틱은 일정 기간 동안의 가격 변동 폭 중 현재 가격의 위치를 백분율로 나타낸 지표입니다. 과매수/과매도를 빠르게 포착해요.',
    interpretationPoints: [
      '%K가 80 이상에서 하락 전환하면 매도 신호',
      '%K가 20 이하에서 상승 전환하면 매수 신호',
      '%K와 %D의 교차로 매매 타이밍 포착'
    ]
  }
};

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

function BackButton({ onClick }: { onClick: () => void }) {
  return (
    <button onClick={onClick} className="box-border content-stretch flex gap-[10px] items-center p-[4px] relative shrink-0" data-name="상단 헤더 좌측 버튼">
      <CaretLeft />
    </button>
  );
}

function Frame7({ onBack }: { onBack: () => void }) {
  return (
    <div className="content-stretch flex gap-[10px] items-center relative shrink-0 w-[68px]">
      <BackButton onClick={onBack} />
    </div>
  );
}

function Component1({ stockName }: { stockName: string }) {
  return (
    <div className="basis-0 grow min-h-px min-w-px relative shrink-0" data-name="헤더 타이틀">
      <div className="flex flex-row items-center justify-center size-full">
        <div className="box-border content-stretch flex gap-[10px] items-center justify-center px-[4px] py-[2px] relative w-full">
          <div className="basis-0 flex flex-col grow justify-center leading-[0] min-h-px min-w-px not-italic overflow-ellipsis overflow-hidden relative shrink-0 text-[#151b26] text-center text-nowrap onboarding-top">
            <p className="[white-space-collapse:collapse] leading-[1.55] overflow-ellipsis overflow-hidden">{stockName}</p>
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

function Frame8({ stockName, onBack }: { stockName: string; onBack: () => void }) {
  return (
    <div className="absolute content-stretch flex items-center justify-center left-[16px] right-[16px] top-1/2 translate-y-[-50%]">
      <Frame7 onBack={onBack} />
      <Component1 stockName={stockName} />
      <Component2 />
    </div>
  );
}

function Component3({ stockName, onBack }: { stockName: string; onBack: () => void }) {
  return (
    <div className="h-[58px] relative shrink-0 w-[375px]" data-name="상단 헤더">
      <Frame8 stockName={stockName} onBack={onBack} />
    </div>
  );
}

function Frame48({ recommendation }: { recommendation: string }) {
  return (
    <div className="basis-0 content-stretch flex flex-col gap-[4px] grow items-start leading-[0] min-h-px min-w-px not-italic relative shrink-0 text-center text-nowrap">
      <div className="flex flex-col justify-center relative shrink-0 text-[#151b26] tracking-[0.24px] stock-recommend-title">
        <p className="leading-[1.5] text-nowrap whitespace-pre">오늘의 추천 행동</p>
      </div>
      <div className="flex flex-col justify-center relative shrink-0 text-[#1fa9a4] tracking-[1.44px] stock-recommend">
        <p className="leading-[normal] text-nowrap whitespace-pre">{recommendation}</p>
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

function Frame88({ recommendation }: { recommendation: string }) {
  return (
    <div className="content-stretch flex gap-[20px] items-start relative shrink-0 w-full">
      <Frame48 recommendation={recommendation} />
      <Info />
    </div>
  );
}

function PriceChart() {
  const chartContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // 백엔드에서 받아올 주가 데이터 (Mock 데이터)
    // 실제로는 API 호출로 데이터를 받아옴
    const generateMockData = () => {
      const data = [];
      const basePrice = 60000;
      const now = new Date();
      
      for (let i = 30; i >= 0; i--) {
        const date = new Date(now);
        date.setDate(date.getDate() - i);
        const randomChange = (Math.random() - 0.5) * 3000;
        const price = basePrice + randomChange + (30 - i) * 100;
        
        data.push({
          time: Math.floor(date.getTime() / 1000) as any,
          value: price
        });
      }
      return data;
    };

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { color: 'transparent' },
        textColor: '#1FA9A4',
      },
      grid: {
        vertLines: { visible: false },
        horzLines: { visible: false },
      },
      width: chartContainerRef.current.clientWidth,
      height: 43,
      timeScale: {
        visible: false,
        borderVisible: false,
        fixLeftEdge: true,
        fixRightEdge: true,
      },
      rightPriceScale: {
        visible: false,
        borderVisible: false,
      },
      leftPriceScale: {
        visible: false,
        borderVisible: false,
      },
      crosshair: {
        mode: 0,
      },
      handleScale: false,
      handleScroll: false,
    });

    const lineSeries = chart.addAreaSeries({
      lineColor: '#1FA9A4',
      lineWidth: 2,
      topColor: 'transparent',
      bottomColor: 'transparent',
      priceLineVisible: false,
      lastValueVisible: false,
      crosshairMarkerVisible: false,
    });

    lineSeries.setData(generateMockData());

    // 차트를 왼쪽 끝까지 확장
    chart.timeScale().fitContent();

    // TradingView 워터마크 제거 - 간소화된 버전
    const removeWatermark = () => {
      if (!chartContainerRef.current) return;
      
      // 워터마크는 보통 작은 크기의 div나 a 태그로 구성됨
      const allElements = chartContainerRef.current.querySelectorAll('div, a, img');
      allElements.forEach((el) => {
        const element = el as HTMLElement;
        const text = element.textContent?.toLowerCase() || '';
        const href = (element as HTMLAnchorElement).href || '';
        
        // TradingView 관련 텍스트나 링크를 포함하는 작은 요소 숨김
        if ((text.includes('tradingview') || href.includes('tradingview')) && 
            element.offsetHeight < 50) {
          element.style.display = 'none';
        }
      });
    };

    // 차트 렌더링 직후와 약간의 지연 후에 워터마크 제거
    removeWatermark();
    const timerId = setTimeout(removeWatermark, 100);

    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({ width: chartContainerRef.current.clientWidth });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      clearTimeout(timerId);
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, []);

  return (
    <div 
      ref={chartContainerRef} 
      className="absolute inset-[-2.92%_-0.17%_-3.46%_-0.23%]"
    />
  );
}

function Frame() {
  return (
    <div className="box-border content-stretch flex flex-col gap-[10px] items-start px-0 py-[8px] relative shrink-0 w-full">
      <div className="aspect-[284.59/37.0933] relative shrink-0 w-full">
        <PriceChart />
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
      <div className="flex flex-col justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-center text-nowrap onboarding-top">
        <p className="leading-[1.55] whitespace-pre">AI 설명</p>
      </div>
    </div>
  );
}

function Frame49({ aiExplanation }: { aiExplanation: string }) {
  return (
    <div className="content-stretch flex flex-col gap-[8px] items-start relative shrink-0 w-full">
      <Frame44 />
      <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[14px] tracking-[0.14px] w-full">
        <p className="leading-[1.45]">{aiExplanation}</p>
      </div>
    </div>
  );
}

function Frame45({ recommendation, aiExplanation }: { recommendation: string; aiExplanation: string }) {
  return (
    <div className="bg-[#f2f4f8] relative rounded-[16px] shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[20px] items-start p-[20px] relative w-full">
          <Frame88 recommendation={recommendation} />
          <Frame />
          <Component4 />
          <Frame49 aiExplanation={aiExplanation} />
        </div>
      </div>
    </div>
  );
}

function Frame41({ recommendation, aiExplanation }: { recommendation: string; aiExplanation: string }) {
  return (
    <div className="box-border content-stretch flex flex-col gap-[20px] items-start pb-[24px] pt-[16px] px-[16px] relative shrink-0 w-[375px]">
      <Frame45 recommendation={recommendation} aiExplanation={aiExplanation} />
    </div>
  );
}

function Frame38({ isActive }: { isActive: boolean }) {
  return (
    <div className="content-stretch flex gap-[4px] items-center justify-center relative shrink-0">
      <div className={`flex flex-col justify-center leading-[0] not-italic overflow-ellipsis overflow-hidden relative shrink-0 text-center text-nowrap tracking-[0.16px] home-stock-name ${isActive ? 'text-[#151b26]' : 'text-[#a1a4a8]'}`}>
        <p className="leading-[1.5] overflow-ellipsis overflow-hidden whitespace-pre">지표 분석</p>
      </div>
    </div>
  );
}

function Frame3({ isActive }: { isActive: boolean }) {
  return (
    <div className="relative shrink-0 w-full">
      <div className="flex flex-row items-center justify-center overflow-clip rounded-[inherit] size-full">
        <div className="box-border content-stretch flex items-center justify-center pb-[4px] pt-[8px] px-[8px] relative w-full">
          <Frame38 isActive={isActive} />
        </div>
      </div>
    </div>
  );
}

function Frame6({ isActive }: { isActive: boolean }) {
  return <div className={`h-[2px] shrink-0 w-full ${isActive ? 'bg-[#151b26]' : 'bg-[#e8e8e9]'}`} />;
}

function Tab1({ isActive, onClick }: { isActive: boolean; onClick: () => void }) {
  return (
    <button 
      onClick={onClick}
      className="basis-0 content-stretch flex flex-col gap-[4px] grow items-center justify-center min-h-px min-w-px relative shrink-0 cursor-pointer" 
      data-name="Tab 2"
    >
      <Frame3 isActive={isActive} />
      <Frame6 isActive={isActive} />
    </button>
  );
}

function Ai1({ isActive }: { isActive: boolean }) {
  return (
    <div className="relative shrink-0 size-[18px]" data-name="AI">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 18 18">
        <g id="AI">
          <path clipRule="evenodd" d={svgPaths.p1036f280} fill={isActive ? '#151B26' : '#A1A4A8'} fillRule="evenodd" id="Vector" />
        </g>
      </svg>
    </div>
  );
}

function Frame39({ isActive }: { isActive: boolean }) {
  return (
    <div className="content-stretch flex gap-[4px] items-center justify-center relative shrink-0">
      <div className={`flex flex-col justify-center leading-[0] not-italic overflow-ellipsis overflow-hidden relative shrink-0 text-center text-nowrap tracking-[0.16px] home-stock-name ${isActive ? 'text-[#151b26]' : 'text-[#a1a4a8]'}`}>
        <p className="leading-[1.5] overflow-ellipsis overflow-hidden whitespace-pre">AI 거래 내역</p>
      </div>
    </div>
  );
}

function Frame4({ isActive }: { isActive: boolean }) {
  return (
    <div className="relative shrink-0 w-full">
      <div className="flex flex-row items-center justify-center overflow-clip rounded-[inherit] size-full">
        <div className="box-border content-stretch flex gap-[4px] items-center justify-center pb-[4px] pt-[8px] px-[8px] relative w-full">
          <Ai1 isActive={isActive} />
          <Frame39 isActive={isActive} />
        </div>
      </div>
    </div>
  );
}

function Frame5({ isActive }: { isActive: boolean }) {
  return <div className={`h-[2px] shrink-0 w-full ${isActive ? 'bg-[#151b26]' : 'bg-[#e8e8e9]'}`} />;
}

function Tab({ isActive, onClick }: { isActive: boolean; onClick: () => void }) {
  return (
    <button 
      onClick={onClick}
      className="basis-0 content-stretch flex flex-col gap-[4px] grow items-center justify-center min-h-px min-w-px relative shrink-0 cursor-pointer" 
      data-name="Tab 1"
    >
      <Frame4 isActive={isActive} />
      <Frame5 isActive={isActive} />
    </button>
  );
}

function Component5({ activeTab, onTabChange }: { activeTab: TabType; onTabChange: (tab: TabType) => void }) {
  return (
    <div className="box-border content-stretch flex items-center justify-center px-[20px] py-0 relative shrink-0 w-[375px]" data-name="영역 고정 세그먼트 탭">
      <Tab1 isActive={activeTab === 'analysis'} onClick={() => onTabChange('analysis')} />
      <Tab isActive={activeTab === 'trading'} onClick={() => onTabChange('trading')} />
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
    <div className="box-border content-stretch flex flex-col gap-[16px] items-start pb-0 pt-[12px] px-0 relative shrink-0 w-full">
      <div className="relative shrink-0 w-full">
        <div className="flex flex-row items-center size-full">
          <div className="box-border content-stretch flex gap-[2px] items-center px-[20px] py-0 relative w-full">
            <Frame9 />
            <Frame10 />
          </div>
        </div>
      </div>
    </div>
  );
}

function IndicatorCard({ title, description, onClick }: { title: string; description: string; onClick: () => void }) {
  return (
    <div className="relative shrink-0 w-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[8px] items-start px-[20px] py-0 relative w-full">
          <button onClick={onClick} className="bg-[#f2f4f8] relative rounded-[16px] shrink-0 w-full text-left">
            <div className="size-full">
              <div className="box-border content-stretch flex flex-col gap-[20px] items-start p-[20px] relative w-full">
                <div className="content-stretch flex flex-col gap-[8px] items-start relative shrink-0 w-full">
                  <div className="content-stretch flex flex-col gap-[2px] items-start justify-center relative shrink-0 w-full">
                    <div className="content-stretch flex gap-[4px] items-center relative shrink-0 w-full">
                      <div className="flex flex-col justify-center leading-[0] not-italic relative shrink-0 text-[#1fa9a4] text-[0px] text-nowrap tracking-[0.16px]">
                        <p className="[text-decoration-skip-ink:none] leading-[1.5] whitespace-pre card-title">{title}</p>
                      </div>
                    </div>
                  </div>
                  <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[14px] tracking-[0.14px] w-full">
                    <p className="leading-[1.45]">{description}</p>
                  </div>
                </div>
              </div>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
}

function AnalysisContent({ onIndicatorClick, investmentStyle }: { 
  onIndicatorClick: (indicator: IndicatorInfo) => void;
  investmentStyle: InvestmentStyle;
}) {
  const indicators = getIndicatorsByStyle(investmentStyle);
  
  return (
    <div className="basis-0 content-stretch flex flex-col gap-[8px] grow min-h-px min-w-px relative shrink-0">
      <Frame11 />
      {indicators.map((indicator) => (
        <IndicatorCard 
          key={indicator.id}
          title={indicator.title} 
          description={indicator.shortDescription}
          onClick={() => onIndicatorClick({
            title: indicator.title,
            description: indicator.shortDescription,
            fullDescription: indicator.detailedDescription,
            interpretationPoints: indicator.interpretationPoints
          })}
        />
      ))}
    </div>
  );
}

// AI 거래 내역 타입 정의
interface Trade {
  type: 'buy' | 'sell';
  quantity: number;
  pricePerShare: number;
  time: string;
  profit?: number;
  profitPercent?: number;
}

interface DayTrading {
  date: string;
  trades: Trade[];
}

// Mock 데이터 - 백엔드에서 하루에 한 번씩 AI 결정을 받아올 예정
const mockTradingHistory: DayTrading[] = [
  {
    date: '오늘',
    trades: [
      {
        type: 'sell',
        quantity: 10,
        pricePerShare: 63830,
        time: '14:22',
        profit: 12830,
        profitPercent: 22.3
      },
      {
        type: 'buy',
        quantity: 10,
        pricePerShare: 51000,
        time: '14:22'
      }
    ]
  },
  {
    date: '어제',
    trades: [
      {
        type: 'sell',
        quantity: 10,
        pricePerShare: 58200,
        time: '14:22',
        profit: -12830,
        profitPercent: -22.3
      },
      {
        type: 'buy',
        quantity: 10,
        pricePerShare: 71030,
        time: '14:23'
      }
    ]
  },
  {
    date: '11월 19일',
    trades: [
      {
        type: 'sell',
        quantity: 100,
        pricePerShare: 45670,
        time: '14:22',
        profit: -12830,
        profitPercent: -22.3
      },
      {
        type: 'buy',
        quantity: 100,
        pricePerShare: 58500,
        time: '14:23'
      }
    ]
  }
];

function InfoIconTrading() {
  return (
    <div className="relative shrink-0 size-[16px]" data-name="info">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 16 16">
        <g id="info">
          <g id="Vector">
            <path d={svgPathsTrading.p2202000} fill="#A1A4A8" />
            <path d={svgPathsTrading.p376400} fill="#A1A4A8" />
            <path clipRule="evenodd" d={svgPathsTrading.p120eb380} fill="#A1A4A8" fillRule="evenodd" />
          </g>
        </g>
      </svg>
    </div>
  );
}

function TradingHistoryHeader() {
  return (
    <div className="box-border content-stretch flex flex-col gap-[16px] items-start pb-0 pt-[12px] px-0 relative shrink-0 w-full">
      <div className="relative shrink-0 w-full">
        <div className="flex flex-row items-center size-full">
          <div className="box-border content-stretch flex gap-[2px] items-center px-[20px] py-0 relative w-full">
            <div className="basis-0 content-stretch flex gap-[4px] grow items-center min-h-px min-w-px relative shrink-0">
              <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[12px] text-nowrap tracking-[0.24px]">
                <p className="leading-[1.5] whitespace-pre">오늘</p>
              </div>
            </div>
            <div className="content-stretch flex gap-[2px] items-center relative shrink-0">
              <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[12px] text-nowrap tracking-[0.24px]">
                <p className="leading-[1.5] whitespace-pre">AI 거래 내역 안내</p>
              </div>
              <InfoIconTrading />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function TradeDivider() {
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

function TradeItem({ trade }: { trade: Trade }) {
  const isSell = trade.type === 'sell';
  const hasProfitInfo = trade.profit !== undefined;
  
  return (
    <>
      <div className="relative shrink-0 w-full">
        <div className="size-full">
          <div className="box-border content-stretch flex flex-col gap-[8px] items-start px-[20px] py-0 relative w-full">
            <div className="box-border content-stretch flex flex-col gap-[4px] items-start px-0 py-[8px] relative rounded-[16px] shrink-0 w-full">
              <div className="content-stretch flex flex-col items-start relative shrink-0 w-full">
                <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#151b26] text-[16px] tracking-[0.16px] w-full">
                  <p className="leading-[1.5]">{trade.quantity}주 {isSell ? '판매' : '구매'}</p>
                </div>
                {hasProfitInfo && (
                  <div className="content-stretch flex font-['Pretendard:Bold',sans-serif] gap-[4px] items-start leading-[0] not-italic relative shrink-0 text-[16px] text-nowrap tracking-[0.16px] w-full">
                    <div className={`flex flex-col justify-center relative shrink-0 ${trade.profit! > 0 ? 'text-[#f3646f]' : 'text-[#5c87f2]'}`}>
                      <p className="leading-[1.5] text-nowrap whitespace-pre">{trade.profit! > 0 ? '+' : ''}{trade.profit!.toLocaleString()}원</p>
                    </div>
                    <div className={`flex flex-col justify-center relative shrink-0 ${trade.profit! > 0 ? 'text-[#f3646f]' : 'text-[#5c87f2]'}`}>
                      <p className="leading-[1.5] text-nowrap whitespace-pre">({trade.profitPercent! > 0 ? '+' : ''}{trade.profitPercent}%)</p>
                    </div>
                  </div>
                )}
              </div>
              <div className="content-stretch flex items-start relative shrink-0 w-full">
                <div className="flex flex-col font-['Pretendard:SemiBold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[11px] text-nowrap tracking-[0.22px]">
                  <p className="leading-[1.45] whitespace-pre">{trade.time}</p>
                </div>
                <div className="flex flex-col font-['Pretendard:SemiBold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[11px] text-nowrap tracking-[0.22px]">
                  <p className="leading-[1.45] whitespace-pre">・</p>
                </div>
                <div className="content-stretch flex gap-[4px] items-center relative shrink-0">
                  <div className="flex flex-col font-['Pretendard:SemiBold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[11px] text-nowrap tracking-[0.22px]">
                    <p className="leading-[1.45] whitespace-pre">1주당</p>
                  </div>
                  <div className="content-stretch flex font-['Pretendard:SemiBold',sans-serif] items-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[11px] text-nowrap tracking-[0.22px]">
                    <div className="flex flex-col justify-center relative shrink-0">
                      <p className="leading-[1.45] text-nowrap whitespace-pre">{trade.pricePerShare.toLocaleString()}원</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <TradeDivider />
    </>
  );
}

function DaySection({ dayTrading }: { dayTrading: DayTrading }) {
  return (
    <div className="box-border content-stretch flex flex-col gap-[16px] items-start pb-0 pt-[12px] px-0 relative shrink-0 w-full">
      <div className="relative shrink-0 w-full">
        <div className="flex flex-row items-center size-full">
          <div className="box-border content-stretch flex gap-[2px] items-center px-[20px] py-0 relative w-full">
            <div className="basis-0 content-stretch flex gap-[4px] grow items-center min-h-px min-w-px relative shrink-0">
              <div className="flex flex-col font-['Pretendard:Medium',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#a1a4a8] text-[12px] text-nowrap tracking-[0.24px]">
                <p className="leading-[1.5] whitespace-pre">{dayTrading.date}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="content-stretch flex flex-col gap-[8px] items-start relative shrink-0 w-full">
        {dayTrading.trades.map((trade, index) => (
          <TradeItem key={index} trade={trade} />
        ))}
      </div>
    </div>
  );
}

function TradingHistory() {
  return (
    <div className="w-full flex flex-col gap-[8px] pb-[40px]">
      <TradingHistoryHeader />
      {mockTradingHistory.map((dayTrading, index) => (
        <DaySection key={index} dayTrading={dayTrading} />
      ))}
    </div>
  );
}

function Frame43({ stockName, onBack, recommendation, aiExplanation, activeTab, onTabChange, onIndicatorClick, investmentStyle }: { 
  stockName: string; 
  onBack: () => void;
  recommendation: string;
  aiExplanation: string;
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
  onIndicatorClick: (indicator: IndicatorInfo) => void;
  investmentStyle: InvestmentStyle;
}) {
  return (
    <div className="absolute inset-[50px_0px_32px_0px] overflow-y-auto flex justify-center">
      <div className="flex flex-col min-h-full w-[375px]">
        <Component3 stockName={stockName} onBack={onBack} />
        <Frame41 recommendation={recommendation} aiExplanation={aiExplanation} />
        <Component5 activeTab={activeTab} onTabChange={onTabChange} />
        <div className="flex-1">
          {activeTab === 'analysis' ? <AnalysisContent onIndicatorClick={onIndicatorClick} investmentStyle={investmentStyle} /> : <TradingHistory />}
        </div>
      </div>
    </div>
  );
}

function NetworkSignalLight() {
  return (
    <div className="h-[14px] relative shrink-0 w-[20px]" data-name="Network Signal / Light">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 20 14">
        <g id="Network Signal / Light">
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

function Notch() {
  return <div className="absolute h-[30px] left-0 right-0 top-0" data-name="Notch" />;
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

function Bar() {
  return <div className="absolute bg-[#151b26] bottom-[8px] h-[5px] left-1/2 rounded-[100px] translate-x-[-50%] w-[134px]" data-name="Bar" />;
}

function IOsHomeBar() {
  return (
    <div className="absolute bottom-0 h-[34px] left-0 overflow-clip right-0" data-name="iOS_Home Bar">
      <Bar />
    </div>
  );
}

interface StockDetailProps {
  stockName: string;
  investmentStyle: InvestmentStyle;
  onBack: () => void;
}

export default function StockDetail({ stockName, investmentStyle, onBack }: StockDetailProps) {
  const [activeTab, setActiveTab] = useState<TabType>('analysis');
  const [selectedIndicator, setSelectedIndicator] = useState<IndicatorInfo | null>(null);

  // 투자 성향에 따라 다른 AI 모델 결과 표시
  const { modelType } = useInvestmentStyle();
  
  const getRecommendationByStyle = () => {
    // 모델 타입에 따라 다른 설명 제공
    const modelExplanations = {
      marl_4agent: {
        recommendation: '매수',
        aiExplanation: '4-에이전트 모델 분석: 단기/장기/위험/감성 에이전트가 종합 분석한 결과, 현재 매수 타이밍으로 판단됩니다. 단기 변동성은 있으나, 중장기적으로 상승 가능성이 높습니다.'
      },
      marl_3agent: {
        recommendation: '보유',
        aiExplanation: '3-에이전트 모델 분석: 안정적인 수익을 목표로 하는 전략으로, 현재 주가는 적정 수준이며 추가 상승 가능성이 있습니다. 리스크를 최소화하며 수익을 추구하는 전략입니다.'
      }
    };
    
    // 모델 타입에 따라 적절한 설명 반환
    return modelExplanations[modelType as keyof typeof modelExplanations] || modelExplanations.marl_4agent;
  };

  const { recommendation, aiExplanation } = getRecommendationByStyle();

  return (
    <div className="bg-white relative min-h-screen w-full" data-name="종목 상세">
      <IOsStatusBar />
      <Frame43 
        stockName={stockName} 
        onBack={onBack}
        recommendation={recommendation}
        aiExplanation={aiExplanation}
        activeTab={activeTab}
        onTabChange={setActiveTab}
        onIndicatorClick={setSelectedIndicator}
        investmentStyle={investmentStyle}
      />
      <IOsHomeBar />
      <IndicatorModal 
        indicator={selectedIndicator}
        onClose={() => setSelectedIndicator(null)}
      />
    </div>
  );
}
