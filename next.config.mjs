/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  reactStrictMode: true,
  
  // Define async rewrites to proxy API requests to Flask backend
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:5000/:path*', // Proxy to Flask API
      },
    ]
  },
  
  // Configure output directory
  distDir: '.next',
  webpack(config) {
    return config
  },
}

export default nextConfig
