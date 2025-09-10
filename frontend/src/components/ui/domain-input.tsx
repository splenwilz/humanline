"use client"

import React from 'react'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { CheckCircle, XCircle, Loader2 } from 'lucide-react'
import { useDomainValidation } from '@/hooks/useDomainValidation'
import { cn } from '@/lib/utils'

interface DomainInputProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  className?: string
  disabled?: boolean
}

export const DomainInput: React.FC<DomainInputProps> = ({
  value,
  onChange,
  placeholder = "Enter your company domain",
  className,
  disabled = false
}) => {
  const { isValid, isChecking, message } = useDomainValidation(value)

  const getStatusIcon = () => {
    if (isChecking) {
      return <Loader2 className="h-4 w-4 animate-spin text-gray-400" />
    }
    
    if (value.length >= 3) {
      return isValid 
        ? <CheckCircle className="h-4 w-4 text-green-500" />
        : <XCircle className="h-4 w-4 text-red-500" />
    }
    
    return null
  }

  const getInputStyles = () => {           
    return cn(
      "pr-10 h-11 rounded-[10px] focus-visible:ring-0 focus-visible:border-custom-base-green",
      isValid ? " focus:border-green-500" : "border-red-500 focus:border-red-500"
    )
  }

  return (
    <div className="space-y-2">
      <Label htmlFor="domain">Company Domain</Label>
      <div className="relative">
        <Input
          id="domain"
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          disabled={disabled}
          className={cn(getInputStyles(), className)}
        />
        <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
          {getStatusIcon()}
        </div>
      </div>
      
      {message && (
        <p className={cn(
          "text-sm",
          isValid ? "text-green-600" : "text-red-600"
        )}>
          {message}
        </p>
      )}
    </div>
  )
}
