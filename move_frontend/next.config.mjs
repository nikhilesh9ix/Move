/** @type {import('next').NextConfig} */
const backendOrigin = (
  process.env.NEXT_PUBLIC_BACKEND_HTTP_URL ||
  process.env.BACKEND_HTTP_URL ||
  'http://localhost:8000'
).replace(/\/$/, '')

const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/move-api/:path*',
        destination: `${backendOrigin}/:path*`,
      },
    ]
  },
}

export default nextConfig
