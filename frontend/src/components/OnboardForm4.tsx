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
import { RadioGroup, RadioGroupItem } from './ui/radio-group'
import { Label } from './ui/label'
import { useOnboarding } from '@/contexts/OnboardingContext'
import { Separator } from './ui/separator'

const formSchema = z.object({
  yourNeeds: z.string().min(1, {
    message: 'Please select a your needs.',
  }),
})

export function OnboardForm4() {
  const { formData, updateFormData, nextStep, canGoNext } = useOnboarding()

  // 1. Define your form with initial values from context
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      yourNeeds: formData.yourNeeds,
    },
  })

  // Update form when context data changes
  useEffect(() => {
    form.reset({
      yourNeeds: formData.yourNeeds,
    })
  }, [formData, form])

  // 2. Define a submit handler that saves to context
  function onSubmit(values: z.infer<typeof formSchema>) {
    // Save to context
    updateFormData({
      yourNeeds: values.yourNeeds,
    })
  }

  // Auto-save form data to context when values change
  useEffect(() => {
    const subscription = form.watch((values) => {
      updateFormData({
        yourNeeds: values.yourNeeds || '',
      })
    })
    return () => subscription.unsubscribe()
  }, [form, updateFormData])

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
                <RadioGroup
                  value={field.value}
                  onValueChange={field.onChange}
                  className="grid gap-y-5 gap-x-5"
                >
                  {yourNeeds.map((need) => (
                    <div
                      key={need.value}
                      onClick={(e) => {
                        e.preventDefault()
                        field.onChange(need.value)
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
