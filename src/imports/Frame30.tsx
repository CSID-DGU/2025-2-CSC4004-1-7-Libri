import imgFrame26089667 from "figma:asset/bdac4e7d8d4f71d5aef6253221470dffe73bb6a6.png";

function Frame3() {
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

function Frame5() {
  return (
    <div className="content-stretch flex gap-[12px] items-start relative shrink-0">
      <Frame3 />
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

function Frame4() {
  return (
    <div className="content-stretch flex flex-col gap-[4px] items-end justify-center relative shrink-0">
      <div className="flex flex-col font-['Pretendard:Bold',sans-serif] justify-center leading-[0] not-italic relative shrink-0 text-[#444951] text-[16px] text-center text-nowrap tracking-[0.16px]">
        <p className="leading-[1.5] whitespace-pre">2,967,000원</p>
      </div>
      <Frame2 />
    </div>
  );
}

function Frame6() {
  return (
    <div className="content-stretch flex items-start justify-between relative shrink-0 w-full">
      <Frame5 />
      <Frame4 />
    </div>
  );
}

export default function Frame() {
  return (
    <div className="bg-[#f2f4f8] relative rounded-[16px] size-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[8px] items-start overflow-clip px-[20px] py-[16px] relative size-full">
          <Frame6 />
        </div>
      </div>
    </div>
  );
}