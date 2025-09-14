'use client'

import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { useEffect } from 'react'

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
import { useOnboarding } from '@/contexts/OnboardingContext'
import { Separator } from '../ui/separator'

const formSchema = z.object({
  companyRoles: z.string().min(1, {
    message: 'Please select a company roles.',
  }),
})

export function OnboardForm3() {
  const { formData, updateFormData, nextStep } = useOnboarding()

  // 1. Define your form with initial values from context
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      companyRoles: formData.companyRoles,
    },
  })

  // Update form when context data changes
  useEffect(() => {
    form.reset({
      companyRoles: formData.companyRoles,
    })
  }, [formData, form])

  // 2. Define a submit handler that saves to context
  function onSubmit(values: z.infer<typeof formSchema>) {
    // Save to context
    updateFormData({
      companyRoles: values.companyRoles,
    })

    // Move to next step
    nextStep()
  }

  // Auto-save form data to context when values change
  useEffect(() => {
    const subscription = form.watch((values) => {
      updateFormData({
        companyRoles: values.companyRoles || '',
      })
    })
    return () => subscription.unsubscribe()
  }, [form, updateFormData])

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
                <RadioGroup
                  value={field.value}
                  onValueChange={field.onChange}
                  className="grid grid-cols-3 gap-y-5 gap-x-5"
                >
                  {companyRoles.map((role) => (
                    <div
                      key={role.value}
                      onClick={(e) => {
                        e.preventDefault()
                        field.onChange(role.value)
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
                        }}
                      />
                    </div>
                  ))}
                </RadioGroup>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </form>
    </Form>
  )
}
