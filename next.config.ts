import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Release 1 is a CDN-deployable experience: no server actions or runtime API.
  output: "export",
  basePath: process.env.NEXT_PUBLIC_BASE_PATH || "",
  trailingSlash: true,
  images: { unoptimized: true },
};
export default nextConfig;
