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
  yourNeeds: z.string().min(1, {
    message: 'Please select a your needs.',
  }),
  customNeeds: z.string().optional(),
}).refine(
  (values) => {
    if (values.yourNeeds === 'other' && !values.customNeeds?.trim()) {
      return false
    }
    return true
  },
  {
    message: 'Please describe your specific needs.',
    path: ['customNeeds'],
  }
)

export function OnboardForm4() {
  const { formData, updateFormData } = useOnboarding()

  // State to track if "other" is selected for needs
  const [isCustomNeeds, setIsCustomNeeds] = useState(
    formData.yourNeeds &&
      ![
        'onboarding-new-employees ',
        'online-time-tracking',
        'performance-management',
        'employee-engagement',
        'Recruitment',
      ].includes(formData.yourNeeds),
  )

  // 1. Define your form with initial values from context
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      yourNeeds: isCustomNeeds ? 'other' : formData.yourNeeds,
      customNeeds: isCustomNeeds && formData.yourNeeds !== 'other' 
        ? formData.yourNeeds 
        : '',
    },
  })

  // Update form when context data changes
  useEffect(() => {
    const isCustom =
      formData.yourNeeds &&
      ![
        'onboarding-new-employees ',
        'online-time-tracking',
        'performance-management',
        'employee-engagement',
        'Recruitment',
      ].includes(formData.yourNeeds)

    setIsCustomNeeds(isCustom)

    const nextValues = {
      yourNeeds: isCustom ? 'other' : formData.yourNeeds,
      customNeeds: isCustom && formData.yourNeeds !== 'other' 
        ? formData.yourNeeds 
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
    // Determine the final needs value
    const finalNeeds =
      values.yourNeeds === 'other'
        ? values.customNeeds || 'other'
        : values.yourNeeds

    // Save to context
    updateFormData({
      yourNeeds: finalNeeds,
    })
  }

  // Auto-save form data to context when values change
  useEffect(() => {
    const subscription = form.watch((values) => {
      // Determine the final needs value for auto-save
      const finalNeeds =
        values.yourNeeds === 'other'
          ? values.customNeeds || 'other'
          : values.yourNeeds

      updateFormData({
        yourNeeds: finalNeeds || '',
      })
    })
    return () => subscription.unsubscribe()
  }, [form, updateFormData])

  // Expose form validation to parent components
  useEffect(() => {
    // Store form validation function globally so context can access it
    const globalWindow = window as typeof window & {
      validateForm4?: () => Promise<boolean>
    }
    globalWindow.validateForm4 = () => {
      return form.trigger() // This triggers Zod validation
    }
    
    return () => {
      delete globalWindow.validateForm4
    }
  }, [form])

  const yourNeeds = [
    {
      value: 'onboarding-new-employees ',
      label: 'Onboarding new employees',
      description:
        'I want to onboard a lot of new employees in a consistent and systematic way.',
    },
    {
      value: 'online-time-tracking',
      label: 'Online time tracking',
      description:
        'I want to track and approve time attendance and time off online, from anywhere.',
    },
    {
      value: 'performance-management',
      label: 'Performance management',
      description:
        'I want to manage and maintain employee performance in a continuous and objective way.',
    },
    {
      value: 'employee-engagement',
      label: 'Employee engagement',
      description:
        'I want to keep my employees happy, engaged, active, and motivated.',
    },
    {
      value: 'Recruitment',
      label: 'Recruitment',
      description:
        'I want to hire the best talents to improve business performance and employer branging.',
    },
    {
      value: 'other',
      label: 'Other',
      description: 'I have specific needs that are not listed above.',
    },
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

        <h1 className="text-xl font-medium">Choose according to your needs</h1>
        <FormField
          control={form.control}
          name="yourNeeds"
          render={({ field }) => (
            <FormItem>
              <FormControl>
                <div className="space-y-4">
                  <RadioGroup
                    value={field.value}
                    onValueChange={(value) => {
                      field.onChange(value)
                      setIsCustomNeeds(value === 'other')
                      if (value !== 'other') {
                        form.setValue('customNeeds', '')
                      }
                    }}
                    className="grid gap-y-5 gap-x-5"
                  >
                    {yourNeeds.map((need) => (
                      <div
                        key={need.value}
                        onClick={(e) => {
                          e.preventDefault()
                          field.onChange(need.value)
                          setIsCustomNeeds(need.value === 'other')
                          if (need.value !== 'other') {
                            form.setValue('customNeeds', '')
                          }
                        }}
                        className={`flex justify-between gap-8 p-3 py-3 border rounded-[10px] cursor-pointer transition-all ${
                          field.value === need.value
                            ? 'border-custom-base-green bg-custom-base-green/5'
                            : 'border-gray-300 hover:border-custom-base-green/50'
                        }`}
                      >
                        <div className="flex flex-col gap-2">
                          <Label
                            htmlFor={`r-${need.value}`}
                            className="cursor-pointer"
                            onClick={(e) => {
                              e.preventDefault()
                              field.onChange(need.value)
                              setIsCustomNeeds(need.value === 'other')
                              if (need.value !== 'other') {
                                form.setValue('customNeeds', '')
                              }
                            }}
                          >
                            {need.label}
                          </Label>
                          <p className="text-[13px] text-muted-foreground">
                            {need.description}
                          </p>
                        </div>
                        <RadioGroupItem
                          value={need.value}
                          id={`r-${need.value}`}
                          className={
                            field.value === need.value
                              ? 'border-custom-base-green'
                              : ''
                          }
                          onClick={(e) => {
                            e.preventDefault()
                            field.onChange(need.value)
                            setIsCustomNeeds(need.value === 'other')
                            if (need.value !== 'other') {
                              form.setValue('customNeeds', '')
                            }
                          }}
                        />
                      </div>
                    ))}
                  </RadioGroup>

                  {/* Custom needs input field */}
                  {isCustomNeeds && (
                    <FormField
                      control={form.control}
                      name="customNeeds"
                      render={({ field: customField }) => (
                        <FormItem>
                          <FormControl>
                            <Input
                              {...customField}
                              placeholder="Please describe your specific needs"
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
