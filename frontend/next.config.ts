import type { NextConfig } from 'next'

import path from 'path'

const nextConfig: NextConfig = {
  /* config options here */
  turbopack: {
    root: path.join(__dirname, '..'),
  },
  
  // Docker support
  output: 'standalone',
  
  // API rewrite for backend communication
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/:path*`,
      },
      {
        source: '/health',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/health`,
      },
      {
        source: '/docs',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/docs`,
      },
    ]
  },
}

export default nextConfig
