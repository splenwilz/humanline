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
import { RadioGroup, RadioGroupItem } from './ui/radio-group'
import { Label } from './ui/label'
import { useOnboarding } from '@/contexts/OnboardingContext'
import { Separator } from './ui/separator'
import { DomainInput } from '@/components/ui/domain-input'

const formSchema = z.object({
  companyDomain: z.string().min(2, {
    message: 'Company domain must be at least 2 characters.',
  }),
  companyIndustry: z.string().min(1, {
    message: 'Please select a company industry.',
  }),
})

export function OnboardForm2() {
  const { formData, updateFormData, nextStep } = useOnboarding()

  // 1. Define your form with initial values from context
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      companyDomain: formData.companyDomain,
      companyIndustry: formData.companyIndustry,
    },
  })

  // Update form when context data changes
  useEffect(() => {
    form.reset({
      companyDomain: formData.companyDomain,
      companyIndustry: formData.companyIndustry,
    })
  }, [formData, form])

  // 2. Define a submit handler that saves to context
  function onSubmit(values: z.infer<typeof formSchema>) {
    // Save to context
    updateFormData({
      companyDomain: values.companyDomain,
      companyIndustry: values.companyIndustry,
    })

    // Move to next step
    nextStep()
  }

  // Auto-save form data to context when values change
  useEffect(() => {
    const subscription = form.watch((values) => {
      updateFormData({
        companyDomain: values.companyDomain || '',
        companyIndustry: values.companyIndustry || '',
      })
    })
    return () => subscription.unsubscribe()
  }, [form, updateFormData])

  const companyIndustries = [
    { value: 'crypto', label: 'Crypto' },
    { value: 'ecommerce', label: 'Ecommerce' },
    { value: 'fintech', label: 'Fintech' },
    { value: 'health-tech', label: 'Health Tech' },
    { value: 'software-outsourcing', label: 'Software Outsourcing' },
    { value: 'other', label: 'Other' },
  ]

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="space-y-8 bg-white rounded-[10px] p-10 h-[80vh]"
      >
        <FormField
          control={form.control}
          name="companyDomain"
          render={({ field }) => (
            <FormItem>
              <FormControl>
                <div className="flex flex-row gap-3">
                  <div className="flex-1">
                    <DomainInput
                      value={field.value}
                      onChange={field.onChange}
                      placeholder="unpixel"
                    />
                  </div>
                  <div className="bg-[#F1F2F4] mt-5 pt-3 rounded-[10px] w-[150px] text-center h-11 text-[#687588] cursor-pointer">
                    hrline.com
                  </div>
                </div>
              </FormControl>

              <FormMessage />
            </FormItem>
          )}
        />
        <Separator />

        <h1 className="text-xl font-medium">What is your industry</h1>
        <FormField
          control={form.control}
          name="companyIndustry"
          render={({ field }) => (
            <FormItem>
              <FormControl>
                <RadioGroup
                  value={field.value}
                  onValueChange={field.onChange}
                  className="grid grid-cols-3 gap-y-5 gap-x-5"
                >
                  {companyIndustries.map((industry) => (
                    <div
                      key={industry.value}
                      onClick={(e) => {
                        e.preventDefault()
                        field.onChange(industry.value)
                      }}
                      className={`flex justify-between gap-8 p-3 py-3 border rounded-[10px] cursor-pointer transition-all ${
                        field.value === industry.value
                          ? 'border-custom-base-green bg-custom-base-green/5'
                          : 'border-gray-300 hover:border-custom-base-green/50'
                      }`}
                    >
                      <Label
                        htmlFor={`r-${industry.value}`}
                        className="cursor-pointer"
                        onClick={(e) => {
                          e.preventDefault()
                          field.onChange(industry.value)
                        }}
                      >
                        {industry.label}
                      </Label>
                      <RadioGroupItem
                        value={industry.value}
                        id={`r-${industry.value}`}
                        className={
                          field.value === industry.value
                            ? 'border-custom-base-green'
                            : ''
                        }
                        onClick={(e) => {
                          e.preventDefault()
                          field.onChange(industry.value)
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
