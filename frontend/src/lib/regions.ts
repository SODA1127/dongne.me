export type Region = { code: string; name: string; englishCode: string };

export const GYEONGGI_REGIONS: Region[] = [
  { code: "4111000000", name: "수원시", englishCode: "suwon" },
  { code: "4113000000", name: "성남시", englishCode: "seongnam" },
  { code: "4115000000", name: "의정부시", englishCode: "uijeongbu" },
  { code: "4117000000", name: "안양시", englishCode: "anyang" },
  { code: "4119000000", name: "부천시", englishCode: "bucheon" },
  { code: "4121000000", name: "광명시", englishCode: "gwangmyeong" },
  { code: "4122000000", name: "평택시", englishCode: "pyeongtaek" },
  { code: "4125000000", name: "동두천시", englishCode: "dongducheon" },
  { code: "4127000000", name: "안산시", englishCode: "ansan" },
  { code: "4128000000", name: "고양시", englishCode: "goyang" },
  { code: "4129000000", name: "과천시", englishCode: "gwacheon" },
  { code: "4131000000", name: "구리시", englishCode: "guri" },
  { code: "4136000000", name: "남양주시", englishCode: "namyangju" },
  { code: "4137000000", name: "오산시", englishCode: "osan" },
  { code: "4139000000", name: "시흥시", englishCode: "siheung" },
  { code: "4141000000", name: "군포시", englishCode: "gunpo" },
  { code: "4143000000", name: "의왕시", englishCode: "uiwang" },
  { code: "4145000000", name: "하남시", englishCode: "hanam" },
  { code: "4146000000", name: "용인시", englishCode: "yongin" },
  { code: "4148000000", name: "파주시", englishCode: "paju" },
  { code: "4150000000", name: "이천시", englishCode: "icheon" },
  { code: "4155000000", name: "안성시", englishCode: "anseong" },
  { code: "4157000000", name: "김포시", englishCode: "gimpo" },
  { code: "4159000000", name: "화성시", englishCode: "hwaseong" },
  { code: "4161000000", name: "광주시", englishCode: "gwangju" },
  { code: "4163000000", name: "양주시", englishCode: "yangju" },
  { code: "4165000000", name: "포천시", englishCode: "pocheon" },
  { code: "4167000000", name: "여주시", englishCode: "yeoju" },
  { code: "4180000000", name: "연천군", englishCode: "yeoncheon" },
  { code: "4182000000", name: "가평군", englishCode: "gapyeong" },
  { code: "4183000000", name: "양평군", englishCode: "yangpyeong" },
];

export const DEFAULT_REGION = GYEONGGI_REGIONS[0]; // 수원시

export function getRegionByCode(code: string): Region | undefined {
  return GYEONGGI_REGIONS.find((r) => r.code === code);
}

export function getRegionByEnglishCode(englishCode: string): Region | undefined {
  return GYEONGGI_REGIONS.find((r) => r.englishCode === englishCode);
}
