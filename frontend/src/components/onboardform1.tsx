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
import { Input } from '@/components/ui/input'
import { AlertCircleIcon } from 'lucide-react'
import { RadioGroup, RadioGroupItem } from './ui/radio-group'
import { Label } from './ui/label'
import { useOnboarding } from '@/contexts/OnboardingContext'
import { DomainInput } from '@/components/ui/domain-input'

const formSchema = z.object({
  companyName: z.string().min(2, {
    message: 'Company name must be at least 2 characters.',
  }),
  companyDomain: z.string().min(2, {
    message: 'Company domain must be at least 2 characters.',
  }),
  companySize: z.string().min(1, {
    message: 'Please select a company size.',
  }),
})

export function OnboardForm1() {
  const { formData, updateFormData, nextStep, canGoNext } = useOnboarding()

  // 1. Define your form with initial values from context
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      companyName: formData.companyName,
      companyDomain: formData.companyDomain,
      companySize: formData.companySize,
    },
  })

  // Update form when context data changes
  useEffect(() => {
    form.reset({
      companyName: formData.companyName,
      companyDomain: formData.companyDomain,
      companySize: formData.companySize,
    })
  }, [formData, form])

  // 2. Define a submit handler that saves to context
  function onSubmit(values: z.infer<typeof formSchema>) {
    // Save to context
    updateFormData({
      companyName: values.companyName,
      companyDomain: values.companyDomain,
      companySize: values.companySize,
    })

    // Move to next step
    nextStep()
  }

  // Auto-save form data to context when values change
  useEffect(() => {
    const subscription = form.watch((values) => {
      if (values.companyName || values.companyDomain || values.companySize) {
        updateFormData({
          companyName: values.companyName || '',
          companyDomain: values.companyDomain || '',
          companySize: values.companySize || '',
        })
      }
    })
    return () => subscription.unsubscribe()
  }, [form, updateFormData])

  const companySizes = [
    { value: '1-10', label: '1-10' },
    { value: '11-50', label: '11-50' },
    { value: '51-100', label: '51-100' },
    { value: '101-200', label: '101-200' },
    { value: '201-500', label: '201-500' },
    { value: '500+', label: '500+' },
  ]

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="space-y-8 bg-white rounded-[10px] p-10 h-[80vh]"
      >
        {/* Form title Type the name of your company     */}
        <h1 className="text-xl font-medium">Type the name of your company</h1>
        <FormField
          control={form.control}
          name="companyName"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Company Name</FormLabel>
              <FormControl>
                <Input
                  placeholder="Unpixel"
                  {...field}
                  className="h-11 rounded-[10px] focus-visible:ring-0 focus-visible:border-custom-base-green"
                />
              </FormControl>

              <FormMessage />
            </FormItem>
          )}
        />
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
        <div className="flex flex-row gap-2">
          <AlertCircleIcon className="w-5 h-5 text-[#687588]" />
          <p className="text-sm text-[#687588]">
            We will create a unique company URL for you to log into Humanline
          </p>
        </div>

        <h1 className="text-xl font-medium">
          What is the size of your company
        </h1>
        <FormField
          control={form.control}
          name="companySize"
          render={({ field }) => (
            <FormItem>
              <FormControl>
                <RadioGroup
                  value={field.value}
                  onValueChange={field.onChange}
                  className="grid grid-cols-4 gap-y-5 gap-x-5"
                >
                  {companySizes.map((size) => (
                    <div
                      key={size.value}
                      onClick={(e) => {
                        e.preventDefault()
                        field.onChange(size.value)
                      }}
                      className={`flex justify-between gap-8 p-3 py-3 border rounded-[10px] cursor-pointer transition-all ${
                        field.value === size.value
                          ? 'border-custom-base-green bg-custom-base-green/5'
                          : 'border-gray-300 hover:border-custom-base-green/50'
                      }`}
                    >
                      <Label
                        htmlFor={`r-${size.value}`}
                        className="cursor-pointer"
                        onClick={(e) => {
                          e.preventDefault()
                          field.onChange(size.value)
                        }}
                      >
                        {size.label}
                      </Label>
                      <RadioGroupItem
                        value={size.value}
                        id={`r-${size.value}`}
                        className={
                          field.value === size.value
                            ? 'border-custom-base-green'
                            : ''
                        }
                        onClick={(e) => {
                          e.preventDefault()
                          field.onChange(size.value)
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
