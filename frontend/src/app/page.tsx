"use client";

import { useState } from "react";

const REGIONS = [
  "수원시", "성남시", "용인시", "고양시", "부천시",
  "안산시", "화성시", "남양주시", "평택시", "의정부시",
  "시흥시", "파주시", "김포시", "광주시", "광명시",
  "군포시", "하남시", "오산시", "이천시", "안성시",
  "구리시", "의왕시", "포천시", "양주시", "여주시",
  "동두천시", "과천시", "가평군", "양평군", "연천군", "안양시",
];

const BRIEFING_CARDS = [
  {
    emoji: "🌤",
    category: "날씨",
    color: "bg-sky-500",
    lightColor: "bg-sky-50",
    textColor: "text-sky-700",
    title: "오늘 수원시 날씨",
    content: (
      <div className="space-y-1 text-sm text-slate-600">
        <p className="font-medium text-slate-800">최저 18°C / 최고 26°C · 강수확률 20%</p>
        <p>미세먼지: <span className="text-green-600 font-medium">좋음 😊</span></p>
        <p className="text-slate-500">오후부터 맑아지겠습니다.</p>
      </div>
    ),
  },
  {
    emoji: "📰",
    category: "지역 뉴스",
    color: "bg-violet-500",
    lightColor: "bg-violet-50",
    textColor: "text-violet-700",
    title: "오늘의 수원 뉴스 3선",
    content: (
      <ul className="space-y-2 text-sm text-slate-600">
        <li className="flex gap-2"><span className="text-slate-400 shrink-0">•</span>수원시, 광교호수공원 야간 개장 시간 연장 발표</li>
        <li className="flex gap-2"><span className="text-slate-400 shrink-0">•</span>영통구 망포동 일대 도로 공사 이번 주 완료 예정</li>
        <li className="flex gap-2"><span className="text-slate-400 shrink-0">•</span>수원FC, 홈경기 앞두고 팬 이벤트 진행</li>
      </ul>
    ),
  },
  {
    emoji: "🏪",
    category: "동네 가게 소식",
    color: "bg-orange-500",
    lightColor: "bg-orange-50",
    textColor: "text-orange-700",
    title: "이번 주 수원 새 소식",
    content: (
      <div className="space-y-2 text-sm text-slate-600">
        <p>🆕 <span className="font-medium">오픈:</span> 광교 스타필드 B1 '온더보더' (멕시칸)</p>
        <p>🆕 <span className="font-medium">오픈:</span> 영통동 '카페 온도' (카페)</p>
        <p>📋 <span className="font-medium">영업정지:</span> 팔달구 '○○ 치킨' (위생 점검)</p>
      </div>
    ),
  },
];

const FEATURES = [
  {
    emoji: "🤖",
    title: "AI가 자동으로 요약",
    desc: "기상청, 경찰청, 지자체 공공 데이터를 AI가 읽기 쉽게 정리합니다.",
  },
  {
    emoji: "📬",
    title: "매일 아침 8시 발송",
    desc: "출근 전 커피 한 잔과 함께 우리 동네 소식을 확인하세요.",
  },
  {
    emoji: "🔒",
    title: "공공 데이터 기반 신뢰",
    desc: "공식 기관 데이터만 사용해 정확하고 신뢰할 수 있습니다.",
  },
];

function SubscribeForm({ size = "default" }: { size?: "default" | "large" }) {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setEmail("");
      alert("구독 신청이 완료되었습니다! 확인 이메일을 보내드렸습니다.");
    }, 800);
  };

  const isLarge = size === "large";

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className={`flex flex-col sm:flex-row gap-2 mx-auto ${isLarge ? "max-w-lg" : "max-w-md"}`}>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="이메일 주소를 입력하세요"
          required
          className={`flex-1 rounded-xl border border-slate-200 bg-white px-4 text-slate-800 placeholder-slate-400 outline-none focus:border-orange-400 focus:ring-2 focus:ring-orange-100 transition ${isLarge ? "py-4 text-base" : "py-3 text-sm"}`}
        />
        <button
          type="submit"
          disabled={loading}
          className={`shrink-0 rounded-xl bg-orange-500 font-semibold text-white hover:bg-orange-600 active:bg-orange-700 transition disabled:opacity-60 ${isLarge ? "px-7 py-4 text-base" : "px-5 py-3 text-sm"}`}
        >
          {loading ? "처리 중..." : "무료로 구독하기"}
        </button>
      </div>
      <p className="mt-2.5 text-xs text-slate-400">
        ✓ 무료&nbsp;&nbsp;✓ 회원가입 없음&nbsp;&nbsp;✓ 언제든 해지 가능
      </p>
    </form>
  );
}

export default function Home() {
  const scrollToSubscribe = () => {
    document.getElementById("subscribe")?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className="min-h-screen bg-white text-slate-900">

      {/* ── 네비게이션 ── */}
      <nav className="sticky top-0 z-50 border-b border-slate-100 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-5 py-4">
          <span className="text-lg font-bold tracking-tight">🏘️ 동네브리핑</span>
          <button
            onClick={scrollToSubscribe}
            className="rounded-lg bg-orange-500 px-4 py-2 text-sm font-semibold text-white hover:bg-orange-600 transition"
          >
            구독하기
          </button>
        </div>
      </nav>

      {/* ── 히어로 ── */}
      <section id="subscribe" className="mx-auto max-w-5xl px-5 pb-20 pt-20 text-center">
        <span className="mb-6 inline-block rounded-full bg-orange-100 px-4 py-1.5 text-xs font-semibold text-orange-600 tracking-wide">
          매일 오전 8시 자동 발송
        </span>
        <h1 className="mb-5 text-4xl font-extrabold leading-tight tracking-tight text-slate-900 sm:text-5xl lg:text-6xl">
          왜 날씨 앱처럼<br />
          <span className="text-orange-500">동네 소식</span>을 받을 수 없을까요?
        </h1>
        <p className="mx-auto mb-10 max-w-xl text-base text-slate-500 sm:text-lg">
          공공 데이터 + AI 요약으로 매일 아침 우리 동네 브리핑을 자동으로 받아보세요.
          회원가입 없이 이메일만으로.
        </p>

        <div className="flex justify-center">
          <SubscribeForm size="large" />
        </div>

        <p className="mt-8 text-sm text-slate-400">
          🏘️ 수원시 주민 <span className="font-semibold text-slate-600">247명</span>이 구독 중
        </p>
      </section>

      {/* ── 브리핑 미리보기 ── */}
      <section className="bg-slate-50 py-20">
        <div className="mx-auto max-w-5xl px-5">
          <div className="mb-10 text-center">
            <h2 className="text-2xl font-bold text-slate-900 sm:text-3xl">
              오늘의 수원시 브리핑 미리보기
            </h2>
            <p className="mt-2 text-slate-500">실제 발송되는 브리핑과 동일한 형식입니다</p>
          </div>

          <div className="grid gap-5 sm:grid-cols-3">
            {BRIEFING_CARDS.map((card) => (
              <div
                key={card.category}
                className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm"
              >
                <div className={`flex items-center gap-2 px-5 py-3 ${card.lightColor}`}>
                  <span className="text-lg">{card.emoji}</span>
                  <span className={`text-xs font-semibold ${card.textColor}`}>{card.category}</span>
                </div>
                <div className="px-5 py-4">
                  <p className="mb-3 font-semibold text-slate-800">{card.title}</p>
                  {card.content}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── 서비스 특징 ── */}
      <section className="py-20">
        <div className="mx-auto max-w-5xl px-5">
          <div className="mb-12 text-center">
            <h2 className="text-2xl font-bold text-slate-900 sm:text-3xl">왜 동네브리핑인가요?</h2>
          </div>
          <div className="grid gap-8 sm:grid-cols-3">
            {FEATURES.map((f) => (
              <div key={f.title} className="text-center">
                <div className="mb-4 text-4xl">{f.emoji}</div>
                <h3 className="mb-2 text-lg font-bold text-slate-800">{f.title}</h3>
                <p className="text-sm text-slate-500 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── 지역 선택 ── */}
      <section className="bg-slate-50 py-20">
        <div className="mx-auto max-w-5xl px-5 text-center">
          <h2 className="mb-3 text-2xl font-bold text-slate-900 sm:text-3xl">
            경기도 31개 시/군 지원
          </h2>
          <p className="mb-8 text-slate-500">현재 수원시 MVP 운영 중 · 순차적으로 확장 예정</p>
          <div className="flex flex-wrap justify-center gap-2">
            {REGIONS.map((r, i) => (
              <span
                key={r}
                className={`rounded-full px-3 py-1.5 text-xs font-medium ${
                  i === 0
                    ? "bg-orange-500 text-white"
                    : "bg-white border border-slate-200 text-slate-500"
                }`}
              >
                {i === 0 ? `✓ ${r}` : r}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* ── 하단 CTA ── */}
      <section className="bg-slate-900 py-20 text-center">
        <div className="mx-auto max-w-5xl px-5">
          <h2 className="mb-3 text-3xl font-extrabold text-white sm:text-4xl">
            지금 바로 시작하세요
          </h2>
          <p className="mb-10 text-slate-400">
            수원시부터 시작해 경기도 전체로 확장 중입니다
          </p>
          <div className="flex justify-center">
            <SubscribeForm />
          </div>
        </div>
      </section>

      {/* ── 푸터 ── */}
      <footer className="border-t border-slate-100 py-8">
        <div className="mx-auto flex max-w-5xl flex-col items-center justify-between gap-3 px-5 text-sm text-slate-400 sm:flex-row">
          <span>🏘️ 동네브리핑 © 2026</span>
          <a href="mailto:hello@dongne.me" className="hover:text-slate-600 transition">
            hello@dongne.me
          </a>
        </div>
      </footer>

    </div>
  );
}
