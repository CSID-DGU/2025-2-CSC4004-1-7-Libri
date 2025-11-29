import imgCiLogoMark021 from "figma:asset/4ce6de04287ac1cd44af2322f588b24a7b2ae7c0.png";

export default function Frame() {
  return (
    <div className="bg-white overflow-clip relative rounded-[100px] size-full">
      <div className="absolute h-[23px] left-[calc(50%+2px)] top-[calc(50%+0.5px)] translate-x-[-50%] translate-y-[-50%] w-[28px]" data-name="ci_logo_mark-02 1">
        <div className="absolute inset-0 mix-blend-darken overflow-hidden pointer-events-none">
          <img alt="" className="absolute h-[131.43%] left-0 max-w-none top-[-31.43%] w-[104.55%]" src={imgCiLogoMark021} />
        </div>
      </div>
    </div>
  );
}