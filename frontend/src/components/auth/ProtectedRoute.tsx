'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useUser } from '@/data/hooks/useUser'
import { Loader2 } from 'lucide-react'

interface ProtectedRouteProps {
  children: React.ReactNode
  requiredRole?: 'admin' | 'user' | 'manager'
  requiredPermissions?: string[]
  fallback?: React.ReactNode
  redirectTo?: string
}

export function ProtectedRoute({
  children,
  requiredRole,
  requiredPermissions = [],
  fallback,
  redirectTo = '/signin',
}: ProtectedRouteProps) {
  const { user, isLoading, isAuthenticated } = useUser()
  const router = useRouter()
  const [isChecking, setIsChecking] = useState(true)

  useEffect(() => {
    if (!isLoading && !isChecking) {
      // Only run checks once when loading is complete
      if (!isAuthenticated) {
        console.log('User not authenticated, redirecting to login')
        // Store current path for redirect after login
        const currentPath = window.location.pathname
        const redirectUrl = `${redirectTo}?callbackUrl=${encodeURIComponent(currentPath)}`
        router.push(redirectUrl)
        return
      }

      // Check role requirements
      if (
        requiredRole &&
        user?.role !== requiredRole &&
        user?.role !== 'admin'
      ) {
        router.push('/dashboard') // Redirect to default authorized page
        return
      }

      // Check permission requirements
      if (requiredPermissions.length > 0) {
        const userPermissions = user?.permissions || []
        const hasAllPermissions = requiredPermissions.every(
          (permission) =>
            userPermissions.includes(permission) || user?.role === 'admin',
        )

        if (!hasAllPermissions) {
          router.push('/dashboard') // Redirect to default authorized page
          return
        }
      }
    }

    if (!isLoading) {
      setIsChecking(false)
    }
  }, [isLoading, isAuthenticated, isChecking])

  // Show loading state
  if (isLoading || isChecking) {
    return (
      fallback || (
        <div className="min-h-screen flex items-center justify-center">
          <div className="flex flex-col items-center space-y-4">
            <Loader2 className="h-8 w-8 animate-spin text-custom-base-green" />
            <p className="text-gray-600">Verifying access...</p>
          </div>
        </div>
      )
    )
  }

  // Show nothing while redirecting
  if (!isAuthenticated) {
    return null
  }

  // Check role access
  if (requiredRole && user?.role !== requiredRole && user?.role !== 'admin') {
    return null
  }

  // Check permission access
  if (requiredPermissions.length > 0) {
    const userPermissions = user?.permissions || []
    const hasAllPermissions = requiredPermissions.every(
      (permission) =>
        userPermissions.includes(permission) || user?.role === 'admin',
    )

    if (!hasAllPermissions) {
      return null
    }
  }

  // Render protected content
  return <>{children}</>
}

// Higher-order component version
export function withProtectedRoute<P extends object>(
  Component: React.ComponentType<P>,
  options?: Omit<ProtectedRouteProps, 'children'>,
) {
  return function ProtectedComponent(props: P) {
    return (
      <ProtectedRoute {...options}>
        <Component {...props} />
      </ProtectedRoute>
    )
  }
}

// Hook for checking permissions in components
export function usePermissions() {
  const { user } = useUser()

  const hasRole = (role: 'admin' | 'user' | 'manager') => {
    return user?.role === role || user?.role === 'admin'
  }

  const hasPermission = (permission: string) => {
    return user?.permissions?.includes(permission) || user?.role === 'admin'
  }

  const hasAnyPermission = (permissions: string[]) => {
    return permissions.some((permission) => hasPermission(permission))
  }

  const hasAllPermissions = (permissions: string[]) => {
    return permissions.every((permission) => hasPermission(permission))
  }

  return {
    user,
    hasRole,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    isAdmin: user?.role === 'admin',
    isManager: user?.role === 'manager',
    isUser: user?.role === 'user',
  }
}
