/**
 * Example component demonstrating comprehensive domain validation
 * This showcases the best practices implemented in the onboarding API integration
 */

'use client'

import React, { useState } from 'react'
import { toast } from 'sonner'
import { useDomainAvailability } from '@/data/hooks/useOnboarding'
import { domainValidation } from '@/data/api/onboarding'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { CheckCircle, XCircle, Loader2, AlertCircle } from 'lucide-react'

/**
 * Domain validation example component with real-time feedback
 * Demonstrates all the best practices implemented in the API integration
 */
export const DomainValidationExample: React.FC = () => {
  // State for domain input
  const [domain, setDomain] = useState('')
  
  // Real-time domain availability checking with debouncing
  const {
    availability,
    isChecking,
    error,
    isAvailable,
    fullDomain,
    checkNow
  } = useDomainAvailability(domain, 500) // 500ms debounce

  // Handle domain input change with immediate client-side validation
  const handleDomainChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setDomain(value)
    
    // Client-side validation feedback
    if (value.length >= 3) {
      const validation = domainValidation.validateFormat(value)
      if (!validation.isValid && validation.error) {
        // Show validation error as toast for immediate feedback
        toast.error('Domain Format Error', {
          description: validation.error,
          duration: 3000
        })
      }
    }
  }

  // Manual domain check trigger
  const handleCheckDomain = () => {
    if (!domain.trim()) {
      toast.error('Please enter a domain to check')
      return
    }
    
    checkNow()
  }

  // Get validation status for UI feedback
  const getValidationStatus = () => {
    if (!domain.trim()) return null
    
    // Client-side validation first
    const validation = domainValidation.validateFormat(domain)
    if (!validation.isValid) {
      return {
        type: 'error' as const,
        message: validation.error || 'Invalid format',
        icon: <XCircle className="h-4 w-4 text-red-500" />
      }
    }
    
    // API validation status
    if (isChecking) {
      return {
        type: 'loading' as const,
        message: 'Checking availability...',
        icon: <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
      }
    }
    
    if (error) {
      return {
        type: 'error' as const,
        message: error,
        icon: <AlertCircle className="h-4 w-4 text-yellow-500" />
      }
    }
    
    if (availability) {
      return {
        type: isAvailable ? 'success' : 'error',
        message: availability.message,
        icon: isAvailable 
          ? <CheckCircle className="h-4 w-4 text-green-500" />
          : <XCircle className="h-4 w-4 text-red-500" />
      }
    }
    
    return null
  }

  const status = getValidationStatus()

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        <CardTitle>Domain Validation Example</CardTitle>
        <CardDescription>
          Real-time domain validation with comprehensive error handling
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Domain Input with Real-time Validation */}
        <div className="space-y-2">
          <Label htmlFor="domain">Company Domain</Label>
          <div className="relative">
            <Input
              id="domain"
              type="text"
              placeholder="Enter your company domain"
              value={domain}
              onChange={handleDomainChange}
              className={`pr-10 ${
                status?.type === 'error' ? 'border-red-500' : 
                status?.type === 'success' ? 'border-green-500' : ''
              }`}
            />
            {/* Status Icon */}
            {status && (
              <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                {status.icon}
              </div>
            )}
          </div>
          
          {/* Validation Message */}
          {status && (
            <div className={`text-sm flex items-center gap-2 ${
              status.type === 'error' ? 'text-red-600' : 
              status.type === 'success' ? 'text-green-600' : 
              'text-blue-600'
            }`}>
              {status.icon}
              {status.message}
            </div>
          )}
        </div>

        {/* Full Domain Preview */}
        {fullDomain && (
          <div className="space-y-2">
            <Label>Full Domain</Label>
            <div className="p-3 bg-gray-50 rounded-md">
              <code className="text-sm font-mono">{fullDomain}</code>
            </div>
          </div>
        )}

        {/* Availability Status Badge */}
        {availability && (
          <div className="flex items-center gap-2">
            <Label>Status:</Label>
            <Badge variant={isAvailable ? 'default' : 'destructive'}>
              {isAvailable ? 'Available' : 'Not Available'}
            </Badge>
          </div>
        )}

        {/* Manual Check Button */}
        <Button 
          onClick={handleCheckDomain}
          disabled={isChecking || !domain.trim()}
          className="w-full"
        >
          {isChecking ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Checking...
            </>
          ) : (
            'Check Domain Availability'
          )}
        </Button>

        {/* Validation Rules */}
        <div className="text-xs text-gray-600 space-y-1">
          <p className="font-medium">Domain Requirements:</p>
          <ul className="list-disc list-inside space-y-1 ml-2">
            <li>3-50 characters long</li>
            <li>Only letters, numbers, and hyphens</li>
            <li>Cannot start or end with hyphen</li>
            <li>No consecutive hyphens</li>
            <li>Reserved domains not allowed</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  )
}

export default DomainValidationExample
