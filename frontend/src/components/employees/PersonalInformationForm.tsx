'use client'

import React from 'react'
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
import Image from 'next/image'
import type { Employee } from '@/types/employees'
import { CountrySelect } from '../ui/country-select'
import { StateSelect } from '../ui/state-select'
import { CitySelect } from '../ui/city-select'
import countriesData from '@/static-data/countriesminified.json'
import type { Country, StatesData, State } from '@/types/geography'

const formSchema = z.object({
  first_name: z.string().min(2, {
    message: 'First Name must be at least 2 characters.',
  }),
  last_name: z.string().min(2, {
    message: 'Last Name must be at least 2 characters.',
  }),
  gender: z.string().min(1, { message: 'Gender is required.' }),
  date_of_birth: z.string().min(1, {
    message: 'Date of birth is required.',
  }),
  email: z.email({
    message: 'Invalid email address.',
  }),
  phone: z.string().min(10, {
    message: 'Phone number must be at least 10 characters.',
  }),
  nationality: z.string().min(1, { message: 'Nationality is required.' }),
  health_care_provider: z.string().min(1, {
    message: 'Health care provider is required.',
  }),
  marital_status: z.string().min(1, {
    message: 'Marital status is required.',
  }),
  personal_tax_id: z.string().min(1, {
    message: 'Personal tax number is required.',
  }),
  social_insurance_number: z.string().min(1, {
    message: 'Social insurance number is required.',
  }),
  primary_address: z.string().min(1, {
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
  postal_code: z.string().min(1, {
    message: 'Postal code is required.',
  }),
})

// Helper function to convert country iso3 to country ID
const getCountryIdFromIso3 = (iso3: string | undefined): number | undefined => {
  if (!iso3) return undefined
  const country = (countriesData as Country[]).find((c: Country) => c.iso3 === iso3)
  return country?.id
}

// Helper function to get state ID from state code
const getStateIdFromCode = async (stateCode: string | undefined, countryId: number | undefined): Promise<number | undefined> => {
  if (!stateCode || !countryId) return undefined
  
  try {
    const response = await fetch('/data/statesminified.json')
    if (!response.ok) return undefined
    
    const statesData = await response.json()
    const country = statesData.find((country: StatesData) => country.id === countryId)
    if (!country) return undefined
    
    const state = country.states.find((state: State) => state.state_code === stateCode)
    return state?.id
  } catch {
    return undefined
  }
}


export function PersonalInformationForm( { employee }: { employee: Employee }) {
  // 1. Define your form.
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      first_name: employee.first_name,
      last_name: employee.last_name,
      gender: employee.personal_details.gender,
      date_of_birth: employee.personal_details.date_of_birth ?? '',
      email: employee.email,
      phone: employee.phone,
      nationality: employee.personal_details.nationality ?? '',
      health_care_provider: employee.personal_details.health_care_provider ?? '',
      marital_status: employee.personal_details.marital_status ?? '',
      personal_tax_id: employee.personal_details.personal_tax_id ?? '',
      social_insurance_number: employee.personal_details.social_insurance_number ?? '',
      primary_address: employee.personal_details.primary_address ?? '',
      country: employee.personal_details.country ?? '',
      city: employee.personal_details.city ?? '',
      state: employee.personal_details.state ?? '',
      postal_code: employee.personal_details.postal_code ?? '',
    },
  })

  // State to track resolved state ID for city filtering
  const [resolvedStateId, setResolvedStateId] = React.useState<number | undefined>(undefined)

  // Watch for state changes and resolve state ID
  const watchedState = form.watch('state')
  const watchedCountry = form.watch('country')
  
  React.useEffect(() => {
    const resolveStateId = async () => {
      const countryId = getCountryIdFromIso3(watchedCountry)
      const stateId = await getStateIdFromCode(watchedState, countryId)
      setResolvedStateId(stateId)
    }
    
    if (watchedState && watchedCountry) {
      resolveStateId()
    } else {
      setResolvedStateId(undefined)
    }
  }, [watchedState, watchedCountry])

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
          
          <div className="grid grid-cols-2 gap-4 gap-y-5">
          <FormField
            control={form.control}
            name="first_name"
            render={({ field }) => (
              <FormItem>
                {/* Required */}
                <FormLabel>
                  First Name <span className="text-red-500">*</span>
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
          <FormField
            control={form.control}
            name="last_name"
            render={({ field }) => (
              <FormItem>
                {/* Required */}
                <FormLabel>
                  Last Name <span className="text-red-500">*</span>
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
          </div>
          <div className="grid grid-cols-2 gap-4 gap-y-5">
            <FormField
              control={form.control}
              name="gender"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>
                    Gender <span className="text-red-500">*</span>
                  </FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    defaultValue={field.value?.toLowerCase() ?? ''}
                  >
                    <FormControl>
                      <SelectTrigger className="w-full h-11 data-[size=default]:h-11 rounded-[10px] focus-visible:ring-0 focus-visible:border-custom-base-green">
                        <SelectValue placeholder="Select gender" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="male">Male</SelectItem>
                      <SelectItem value="female">Female</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                      <SelectItem value="prefer-not-to-say">Prefer not to say</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="date_of_birth"
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
                    <CountrySelect
                      value={field.value}
                      onValueChange={field.onChange}
                      placeholder="Select nationality"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="health_care_provider"
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
              name="marital_status"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>
                    Marital Status <span className="text-red-500">*</span>
                  </FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    defaultValue={field.value?.toLowerCase() ?? ''}
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
              name="personal_tax_id"
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
            name="social_insurance_number"
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
                name="primary_address"
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
                      <CountrySelect
                        value={field.value}
                        onValueChange={field.onChange}
                        placeholder="Select country"
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
                      <CitySelect
                        value={field.value}
                        onValueChange={field.onChange}
                        placeholder="Select city"
                        countryId={getCountryIdFromIso3(form.watch('country'))}
                        stateId={resolvedStateId}
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
                      <StateSelect
                        value={field.value}
                        onValueChange={field.onChange}
                        placeholder="Select state"
                        countryId={getCountryIdFromIso3(form.watch('country'))}
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
                name="postal_code"
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
        <Button
          type="submit"
          className="bg-custom-grey-900 text-white cursor-pointer w-full mt-10"
        >
          Save
        </Button>
      </form>
    </Form>
  )
}
