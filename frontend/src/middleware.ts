import { NextRequest, NextResponse } from 'next/server'
import { jwtVerify } from 'jose'

// Define route patterns
const publicRoutes = [
  '/',
  '/signin',
  '/signup', 
  '/confirm',
  '/api/health',
  '/forgot-password',
  '/reset-password'
]

const authRoutes = [
  '/signin',
  '/signup',
  '/confirm'
]

const protectedRoutes = [
  '/dashboard',
  '/onboarding',
  '/employees',
  '/profile',
  '/settings',
  '/admin'
]

// JWT secret for token verification
const JWT_SECRET = new TextEncoder().encode(
  process.env.JWT_SECRET || 'your-super-secret-jwt-key-at-least-32-characters-long-change-this-in-production'
)

/**
 * Verify JWT token with proper signature verification
 */
async function verifyToken(token: string): Promise<any> {
  try {
    const { payload } = await jwtVerify(token, JWT_SECRET)
    return payload
  } catch (error) {
    console.error('Token verification failed:', error)
    return null
  }
}

/**
 * Check if route matches any pattern in the array
 */
function matchesRoute(pathname: string, routes: string[]): boolean {
  return routes.some(route => {
    // Exact match
    if (route === pathname) return true
    
    // Wildcard match (e.g., /dashboard matches /dashboard/*)
    if (route.endsWith('*')) {
      const baseRoute = route.slice(0, -1)
      return pathname.startsWith(baseRoute)
    }
    
    // Prefix match for nested routes
    return pathname.startsWith(route + '/')
  })
}

/**
 * Get user authentication status from request
 */
async function getAuthStatus(request: NextRequest) {
  const token = request.cookies.get('access_token')?.value
  
  if (!token) {
    return { isAuthenticated: false, user: null }
  }

  const payload = await verifyToken(token)
  
  if (!payload) {
    return { isAuthenticated: false, user: null }
  }

  return {
    isAuthenticated: true,
    user: {
      id: payload.sub,
      email: payload.email,
      role: payload.role || 'user',
      isEmailVerified: Boolean(payload.email_verified || payload.is_verified)
    }
  }
}

/**
 * Main middleware function
 */
export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  
  // Skip middleware for static files and API routes (except protected ones)
  if (
    pathname.startsWith('/_next/') ||
    pathname.startsWith('/api/') ||
    pathname.includes('.') // Static files
  ) {
    return NextResponse.next()
  }

  const { isAuthenticated, user } = await getAuthStatus(request)
  
  // Handle public routes
  if (matchesRoute(pathname, publicRoutes)) {
    return NextResponse.next()
  }

  // Redirect authenticated users away from auth pages
  if (isAuthenticated && matchesRoute(pathname, authRoutes)) {
    const redirectUrl = new URL('/dashboard', request.url)
    return NextResponse.redirect(redirectUrl)
  }

  // Handle protected routes
  if (matchesRoute(pathname, protectedRoutes)) {
    if (!isAuthenticated) {
      // Store the attempted URL for redirect after login
      const loginUrl = new URL('/signin', request.url)
      loginUrl.searchParams.set('callbackUrl', pathname)
      return NextResponse.redirect(loginUrl)
    }

    // Check email verification for certain routes
    if (!user?.isEmailVerified && pathname !== '/confirm') {
      const confirmUrl = new URL('/confirm', request.url)
      return NextResponse.redirect(confirmUrl)
    }

    // Role-based access control
    if (pathname.startsWith('/admin') && user?.role !== 'admin') {
      const unauthorizedUrl = new URL('/dashboard', request.url)
      return NextResponse.redirect(unauthorizedUrl)
    }

    // Add user info to headers for server components
    const response = NextResponse.next()
    response.headers.set('x-user-id', user?.id || '')
    response.headers.set('x-user-email', user?.email || '')
    response.headers.set('x-user-role', user?.role || '')
    
    return response
  }

  // Default: allow the request
  return NextResponse.next()
}

/**
 * Middleware configuration
 */
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
}
