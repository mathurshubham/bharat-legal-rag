import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  // Silence the Turbopack/webpack warning — no custom webpack needed
  turbopack: {},
};

export default nextConfig;
