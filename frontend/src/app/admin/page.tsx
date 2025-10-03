'use client'

import { ProtectedRoute, usePermissions } from '@/components/auth/ProtectedRoute'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Shield, Users, Settings, BarChart3 } from 'lucide-react'

function AdminDashboard() {
  const { user, hasPermission, isAdmin } = usePermissions()

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Admin Dashboard</h1>
          <p className="text-gray-600">Administrative controls and system management</p>
        </div>
        <Badge variant="destructive" className="flex items-center gap-2">
          <Shield className="h-4 w-4" />
          Admin Only
        </Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              User Management
            </CardTitle>
            <CardDescription>
              Manage user accounts, roles, and permissions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button 
              className="w-full" 
              disabled={!hasPermission('users.write')}
            >
              Manage Users
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              System Settings
            </CardTitle>
            <CardDescription>
              Configure application settings and preferences
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button 
              className="w-full" 
              disabled={!hasPermission('settings.write')}
            >
              System Settings
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Analytics
            </CardTitle>
            <CardDescription>
              View system analytics and reports
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button 
              className="w-full" 
              disabled={!hasPermission('reports.read')}
            >
              View Analytics
            </Button>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Current User Info</CardTitle>
          <CardDescription>Your current authentication status</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <p><strong>Email:</strong> {user?.email}</p>
            <p><strong>Role:</strong> <Badge>{user?.role}</Badge></p>
            <p><strong>Is Admin:</strong> {isAdmin ? '✅ Yes' : '❌ No'}</p>
            <p><strong>Permissions:</strong></p>
            <div className="flex flex-wrap gap-2 mt-2">
              {user?.permissions?.map(permission => (
                <Badge key={permission} variant="outline">
                  {permission}
                </Badge>
              )) || <span className="text-gray-500">No specific permissions</span>}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default function AdminPage() {
  return (
    <ProtectedRoute requiredRole="admin">
      <AdminDashboard />
    </ProtectedRoute>
  )
}
