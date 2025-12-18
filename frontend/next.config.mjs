/** @type {import('next').NextConfig} */
const nextConfig = {
  webpack(config) {
    // Exclude svg from Next's default loader
    const fileLoaderRule = config.module.rules.find(
      (rule) => rule.test?.test?.(".svg")
    )

    if (fileLoaderRule) {
      fileLoaderRule.exclude = /\.svg$/i
    }

    // Add SVGR loader
    config.module.rules.push({
      test: /\.svg$/i,
      issuer: /\.[jt]sx?$/,
      resourceQuery: /component/, // <-- IMPORTANT
      use: ["@svgr/webpack"],
    })

    return config
  },
}

export default nextConfig
