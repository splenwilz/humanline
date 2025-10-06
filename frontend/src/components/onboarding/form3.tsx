'use client'

import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { useEffect, useState } from 'react'

import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { RadioGroup, RadioGroupItem } from '../ui/radio-group'
import { Label } from '../ui/label'
import { Input } from '@/components/ui/input'
import { useOnboarding } from '@/contexts/OnboardingContext'
import { Separator } from '../ui/separator'

const formSchema = z.object({
  companyRoles: z.string().min(1, {
    message: 'Please select a company roles.',
  }),
  customRole: z.string().optional(),
}).refine(
  (values) => {
    if (values.companyRoles === 'other' && !values.customRole?.trim()) {
      return false
    }
    return true
  },
  {
    message: 'Please specify your role.',
    path: ['customRole'],
  }
)

export function OnboardForm3() {
  const { formData, updateFormData, nextStep } = useOnboarding()

  // State to track if "other" is selected for role
  const [isCustomRole, setIsCustomRole] = useState(
    formData.companyRoles &&
      ![
        'ceo-founder-owner ',
        'hr-manager',
        'hr-staff',
        'it-tech-manager',
        'it-tech-staff',
      ].includes(formData.companyRoles),
  )

  // 1. Define your form with initial values from context
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      companyRoles: isCustomRole ? 'other' : formData.companyRoles,
      customRole: isCustomRole && formData.companyRoles !== 'other' 
        ? formData.companyRoles 
        : '',
    },
  })

  // Update form when context data changes
  useEffect(() => {
    const isCustom =
      formData.companyRoles &&
      ![
        'ceo-founder-owner ',
        'hr-manager',
        'hr-staff',
        'it-tech-manager',
        'it-tech-staff',
      ].includes(formData.companyRoles)

    setIsCustomRole(isCustom)

    const nextValues = {
      companyRoles: isCustom ? 'other' : formData.companyRoles,
      customRole: isCustom && formData.companyRoles !== 'other' 
        ? formData.companyRoles 
        : '',
    }

    // Only reset if values actually changed to prevent feedback loop
    const currentValues = form.getValues()
    const hasChanged = Object.keys(nextValues).some(
      (key) =>
        currentValues[key as keyof typeof currentValues] !==
        nextValues[key as keyof typeof nextValues],
    )

    if (hasChanged) {
      form.reset(nextValues)
    }
  }, [formData, form])

  // 2. Define a submit handler that saves to context
  function onSubmit(values: z.infer<typeof formSchema>) {
    // Determine the final role value
    const finalRole =
      values.companyRoles === 'other'
        ? values.customRole || 'other'
        : values.companyRoles

    // Save to context
    updateFormData({
      companyRoles: finalRole,
    })

    // Move to next step
    nextStep()
  }

  // Auto-save form data to context when values change
  useEffect(() => {
    const subscription = form.watch((values) => {
      // Determine the final role value for auto-save
      const finalRole =
        values.companyRoles === 'other'
          ? values.customRole || 'other'
          : values.companyRoles

      updateFormData({
        companyRoles: finalRole || '',
      })
    })
    return () => subscription.unsubscribe()
  }, [form, updateFormData])

  // Expose form validation to parent components
  useEffect(() => {
    // Store form validation function globally so context can access it
    const globalWindow = window as typeof window & {
      validateForm3?: () => Promise<boolean>
    }
    globalWindow.validateForm3 = () => {
      return form.trigger() // This triggers Zod validation
    }
    
    return () => {
      delete globalWindow.validateForm3
    }
  }, [form])

  const companyRoles = [
    { value: 'ceo-founder-owner ', label: 'CEO/Founder/Owner' },
    { value: 'hr-manager', label: 'HR Manager' },
    { value: 'hr-staff', label: 'HR Staff' },
    { value: 'it-tech-manager', label: 'IT Tech Manager' },
    { value: 'it-tech-staff', label: 'IT Tech Staff' },
    { value: 'other', label: 'Other' },
  ]

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="space-y-8 bg-white rounded-[10px] p-10 h-[80vh]"
      >
        <FormLabel className="text-muted-foreground font-light">
          Your company domain
        </FormLabel>
        <h1 className="text-xl font-medium">
          {formData.companyDomain}
          {'.hrline.com'}
        </h1>
        <Separator />

        <h1 className="text-xl font-medium">Choose role</h1>
        <FormField
          control={form.control}
          name="companyRoles"
          render={({ field }) => (
            <FormItem>
              <FormControl>
                <div className="space-y-4">
                  <RadioGroup
                    value={field.value}
                    onValueChange={(value) => {
                      field.onChange(value)
                      setIsCustomRole(value === 'other')
                      if (value !== 'other') {
                        form.setValue('customRole', '')
                      }
                    }}
                    className="grid grid-cols-3 gap-y-5 gap-x-5"
                  >
                    {companyRoles.map((role) => (
                      <div
                        key={role.value}
                        onClick={(e) => {
                          e.preventDefault()
                          field.onChange(role.value)
                          setIsCustomRole(role.value === 'other')
                          if (role.value !== 'other') {
                            form.setValue('customRole', '')
                          }
                        }}
                        className={`flex justify-between gap-8 p-3 py-3 border rounded-[10px] cursor-pointer transition-all ${
                          field.value === role.value
                            ? 'border-custom-base-green bg-custom-base-green/5'
                            : 'border-gray-300 hover:border-custom-base-green/50'
                        }`}
                      >
                        <Label
                          htmlFor={`r-${role.value}`}
                          className="cursor-pointer"
                          onClick={(e) => {
                            e.preventDefault()
                            field.onChange(role.value)
                            setIsCustomRole(role.value === 'other')
                            if (role.value !== 'other') {
                              form.setValue('customRole', '')
                            }
                          }}
                        >
                          {role.label}
                        </Label>
                        <RadioGroupItem
                          value={role.value}
                          id={`r-${role.value}`}
                          className={
                            field.value === role.value
                              ? 'border-custom-base-green'
                              : ''
                          }
                          onClick={(e) => {
                            e.preventDefault()
                            field.onChange(role.value)
                            setIsCustomRole(role.value === 'other')
                            if (role.value !== 'other') {
                              form.setValue('customRole', '')
                            }
                          }}
                        />
                      </div>
                    ))}
                  </RadioGroup>

                  {/* Custom role input field */}
                  {isCustomRole && (
                    <FormField
                      control={form.control}
                      name="customRole"
                      render={({ field: customField }) => (
                        <FormItem>
                          <FormControl>
                            <Input
                              {...customField}
                              placeholder="Please specify your role"
                              className="h-11 rounded-[10px] focus-visible:ring-0 focus-visible:border-custom-base-green"
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  )}
                </div>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </form>
    </Form>
  )
}
