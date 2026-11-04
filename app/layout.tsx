import type { Metadata } from "next";
import Script from "next/script";
import type { ReactNode } from "react";
import markup from "../generated/pageMarkup.json";
import "../public/assets/site.css";
import "../public/assets/cinema.css";
import "../public/assets/story-media.css";

export const metadata: Metadata = {
  title: "Ngày mai, mình sẽ… | Hành trình lịch sử 1930–2026",
  description: "Website kể chuyện tương tác bằng tiếng Việt qua 12 chương, 55 cảnh — lịch sử Đảng 1930–2026. Bản thảo cần thẩm định lịch sử.",
  robots: { index: false, follow: false }, // Flip only after factual & rights sign-off.
  openGraph: {
    title: "Ngày mai, mình sẽ…",
    description: "Có những điều bình thường hôm nay từng là ước mơ của nhiều thế hệ.",
    locale: "vi_VN", type: "website"
  }
};

export default function RootLayout({ children }: { children: ReactNode }) {
  const basePath = process.env.NEXT_PUBLIC_BASE_PATH || "";
  return (
    <html lang="vi">
      <body>
        <Script src={`${basePath}/assets/story-media.js?v=${markup.assetVersion}`} strategy="beforeInteractive" />
        {children}
        <Script src={`${basePath}/assets/site.js?v=${markup.assetVersion}`} strategy="afterInteractive" />
        <Script src={`${basePath}/assets/cinema.js?v=${markup.assetVersion}`} strategy="afterInteractive" />
      </body>
    </html>
  );
}
