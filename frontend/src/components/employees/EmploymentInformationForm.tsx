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
import { Plus, Trash2 } from 'lucide-react'
import Image from 'next/image'

const jobTimelineSchema = z.object({
  effectiveDate: z.string().min(1, {
    message: 'Effective date is required.',
  }),
  jobTitle: z.string().min(1, {
    message: 'Job title is required.',
  }),
  positionType: z.string().optional(),
  employmentType: z.string().min(1, {
    message: 'Employment type is required.',
  }),
  lineManager: z.string().min(1, {
    message: 'Line manager is required.',
  }),
})

const contractTimelineSchema = z.object({
  contractNumber: z.string().min(1, {
    message: 'Contract number is required.',
  }),
  contractName: z.string().min(1, {
    message: 'Contract name is required.',
  }),
  contractType: z.string().min(1, {
    message: 'Contract type is required.',
  }),
  contractStartDate: z.string().min(1, {
    message: 'Contract start date is required.',
  }),
  contractEndDate: z.string().optional(),
})

const formSchema = z.object({
  employeeId: z.string().min(2, {
    message: 'Employee ID must be at least 2 characters.',
  }),
  serviceYear: z.string().min(2, {
    message: 'Service year must be at least 2 characters.',
  }),
  joinDate: z.string().min(1, {
    message: 'Join date is required.',
  }),
  jobTimelines: z.array(jobTimelineSchema).min(1, {
    message: 'At least one job timeline entry is required.',
  }),
  contractTimelines: z.array(contractTimelineSchema).min(1, {
    message: 'At least one contract timeline entry is required.',
  }),
  currentWorkSchedule: z.string().min(1, {
    message: 'Current work schedule is required.',
  }),
  standardWorkingHours: z.string().min(1, {
    message: 'Standard working hours is required.',
  }),
  scheduleType: z.string().min(1, {
    message: 'Schedule type is required.',
  }),
  totalWorkingHoursByWeek: z.string().min(1, {
    message: 'Total working hours by week is required.',
  }),
  dailyWorkingHours: z.object({
    monday: z.string().min(1, { message: 'Monday is required.' }),
    tuesday: z.string().min(1, { message: 'Tuesday is required.' }),
    wednesday: z.string().min(1, { message: 'Wednesday is required.' }),
    thursday: z.string().min(1, { message: 'Thursday is required.' }),
    friday: z.string().min(1, { message: 'Friday is required.' }),
    saturday: z.string().optional(),
    sunday: z.string().optional(),
  }),
})

export function EmploymentInformationForm() {
  // 1. Define your form.
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      employeeId: '',
      serviceYear: '',
      joinDate: '',
      jobTimelines: [
        {
          effectiveDate: '',
          jobTitle: '',
          positionType: '',
          employmentType: '',
          lineManager: '',
        },
      ],
      contractTimelines: [
        {
          contractNumber: '',
          contractName: '',
          contractType: '',
          contractStartDate: '',
          contractEndDate: '',
        },
      ],
      currentWorkSchedule: '',
      standardWorkingHours: '',
      scheduleType: '',
      totalWorkingHoursByWeek: '',
      dailyWorkingHours: {
        monday: '',
        tuesday: '',
        wednesday: '',
        thursday: '',
        friday: '',
        saturday: '',
        sunday: '',
      },
    },
  })

  // Helper functions for managing timeline arrays
  const addJobTimeline = () => {
    const currentJobTimelines = form.getValues('jobTimelines')
    form.setValue('jobTimelines', [
      ...currentJobTimelines,
      {
        effectiveDate: '',
        jobTitle: '',
        positionType: '',
        employmentType: '',
        lineManager: '',
      },
    ])
  }

  const removeJobTimeline = (index: number) => {
    const currentJobTimelines = form.getValues('jobTimelines')
    if (currentJobTimelines.length > 1) {
      form.setValue(
        'jobTimelines',
        currentJobTimelines.filter((_, i) => i !== index),
      )
    }
  }

  const addContractTimeline = () => {
    const currentContractTimelines = form.getValues('contractTimelines')
    form.setValue('contractTimelines', [
      ...currentContractTimelines,
      {
        contractNumber: '',
        contractName: '',
        contractType: '',
        contractStartDate: '',
        contractEndDate: '',
      },
    ])
  }

  const removeContractTimeline = (index: number) => {
    const currentContractTimelines = form.getValues('contractTimelines')
    if (currentContractTimelines.length > 1) {
      form.setValue(
        'contractTimelines',
        currentContractTimelines.filter((_, i) => i !== index),
      )
    }
  }

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
              Employment Information
            </Label>
            <Image src="/icons/edit.svg" alt="edit" width={18} height={18} />
          </div>

          <div className="flex flex-col gap-3 gap-y-1">
            <div className="flex flex-row gap-2 w-full ">
              <Label className="text-custom-grey-600 text-[14px] w-[150px]">
                Employee ID
              </Label>
              <FormField
                control={form.control}
                name="employeeId"
                render={({ field }) => (
                  <FormItem className="w-full">
                    <FormControl className="w-full ">
                      <Input
                        placeholder="1234567890"
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
                Service Year
              </Label>
              <FormField
                control={form.control}
                name="serviceYear"
                render={({ field }) => (
                  <FormItem className="w-full">
                    <FormControl className="w-full ">
                      <Input
                        placeholder="2024"
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
                Join Date
              </Label>
              <FormField
                control={form.control}
                name="joinDate"
                render={({ field }) => (
                  <FormItem className="w-full">
                    <FormControl className="w-full ">
                      <Input
                        placeholder="2024-01-01"
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

        {/* Job Timeline Table */}
        <div className="flex flex-col gap-3 space-y-4 mt-6 p-6 border border-custom-grey-200 rounded-3xl">
          <div className="flex justify-between items-center">
            <Label className="text-custom-grey-900 font-bold text-[18px]">
              Job Timeline
            </Label>
            <Button
              type="button"
              onClick={addJobTimeline}
              className="bg-custom-base-green text-white h-8 w-8 p-0 rounded-full"
            >
              <Plus className="h-4 w-4" />
            </Button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-custom-grey-100">
                  <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                    Effective Date
                  </th>
                  <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                    Job Title
                  </th>
                  <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                    Position Type
                  </th>
                  <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                    Employment Type
                  </th>
                  <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                    Line Manager
                  </th>
                  <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody>
                {form.watch('jobTimelines').map((_, index) => (
                  <tr key={index} className="border-b border-custom-grey-200">
                    <td className="p-3">
                      <FormField
                        control={form.control}
                        name={`jobTimelines.${index}.effectiveDate`}
                        render={({ field }) => (
                          <FormItem>
                            <FormControl>
                              <Input
                                type="date"
                                {...field}
                                className="border-0 shadow-none h-8 text-custom-grey-900 w-full focus-visible:ring-0 focus-visible:border-custom-base-green"
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </td>
                    <td className="p-3">
                      <FormField
                        control={form.control}
                        name={`jobTimelines.${index}.jobTitle`}
                        render={({ field }) => (
                          <FormItem>
                            <FormControl>
                              <Input
                                placeholder="UI UX Designer"
                                {...field}
                                className="border-0 shadow-none h-8 text-custom-grey-900 w-full focus-visible:ring-0 focus-visible:border-custom-base-green"
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </td>
                    <td className="p-3">
                      <FormField
                        control={form.control}
                        name={`jobTimelines.${index}.positionType`}
                        render={({ field }) => (
                          <FormItem>
                            <FormControl>
                              <Input
                                placeholder="-"
                                {...field}
                                className="border-0 shadow-none h-8 text-custom-grey-900 w-full focus-visible:ring-0 focus-visible:border-custom-base-green"
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </td>
                    <td className="p-3">
                      <FormField
                        control={form.control}
                        name={`jobTimelines.${index}.employmentType`}
                        render={({ field }) => (
                          <FormItem>
                            <Select
                              onValueChange={field.onChange}
                              defaultValue={field.value}
                            >
                              <FormControl>
                                <SelectTrigger className="border-0 shadow-none h-8 data-[size=default]:h-8 w-full focus-visible:ring-0 focus-visible:border-custom-base-green">
                                  <SelectValue placeholder="Fulltime" />
                                </SelectTrigger>
                              </FormControl>
                              <SelectContent>
                                <SelectItem value="fulltime">
                                  Fulltime
                                </SelectItem>
                                <SelectItem value="part-time">
                                  Part Time
                                </SelectItem>
                                <SelectItem value="contract">
                                  Contract
                                </SelectItem>
                                <SelectItem value="internship">
                                  Internship
                                </SelectItem>
                              </SelectContent>
                            </Select>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </td>
                    <td className="p-3">
                      <FormField
                        control={form.control}
                        name={`jobTimelines.${index}.lineManager`}
                        render={({ field }) => (
                          <FormItem>
                            <FormControl>
                              <Input
                                placeholder="@skylar"
                                {...field}
                                className="border-0 shadow-none h-8 text-custom-grey-900 w-full focus-visible:ring-0 focus-visible:border-custom-base-green"
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </td>
                    <td className="p-3">
                      {form.watch('jobTimelines').length > 1 && (
                        <Button
                          type="button"
                          onClick={() => removeJobTimeline(index)}
                          className="bg-red-500 text-white h-6 w-6 p-0 rounded-full"
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Contract Timeline Table */}
        <div className="flex flex-col gap-3 space-y-4 mt-6 p-6 border border-custom-grey-200 rounded-3xl">
          <div className="flex justify-between items-center">
            <Label className="text-custom-grey-900 font-bold text-[18px]">
              Contract Timeline
            </Label>
            <Button
              type="button"
              onClick={addContractTimeline}
              className="bg-custom-base-green text-white h-8 w-8 p-0 rounded-full"
            >
              <Plus className="h-4 w-4" />
            </Button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-custom-grey-100">
                  <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                    Contract Number
                  </th>
                  <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                    Contract Name
                  </th>
                  <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                    Contract Type
                  </th>
                  <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                    Start Date
                  </th>
                  <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                    End Date
                  </th>
                  <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody>
                {form.watch('contractTimelines').map((_, index) => (
                  <tr key={index} className="border-b border-custom-grey-200">
                    <td className="p-3">
                      <FormField
                        control={form.control}
                        name={`contractTimelines.${index}.contractNumber`}
                        render={({ field }) => (
                          <FormItem>
                            <FormControl>
                              <Input
                                placeholder="#12345"
                                {...field}
                                className="border-0 shadow-none h-8 text-custom-grey-900 w-full focus-visible:ring-0 focus-visible:border-custom-base-green"
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </td>
                    <td className="p-3">
                      <FormField
                        control={form.control}
                        name={`contractTimelines.${index}.contractName`}
                        render={({ field }) => (
                          <FormItem>
                            <FormControl>
                              <Input
                                placeholder="Fulltime Remote"
                                {...field}
                                className="border-0 shadow-none h-8 text-custom-grey-900 w-full focus-visible:ring-0 focus-visible:border-custom-base-green"
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </td>
                    <td className="p-3">
                      <FormField
                        control={form.control}
                        name={`contractTimelines.${index}.contractType`}
                        render={({ field }) => (
                          <FormItem>
                            <Select
                              onValueChange={field.onChange}
                              defaultValue={field.value}
                            >
                              <FormControl>
                                <SelectTrigger className="border-0 shadow-none h-8 data-[size=default]:h-8 w-full focus-visible:ring-0 focus-visible:border-custom-base-green">
                                  <SelectValue placeholder="Fulltime Remote" />
                                </SelectTrigger>
                              </FormControl>
                              <SelectContent>
                                <SelectItem value="fulltime-remote">
                                  Fulltime Remote
                                </SelectItem>
                                <SelectItem value="fulltime-office">
                                  Fulltime Office
                                </SelectItem>
                                <SelectItem value="part-time">
                                  Part Time
                                </SelectItem>
                                <SelectItem value="contract">
                                  Contract
                                </SelectItem>
                              </SelectContent>
                            </Select>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </td>
                    <td className="p-3">
                      <FormField
                        control={form.control}
                        name={`contractTimelines.${index}.contractStartDate`}
                        render={({ field }) => (
                          <FormItem>
                            <FormControl>
                              <Input
                                type="date"
                                {...field}
                                className="border-0 shadow-none h-8 text-custom-grey-900 w-full focus-visible:ring-0 focus-visible:border-custom-base-green"
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </td>
                    <td className="p-3">
                      <FormField
                        control={form.control}
                        name={`contractTimelines.${index}.contractEndDate`}
                        render={({ field }) => (
                          <FormItem>
                            <FormControl>
                              <Input
                                type="date"
                                placeholder="-"
                                {...field}
                                className="border-0 shadow-none h-8 text-custom-grey-900 w-full focus-visible:ring-0 focus-visible:border-custom-base-green"
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </td>
                    <td className="p-3">
                      {form.watch('contractTimelines').length > 1 && (
                        <Button
                          type="button"
                          onClick={() => removeContractTimeline(index)}
                          className="bg-red-500 text-white h-6 w-6 p-0 rounded-full"
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Work Schedule */}
        <div className="flex flex-col gap-3 space-y-4 mt-6 p-6 border border-custom-grey-200 rounded-3xl">
          <div className="flex justify-between items-center">
            <Label className="text-custom-grey-900 font-bold text-[18px]">
              Work Schedule
            </Label>
            <Image src="/icons/edit.svg" alt="edit" width={18} height={18} />
          </div>

          <div className="flex flex-col gap-3 gap-y-1">
            <div className="flex flex-row gap-2 w-full ">
              <Label className="text-custom-grey-600 text-[14px] w-[260px]">
                Current Work Schedule
              </Label>
              <FormField
                control={form.control}
                name="currentWorkSchedule"
                render={({ field }) => (
                  <FormItem className="w-full">
                    <FormControl className="w-full ">
                      <Input
                        placeholder="Mon-Fri, Duration 40 hours/week"
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
              <Label className="text-custom-grey-600 text-[14px] w-[260px]">
                Standard Working Hours
              </Label>
              <FormField
                control={form.control}
                name="standardWorkingHours"
                render={({ field }) => (
                  <FormItem className="w-full">
                    <FormControl className="w-full ">
                      <Input
                        placeholder="8h 00m"
                        {...field}
                        className="border-0 shadow-none h-11 text-custom-grey-900 placeholder:text-custom-grey-900 w-full rounded-[10px] focus-visible:ring-0 focus-visible:border-custom-base-green"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            {/* Schedule Type */}
            <div className="flex flex-row gap-2 w-full ">
              <Label className="text-custom-grey-600 text-[14px] w-[260px]">
                Schedule Type
              </Label>
              <FormField
                control={form.control}
                name="scheduleType"
                render={({ field }) => (
                  <FormItem className="w-full">
                    <FormControl className="w-full ">
                      <Select
                        onValueChange={field.onChange}
                        defaultValue={field.value}
                      >
                        <FormControl>
                          <SelectTrigger className="border-0 shadow-none h-8 data-[size=default]:h-8 w-full focus-visible:ring-0 focus-visible:border-custom-base-green">
                            <SelectValue placeholder="Duration Based" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="duration-based">
                            Duration Based
                          </SelectItem>
                          <SelectItem value="shift-based">
                            Shift Based
                          </SelectItem>
                          <SelectItem value="flexible">Flexible</SelectItem>
                        </SelectContent>
                      </Select>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            {/* Total Working Hours/Week */}
            <div className="flex flex-row gap-2 w-full ">
              <Label className="text-custom-grey-600 text-[14px] w-[260px]">
                Total Working Hours/Week
              </Label>
              <FormField
                control={form.control}
                name="totalWorkingHoursByWeek"
                render={({ field }) => (
                  <FormItem className="w-full">
                    <FormControl className="w-full ">
                      <Input
                        placeholder="40h 00m"
                        {...field}
                        className="border-0 shadow-none h-11 text-custom-grey-900 placeholder:text-custom-grey-900 w-full rounded-[10px] focus-visible:ring-0 focus-visible:border-custom-base-green"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            {/* Daily Working Hours */}
            <div className="flex flex-row justify-baseline items-baseline gap-2 w-full">
              <Label className="text-custom-grey-600 text-[14px] w-[200px]">
                Daily Working Hours
              </Label>
              <div className="flex flex-col gap-2 ml-0">
                <div className="flex flex-row gap-2 w-full">
                  <Label className="text-custom-grey-900 text-[14px] w-[100px]">
                    Monday
                  </Label>
                  <FormField
                    control={form.control}
                    name="dailyWorkingHours.monday"
                    render={({ field }) => (
                      <FormItem className="w-full">
                        <FormControl>
                          <Input
                            placeholder="8h 00m"
                            {...field}
                            className="border-0 shadow-none h-8 text-custom-grey-600 placeholder:text-custom-grey-600 w-full rounded-[10px] focus-visible:ring-0 focus-visible:border-custom-base-green"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
                <div className="flex flex-row gap-2 w-full">
                  <Label className="text-custom-grey-900 text-[14px] w-[100px]">
                    Tuesday
                  </Label>
                  <FormField
                    control={form.control}
                    name="dailyWorkingHours.tuesday"
                    render={({ field }) => (
                      <FormItem className="w-full">
                        <FormControl>
                          <Input
                            placeholder="8h 00m"
                            {...field}
                            className="border-0 shadow-none h-8 text-custom-grey-600 placeholder:text-custom-grey-600 w-full rounded-[10px] focus-visible:ring-0 focus-visible:border-custom-base-green"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
                <div className="flex flex-row gap-2 w-full">
                  <Label className="text-custom-grey-900 text-[14px] w-[100px]">
                    Wednesday
                  </Label>
                  <FormField
                    control={form.control}
                    name="dailyWorkingHours.wednesday"
                    render={({ field }) => (
                      <FormItem className="w-full">
                        <FormControl>
                          <Input
                            placeholder="8h 00m"
                            {...field}
                            className="border-0 shadow-none h-8 text-custom-grey-600 placeholder:text-custom-grey-600 w-full rounded-[10px] focus-visible:ring-0 focus-visible:border-custom-base-green"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
                <div className="flex flex-row gap-2 w-full">
                  <Label className="text-custom-grey-900 text-[14px] w-[100px]">
                    Thursday
                  </Label>
                  <FormField
                    control={form.control}
                    name="dailyWorkingHours.thursday"
                    render={({ field }) => (
                      <FormItem className="w-full">
                        <FormControl>
                          <Input
                            placeholder="8h 00m"
                            {...field}
                            className="border-0 shadow-none h-8 text-custom-grey-600 placeholder:text-custom-grey-600 w-full rounded-[10px] focus-visible:ring-0 focus-visible:border-custom-base-green"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
                <div className="flex flex-row gap-2 w-full">
                  <Label className="text-custom-grey-900 text-[14px] w-[100px]">
                    Friday
                  </Label>
                  <FormField
                    control={form.control}
                    name="dailyWorkingHours.friday"
                    render={({ field }) => (
                      <FormItem className="w-full">
                        <FormControl>
                          <Input
                            placeholder="8h 00m"
                            {...field}
                            className="border-0 shadow-none h-8 text-custom-grey-600 placeholder:text-custom-grey-600 w-full rounded-[10px] focus-visible:ring-0 focus-visible:border-custom-base-green"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <Button
          type="submit"
          onClick={() => form.handleSubmit(onSubmit)}
          className="bg-custom-grey-900 text-white cursor-pointer w-full mt-10"
        >
          Submit
        </Button>
      </form>
    </Form>
  )
}
