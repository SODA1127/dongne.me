import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "동네브리핑 | 매일 아침 동네 소식",
  description: "경기도 시/군별 매일 아침 동네 소식을 이메일로 받아보세요. 지역 뉴스, 날씨, 생활 정보를 한 번에.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
