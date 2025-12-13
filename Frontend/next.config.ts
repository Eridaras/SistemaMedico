import type {NextConfig} from 'next';

const nextConfig: NextConfig = {
  /* config options here */
  typescript: {
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'placehold.co',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'images.unsplash.com',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'picsum.photos',
        port: '',
        pathname: '/**',
      },
    ],
  },
  async rewrites() {
    return [
      {
        source: '/api/auth/:path*',
        destination: 'http://localhost:5001/api/auth/:path*',
      },
      {
        source: '/api/inventario/:path*',
        destination: 'http://localhost:5002/api/inventario/:path*',
      },
      {
        source: '/api/historia-clinica/:path*',
        destination: 'http://localhost:5003/api/historia-clinica/:path*',
      },
      {
        source: '/api/facturacion/:path*',
        destination: 'http://localhost:5004/api/facturacion/:path*',
      },
      {
        source: '/api/citas/:path*',
        destination: 'http://localhost:5005/api/citas/:path*',
      },
      {
        source: '/api/logs/:path*',
        destination: 'http://localhost:5006/api/logs/:path*',
      },
    ];
  },
};

export default nextConfig;
