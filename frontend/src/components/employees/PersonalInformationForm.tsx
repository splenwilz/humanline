'use client'

import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { Button } from '@/components/ui/button'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Label } from '../ui/label'
import { Edit2Icon, EditIcon } from 'lucide-react'
import Image from 'next/image'

const formSchema = z.object({
  fullName: z.string().min(2, {
    message: 'Full Name must be at least 2 characters.',
  }),
  gender: z.string().min(2, {
    message: 'Gender must be at least 2 characters.',
  }),
  dateOfBirth: z.string().min(1, {
    message: 'Date of birth is required.',
  }),
  email: z.email({
    message: 'Invalid email address.',
  }),
  phone: z.string().min(10, {
    message: 'Phone number must be at least 10 characters.',
  }),
  nationality: z.string().min(1, {
    message: 'Nationality is required.',
  }),
  healthCareProvider: z.string().min(1, {
    message: 'Health care provider is required.',
  }),
  maritalStatus: z.string().min(1, {
    message: 'Marital status is required.',
  }),
  PersonalTaxId: z.string().min(1, {
    message: 'Personal tax number is required.',
  }),
  SocialInsurance: z.string().min(1, {
    message: 'Social insurance number is required.',
  }),
  primaryAddress: z.string().min(1, {
    message: 'Primary address is required.',
  }),
  country: z.string().min(1, {
    message: 'Country is required.',
  }),
  city: z.string().min(1, {
    message: 'City is required.',
  }),
  state: z.string().min(1, {
    message: 'State is required.',
  }),
  postalCode: z.string().min(1, {
    message: 'Postal code is required.',
  }),
})

export function PersonalInformationForm() {
  // 1. Define your form.
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      fullName: '',
      gender: '',
      email: '',
      phone: '',
      nationality: '',
      healthCareProvider: '',
      maritalStatus: '',
      PersonalTaxId: '',
      SocialInsurance: '',
    },
  })

  // 2. Define a submit handler.
  function onSubmit(values: z.infer<typeof formSchema>) {
    // Do something with the form values.
    // ✅ This will be type-safe and validated.
    console.log(values)
  }
  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="">
        <div className="flex flex-col gap-3 space-y-4 mt-6 p-6 border border-custom-grey-200 rounded-3xl">
          <div className="flex justify-between items-center">
            <Label className="text-custom-grey-900 font-bold text-[18px]">
              Personal Information
            </Label>
            <Image src="/icons/edit.svg" alt="edit" width={18} height={18} />
          </div>
          <FormField
            control={form.control}
            name="fullName"
            render={({ field }) => (
              <FormItem>
                {/* Required */}
                <FormLabel>
                  Full Name <span className="text-red-500">*</span>
                </FormLabel>
                <FormControl>
                  <Input
                    placeholder="John"
                    {...field}
                    className="h-11 rounded-[10px] focus-visible:ring-0 focus-visible:border-custom-base-green"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <div className="grid grid-cols-2 gap-4 gap-y-5">
            <FormField
              control={form.control}
              name="gender"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>
                    Gender <span className="text-red-500">*</span>
                  </FormLabel>
                  <FormControl>
                    <Input
                      placeholder="Doe"
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
              name="dateOfBirth"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>
                    Date of Birth <span className="text-red-500">*</span>
                  </FormLabel>
                  <FormControl>
                    <div className="relative">
                      <Input
                        type="date"
                        placeholder="Select Date of Birth"
                        {...field}
                        className="h-11 rounded-[10px] focus-visible:ring-0 focus-visible:border-custom-base-green"
                      />
                    </div>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>
                    Email <span className="text-red-500">*</span>
                  </FormLabel>
                  <FormControl>
                    <Input
                      placeholder="john.doe@example.com"
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
              name="phone"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>
                    Phone <span className="text-red-500">*</span>
                  </FormLabel>
                  <FormControl>
                    <Input
                      placeholder="09110214066"
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
              name="nationality"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>
                    Nationality <span className="text-red-500">*</span>
                  </FormLabel>
                  <FormControl>
                    <Input
                      placeholder="Indonesia"
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
              name="healthCareProvider"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>
                    Health Care <span className="text-red-500">*</span>
                  </FormLabel>
                  <FormControl>
                    <Input
                      placeholder="BCA"
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
              name="maritalStatus"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>
                    Marital Status <span className="text-red-500">*</span>
                  </FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    defaultValue={field.value}
                  >
                    <FormControl>
                      <SelectTrigger className="w-full h-11 data-[size=default]:h-11 rounded-[10px] focus-visible:ring-0 focus-visible:border-custom-base-green">
                        <SelectValue placeholder="Select marital status" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="single">Single</SelectItem>
                      <SelectItem value="married">Married</SelectItem>
                      <SelectItem value="divorced">Divorced</SelectItem>
                      <SelectItem value="widowed">Widowed</SelectItem>
                      <SelectItem value="separated">Separated</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="PersonalTaxId"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>
                    Personal Tax ID <span className="text-red-500">*</span>
                  </FormLabel>
                  <FormControl>
                    <Input
                      placeholder="QQ 12 34 56 A"
                      {...field}
                      className="h-11 rounded-[10px] focus-visible:ring-0 focus-visible:border-custom-base-green"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
          <FormField
            control={form.control}
            name="SocialInsurance"
            render={({ field }) => (
              <FormItem>
                <FormLabel>
                  Social Insurance <span className="text-red-500">*</span>
                </FormLabel>
                <FormControl>
                  <Input
                    placeholder="Indonesia"
                    {...field}
                    className="h-11 rounded-[10px] focus-visible:ring-0 focus-visible:border-custom-base-green"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        {/* <Button
          type="submit"
          className="bg-custom-grey-900 text-white cursor-pointer"
        >
          Save
        </Button> */}

        {/* Address Information but not inputs or with inputs with no borders */}

        <div className="flex flex-col gap-3 space-y-4 mt-6 p-6 border border-custom-grey-200 rounded-3xl">
          <div className="flex justify-between items-center">
            <Label className="text-custom-grey-900 font-bold text-[18px]">
              Address Information
            </Label>
            <Image src="/icons/edit.svg" alt="edit" width={18} height={18} />
          </div>

          <div className="flex flex-col gap-3 gap-y-1">
            <div className="flex flex-row gap-2 w-full ">
              <Label className="text-custom-grey-600 text-[14px] w-[150px]">
                Primary address
              </Label>
              <FormField
                control={form.control}
                name="primaryAddress"
                render={({ field }) => (
                  <FormItem className="w-full">
                    <FormControl className="w-full ">
                      <Input
                        placeholder="Banyumanik Street, Central Java. Semarang Indonesia"
                        {...field}
                        className="border-0 shadow-none h-11 text-custom-grey-900 placeholder:text-custom-grey-900 w-full rounded-[10px] focus-visible:ring-0 focus-visible:border-custom-base-green"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <div className="flex flex-row gap-2 w-full ">
              <Label className="text-custom-grey-600 text-[14px] w-[150px]">
                Country
              </Label>
              <FormField
                control={form.control}
                name="country"
                render={({ field }) => (
                  <FormItem className="w-full">
                    <FormControl className="w-full ">
                      <Input
                        placeholder="Indonesia"
                        {...field}
                        className="border-0 shadow-none h-11 text-custom-grey-900 placeholder:text-custom-grey-900 w-full rounded-[10px] focus-visible:ring-0 focus-visible:border-custom-base-green"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <div className="flex flex-row gap-2 w-full ">
              <Label className="text-custom-grey-600 text-[14px] w-[150px]">
                City
              </Label>
              <FormField
                control={form.control}
                name="city"
                render={({ field }) => (
                  <FormItem className="w-full">
                    <FormControl className="w-full ">
                      <Input
                        placeholder="Central Java"
                        {...field}
                        className="border-0 shadow-none h-11 text-custom-grey-900 placeholder:text-custom-grey-900 w-full rounded-[10px] focus-visible:ring-0 focus-visible:border-custom-base-green"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <div className="flex flex-row gap-2 w-full ">
              <Label className="text-custom-grey-600 text-[14px] w-[150px]">
                State
              </Label>
              <FormField
                control={form.control}
                name="state"
                render={({ field }) => (
                  <FormItem className="w-full">
                    <FormControl className="w-full ">
                      <Input
                        placeholder="Semarang"
                        {...field}
                        className="border-0 shadow-none h-11 text-custom-grey-900 placeholder:text-custom-grey-900 w-full rounded-[10px] focus-visible:ring-0 focus-visible:border-custom-base-green"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <div className="flex flex-row gap-2 w-full ">
              <Label className="text-custom-grey-600 text-[14px] w-[150px]">
                Postal Code
              </Label>
              <FormField
                control={form.control}
                name="postalCode"
                render={({ field }) => (
                  <FormItem className="w-full">
                    <FormControl className="w-full ">
                      <Input
                        placeholder="10001"
                        {...field}
                        className="border-0 shadow-none h-11 text-custom-grey-900 placeholder:text-custom-grey-900 w-full rounded-[10px] focus-visible:ring-0 focus-visible:border-custom-base-green"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
          </div>
        </div>
      </form>
    </Form>
  )
}
