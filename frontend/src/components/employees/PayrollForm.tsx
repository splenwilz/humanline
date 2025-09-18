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
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '../ui/tooltip'
import { ChevronDown, ChevronUp, Plus, Trash2, HelpCircle } from 'lucide-react'
import { useState } from 'react'

const formSchema = z.object({
  // Employment Information
  employeeStatus: z.string().min(1, {
    message: 'Employee status is required.',
  }),
  employeeType: z.string().min(1, {
    message: 'Employee type is required.',
  }),
  geofencing: z.string().min(1, {
    message: 'Geofence is required.',
  }),
  jobTitle: z.string().min(1, {
    message: 'Job title is required.',
  }),
  jobDate: z.string().min(1, {
    message: 'Job date is required.',
  }),
  lastWorkingDate: z.string().optional(),

  // Total Compensation
  totalCompensation: z.string().min(1, {
    message: 'Total compensation is required.',
  }),

  // Salary
  salary: z.object({
    amount: z.string().optional(),
    currency: z.string().optional(),
  }),

  // Recurring
  recurring: z.object({
    amount: z.string().optional(),
    currency: z.string().optional(),
    items: z
      .array(
        z.object({
          item: z.string().optional(),
          type: z.string().optional(),
          amount: z
            .string()
            .refine((val) => !val || !isNaN(parseFloat(val)), {
              message: 'Amount must be a valid number',
            })
            .optional(),
          frequency: z.string().optional(),
        }),
      )
      .optional(),
  }),

  // One-off
  oneOff: z.object({
    amount: z.string().optional(),
    currency: z.string().optional(),
    items: z
      .array(
        z.object({
          item: z.string().optional(),
          type: z.string().optional(),
          amount: z
            .string()
            .refine((val) => !val || !isNaN(parseFloat(val)), {
              message: 'Amount must be a valid number',
            })
            .optional(),
          date: z.string().optional(),
        }),
      )
      .optional(),
  }),

  // Time-off
  timeOff: z.object({
    amount: z.string().optional(),
    currency: z.string().optional(),
    items: z
      .array(
        z.object({
          type: z.string().optional(),
          daysUsed: z.string().optional(),
          daysRemaining: z.string().optional(),
          amount: z
            .string()
            .refine((val) => !val || !isNaN(parseFloat(val)), {
              message: 'Amount must be a valid number',
            })
            .optional(),
        }),
      )
      .optional(),
  }),

  // Overtime
  overtime: z.object({
    amount: z.string().optional(),
    currency: z.string().optional(),
    items: z
      .array(
        z.object({
          date: z.string().optional(),
          hours: z.string().optional(),
          rate: z.string().optional(),
          amount: z
            .string()
            .refine((val) => !val || !isNaN(parseFloat(val)), {
              message: 'Amount must be a valid number',
            })
            .optional(),
        }),
      )
      .optional(),
  }),

  // Deficit
  deficit: z.object({
    totalAmount: z.string().optional(),
    entries: z
      .array(
        z.object({
          deficit: z.string().optional(),
          type: z.string().optional(),
          amount: z.string().optional(),
        }),
      )
      .optional(),
  }),

  // Attendance
  attendance: z.object({
    totalHours: z.string().optional(),
    entries: z
      .array(
        z.object({
          period: z.string().optional(),
          actualWorkHours: z.string().optional(),
        }),
      )
      .optional(),
  }),

  // Carry Over of Overtime
  carryOverOvertime: z.string().optional(),

  // Dependents
  dependents: z.object({
    count: z.string().optional(),
    items: z
      .array(
        z.object({
          name: z.string().optional(),
          relationship: z.string().optional(),
          dateOfBirth: z.string().optional(),
          taxBenefit: z.string().optional(),
        }),
      )
      .optional(),
  }),

  // Bank Information
  bankInfo: z.object({
    bankName: z.string().optional(),
    branch: z.string().optional(),
    swiftBic: z.string().optional(),
    accountName: z.string().optional(),
    accountNumber: z.string().optional(),
    iban: z.string().optional(),
  }),

  // Offset
  offset: z.array(
    z.object({
      amount: z.string().optional(),
      currency: z.string().optional(),
      description: z.string().optional(),
    }),
  ),
})

export default function PayrollForm() {
  // State for collapsible sections
  const [expandedSections, setExpandedSections] = useState({
    recurring: false,
    oneOff: false,
    timeOff: false,
    overtime: false,
    deficit: true, // Expanded by default as shown in screenshot
    attendance: true, // Expanded by default as shown in screenshot
    carryOverOvertime: false,
    dependents: false,
  })

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }))
  }

  // 1. Define your form.
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      employeeStatus: 'Active',
      employeeType: 'Contractor',
      geofencing: '30 Sep 2024',
      jobTitle: 'Junior UI/UX Designer',
      jobDate: '16 Feb 2020',
      lastWorkingDate: '-',
      totalCompensation: '3,729,00',
      salary: {
        amount: '',
        currency: 'USD',
      },
      recurring: {
        amount: '0',
        currency: 'USD',
        items: [
          {
            item: 'Health Insurance',
            type: 'Benefit',
            amount: '$150.00',
            frequency: 'Monthly',
          },
          {
            item: 'Transportation Allowance',
            type: 'Allowance',
            amount: '$200.00',
            frequency: 'Monthly',
          },
        ],
      },
      oneOff: {
        amount: '0',
        currency: 'USD',
        items: [
          {
            item: 'Performance Bonus',
            type: 'Bonus',
            amount: '$500.00',
            date: '2024-12-01',
          },
          {
            item: 'Project Completion',
            type: 'Bonus',
            amount: '$1,000.00',
            date: '2024-11-15',
          },
        ],
      },
      timeOff: {
        amount: '0',
        currency: 'USD',
        items: [
          {
            type: 'Annual Leave',
            daysUsed: '5',
            daysRemaining: '15',
            amount: '$0.00',
          },
          {
            type: 'Sick Leave',
            daysUsed: '2',
            daysRemaining: '8',
            amount: '$0.00',
          },
        ],
      },
      overtime: {
        amount: '0',
        currency: 'USD',
        items: [
          {
            date: '2024-11-20',
            hours: '4',
            rate: '$25.00',
            amount: '$100.00',
          },
          {
            date: '2024-11-25',
            hours: '6',
            rate: '$25.00',
            amount: '$150.00',
          },
        ],
      },
      deficit: {
        totalAmount: '-$529,00',
        entries: [
          {
            deficit: '-13h 30m',
            type: 'Regular',
            amount: '$229,00',
          },
          {
            deficit: '-14h 30m',
            type: 'Regular',
            amount: '$300,00',
          },
        ],
      },
      attendance: {
        totalHours: '40h 30m',
        entries: [
          {
            period: '1 Feb 2023 - 28 Feb 2023',
            actualWorkHours: '40h 30m',
          },
        ],
      },
      carryOverOvertime: '-',
      dependents: {
        count: '0',
        items: [
          {
            name: 'No dependents',
            relationship: '-',
            dateOfBirth: '-',
            taxBenefit: '$0.00',
          },
        ],
      },
      bankInfo: {
        bankName: 'Bank Central Asia',
        branch: 'Banyumanik',
        swiftBic: '-',
        accountName: 'Pristia Candra Arum',
        accountNumber: '00130249013492034',
        iban: '-',
      },
      offset: [
        {
          amount: '0',
          currency: 'USD',
          description: '',
        },
        {
          amount: '0',
          currency: 'USD',
          description: '',
        },
      ],
    },
  })

  // Helper functions for managing offset entries
  const addOffset = () => {
    const currentOffsets = form.getValues('offset')
    form.setValue('offset', [
      ...currentOffsets,
      {
        amount: '',
        currency: 'USD',
        description: '',
      },
    ])
  }

  const removeOffset = (index: number) => {
    const currentOffsets = form.getValues('offset')
    if (currentOffsets.length > 1) {
      form.setValue(
        'offset',
        currentOffsets.filter((_, i) => i !== index),
      )
    }
  }

  // Helper functions for adding/removing items from arrays
  const addRecurringItem = () => {
    const currentItems = form.getValues('recurring.items') || []
    form.setValue('recurring.items', [
      ...currentItems,
      { item: '', type: '', amount: '', frequency: '' },
    ])
  }

  const removeRecurringItem = (index: number) => {
    const currentItems = form.getValues('recurring.items') || []
    form.setValue(
      'recurring.items',
      currentItems.filter((_, i) => i !== index),
    )
  }

  const addOneOffItem = () => {
    const currentItems = form.getValues('oneOff.items') || []
    form.setValue('oneOff.items', [
      ...currentItems,
      { item: '', type: '', amount: '', date: '' },
    ])
  }

  const removeOneOffItem = (index: number) => {
    const currentItems = form.getValues('oneOff.items') || []
    form.setValue(
      'oneOff.items',
      currentItems.filter((_, i) => i !== index),
    )
  }

  const addTimeOffItem = () => {
    const currentItems = form.getValues('timeOff.items') || []
    form.setValue('timeOff.items', [
      ...currentItems,
      { type: '', daysUsed: '', daysRemaining: '', amount: '' },
    ])
  }

  const removeTimeOffItem = (index: number) => {
    const currentItems = form.getValues('timeOff.items') || []
    form.setValue(
      'timeOff.items',
      currentItems.filter((_, i) => i !== index),
    )
  }

  const addOvertimeItem = () => {
    const currentItems = form.getValues('overtime.items') || []
    form.setValue('overtime.items', [
      ...currentItems,
      { date: '', hours: '', rate: '', amount: '' },
    ])
  }

  const removeOvertimeItem = (index: number) => {
    const currentItems = form.getValues('overtime.items') || []
    form.setValue(
      'overtime.items',
      currentItems.filter((_, i) => i !== index),
    )
  }

  const addDependentItem = () => {
    const currentItems = form.getValues('dependents.items') || []
    form.setValue('dependents.items', [
      ...currentItems,
      { name: '', relationship: '', dateOfBirth: '', taxBenefit: '' },
    ])
  }

  const removeDependentItem = (index: number) => {
    const currentItems = form.getValues('dependents.items') || []
    form.setValue(
      'dependents.items',
      currentItems.filter((_, i) => i !== index),
    )
  }

  // Auto-calculation functions
  const calculateRecurringTotal = () => {
    const items = form.getValues('recurring.items') || []
    const total = items.reduce((sum, item) => {
      const amount = parseFloat(item.amount || '0')
      return sum + (isNaN(amount) ? 0 : amount)
    }, 0)
    form.setValue('recurring.amount', total.toString())
  }

  const calculateOneOffTotal = () => {
    const items = form.getValues('oneOff.items') || []
    const total = items.reduce((sum, item) => {
      const amount = parseFloat(item.amount || '0')
      return sum + (isNaN(amount) ? 0 : amount)
    }, 0)
    form.setValue('oneOff.amount', total.toString())
  }

  const calculateTimeOffTotal = () => {
    const items = form.getValues('timeOff.items') || []
    const total = items.reduce((sum, item) => {
      const amount = parseFloat(item.amount || '0')
      return sum + (isNaN(amount) ? 0 : amount)
    }, 0)
    form.setValue('timeOff.amount', total.toString())
  }

  const calculateOvertimeTotal = () => {
    const items = form.getValues('overtime.items') || []
    const total = items.reduce((sum, item) => {
      const amount = parseFloat(item.amount || '0')
      return sum + (isNaN(amount) ? 0 : amount)
    }, 0)
    form.setValue('overtime.amount', total.toString())
  }

  // 2. Define a submit handler.
  function onSubmit(values: z.infer<typeof formSchema>) {
    // Do something with the form values.
    // ✅ This will be type-safe and validated.
    console.log(values)
  }
  return (
    <TooltipProvider>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="">
          {/* Employment Information Section */}
          <div className="flex flex-col gap-3 space-y-4 mt-6 p-6 border border-custom-grey-200 rounded-3xl">
            <div className="flex items-center gap-2 mb-2">
              <h3 className="text-custom-grey-900 font-semibold text-[18px]">
                Employment Information
              </h3>
              <Tooltip>
                <TooltipTrigger>
                  <HelpCircle className="w-4 h-4 text-custom-grey-400 hover:text-custom-grey-600" />
                </TooltipTrigger>
                <TooltipContent>
                  <p className="max-w-xs">
                    Basic employment details including status, type, location
                    tracking, and job information. This helps track employee
                    classification and work arrangements.
                  </p>
                </TooltipContent>
              </Tooltip>
            </div>
            <div className="grid grid-cols-2 gap-6">
              {/* Left Column */}
              <div className="flex flex-col gap-4">
                <div className="flex flex-row gap-2 w-full">
                  <Label className="text-custom-grey-600 text-[14px] w-[160px]">
                    Employee Status
                  </Label>
                  <FormField
                    control={form.control}
                    name="employeeStatus"
                    render={({ field }) => (
                      <FormItem className="w-full">
                        <Select
                          onValueChange={field.onChange}
                          defaultValue={field.value}
                        >
                          <FormControl>
                            <SelectTrigger className="border-0 shadow-none h-8 w-full focus-visible:ring-0 focus-visible:border-custom-base-green">
                              <SelectValue placeholder="Select status" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            <SelectItem value="Active">Active</SelectItem>
                            <SelectItem value="Resigned">Resigned</SelectItem>
                            <SelectItem value="Terminated">
                              Terminated
                            </SelectItem>
                            <SelectItem value="On Leave">On Leave</SelectItem>
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
                <div className="flex flex-row gap-2 w-full">
                  <Label className="text-custom-grey-600 text-[14px] w-[160px]">
                    Employment Type
                  </Label>
                  <FormField
                    control={form.control}
                    name="employeeType"
                    render={({ field }) => (
                      <FormItem className="w-full">
                        <FormControl>
                          <Input
                            {...field}
                            className="border-0 shadow-none h-8 text-custom-grey-900 w-full focus-visible:ring-0 focus-visible:border-custom-base-green"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
                <div className="flex flex-row gap-2 w-full">
                  <Label className="text-custom-grey-600 text-[14px] w-[160px]">
                    Geofencing
                  </Label>
                  <FormField
                    control={form.control}
                    name="geofencing"
                    render={({ field }) => (
                      <FormItem className="w-full">
                        <FormControl>
                          <Input
                            {...field}
                            className="border-0 shadow-none h-8 text-custom-grey-900 w-full focus-visible:ring-0 focus-visible:border-custom-base-green"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
              </div>

              {/* Right Column */}
              <div className="flex flex-col gap-4">
                <div className="flex flex-row gap-2 w-full">
                  <Label className="text-custom-grey-600 text-[14px] w-[160px]">
                    Job Title
                  </Label>
                  <FormField
                    control={form.control}
                    name="jobTitle"
                    render={({ field }) => (
                      <FormItem className="w-full">
                        <FormControl>
                          <Input
                            {...field}
                            className="border-0 shadow-none h-8 text-custom-grey-900 w-full focus-visible:ring-0 focus-visible:border-custom-base-green"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
                <div className="flex flex-row gap-2 w-full">
                  <Label className="text-custom-grey-600 text-[14px] w-[160px]">
                    Job Date
                  </Label>
                  <FormField
                    control={form.control}
                    name="jobDate"
                    render={({ field }) => (
                      <FormItem className="w-full">
                        <FormControl>
                          <Input
                            {...field}
                            className="border-0 shadow-none h-8 text-custom-grey-900 w-full focus-visible:ring-0 focus-visible:border-custom-base-green"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
                <div className="flex flex-row gap-2 w-full">
                  <Label className="text-custom-grey-600 text-[14px] w-[160px]">
                    Last Working Date
                  </Label>
                  <FormField
                    control={form.control}
                    name="lastWorkingDate"
                    render={({ field }) => (
                      <FormItem className="w-full">
                        <FormControl>
                          <Input
                            {...field}
                            className="border-0 shadow-none h-8 text-custom-grey-900 w-full focus-visible:ring-0 focus-visible:border-custom-base-green"
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

          {/* Total Compensation Section */}
          <div className="h-[75px] flex flex-col bg-custom-grey-50 gap-3 space-y-4 mt-6 p-3 px-6 border border-custom-grey-200 rounded-2xl">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <Label className="text-custom-grey-900 font-semibold text-[16px]">
                  Total Compensation
                </Label>
                <Tooltip>
                  <TooltipTrigger>
                    <HelpCircle className="w-4 h-4 text-custom-grey-400 hover:text-custom-grey-600" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p className="max-w-xs">
                      The grand total of all employee compensation including
                      salary, benefits, bonuses, and allowances minus any
                      deductions. This is the final amount paid to the employee.
                    </p>
                  </TooltipContent>
                </Tooltip>
              </div>
              <FormField
                control={form.control}
                name="totalCompensation"
                render={({ field }) => (
                  <FormItem>
                    <FormControl>
                      <Input
                        {...field}
                        className="border-0 shadow-none h-12 text-custom-grey-900 text-right text-xl font-bold w-32 focus-visible:ring-0 focus-visible:border-custom-base-green"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
          </div>

          {/* Salary Section */}
          <div className="h-[75px] py-5 px-6 flex flex-col gap-3 space-y-4 mt-6 border border-custom-grey-200 rounded-2xl">
            <div className="flex justify-between items-center ">
              <Label className="text-custom-grey-900 font-semibold text-[16px]">
                Salary
              </Label>
              <div className="flex gap-2">
                <FormField
                  control={form.control}
                  name="salary.amount"
                  render={({ field }) => (
                    <FormItem>
                      <FormControl>
                        <Input
                          placeholder="Amount"
                          {...field}
                          className="border-0 shadow-none h-8 text-custom-grey-900 w-24 focus-visible:ring-0 focus-visible:border-custom-base-green"
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="salary.currency"
                  render={({ field }) => (
                    <FormItem>
                      <FormControl>
                        <Select
                          onValueChange={field.onChange}
                          defaultValue={field.value}
                        >
                          <SelectTrigger className="border-0 shadow-none h-8 w-16 focus-visible:ring-0 focus-visible:border-custom-base-green">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="USD">USD</SelectItem>
                            <SelectItem value="EUR">EUR</SelectItem>
                            <SelectItem value="GBP">GBP</SelectItem>
                          </SelectContent>
                        </Select>
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </div>
          </div>

          {/* Recurring Section */}
          <div className="py-5 px-6 flex flex-col gap-3 space-y-4 mt-6 border border-custom-grey-200 rounded-2xl">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <Label className="text-custom-grey-900 font-semibold text-[16px]">
                  Recurring
                </Label>
                <Tooltip>
                  <TooltipTrigger>
                    <HelpCircle className="w-4 h-4 text-custom-grey-400 hover:text-custom-grey-600" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p className="max-w-xs">
                      Regular monthly benefits and allowances like health
                      insurance, transportation, meal allowances, and other
                      recurring perks that employees receive every pay period.
                    </p>
                  </TooltipContent>
                </Tooltip>
              </div>
              <div className="flex gap-2 items-center">
                <FormField
                  control={form.control}
                  name="recurring.amount"
                  render={({ field }) => (
                    <FormItem>
                      <FormControl>
                        <Input
                          {...field}
                          className="border-0 shadow-none h-8 text-custom-grey-900 w-16 focus-visible:ring-0 focus-visible:border-custom-base-green"
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <button
                  type="button"
                  onClick={() => toggleSection('recurring')}
                  className="p-1 hover:bg-custom-grey-100 rounded"
                >
                  {expandedSections.recurring ? (
                    <ChevronUp className="w-5 h-4 text-custom-grey-600" />
                  ) : (
                    <ChevronDown className="w-5 h-4 text-custom-grey-600" />
                  )}
                </button>
              </div>
            </div>

            {/* Recurring Items Table - Collapsible */}
            {expandedSections.recurring && (
              <div className="mt-4">
                <div className="flex justify-between items-center mb-3">
                  <h4 className="text-custom-grey-900 font-medium text-sm">
                    Recurring Items
                  </h4>
                  <button
                    type="button"
                    onClick={addRecurringItem}
                    className="flex items-center gap-1 text-custom-base-green text-sm hover:text-custom-grey-800"
                  >
                    <Plus className="w-4 h-4" />
                    Add Item
                  </button>
                </div>
                <table className="w-full">
                  <thead>
                    <tr className="bg-custom-grey-100">
                      <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                        Item
                      </th>
                      <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                        Type
                      </th>
                      <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                        Amount
                      </th>
                      <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                        Frequency
                      </th>
                      <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {form.watch('recurring.items')?.map((_, index) => (
                      <tr
                        key={index}
                        className="border-b border-custom-grey-200"
                      >
                        <td className="p-3">
                          <FormField
                            control={form.control}
                            name={`recurring.items.${index}.item`}
                            render={({ field }) => (
                              <FormItem>
                                <FormControl>
                                  <Input
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
                            name={`recurring.items.${index}.type`}
                            render={({ field }) => (
                              <FormItem>
                                <FormControl>
                                  <Input
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
                            name={`recurring.items.${index}.amount`}
                            render={({ field }) => (
                              <FormItem>
                                <FormControl>
                                  <Input
                                    {...field}
                                    onChange={(e) => {
                                      field.onChange(e)
                                      // Auto-calculate total after a short delay
                                      setTimeout(calculateRecurringTotal, 100)
                                    }}
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
                            name={`recurring.items.${index}.frequency`}
                            render={({ field }) => (
                              <FormItem>
                                <FormControl>
                                  <Input
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
                          <button
                            type="button"
                            onClick={() => removeRecurringItem(index)}
                            className="text-red-500 hover:text-red-700"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* One-off Section */}
          <div className="py-5 px-6 flex flex-col gap-3 space-y-4 mt-6 border border-custom-grey-200 rounded-2xl">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <Label className="text-custom-grey-900 font-semibold text-[16px]">
                  One-off
                </Label>
                <Tooltip>
                  <TooltipTrigger>
                    <HelpCircle className="w-4 h-4 text-custom-grey-400 hover:text-custom-grey-600" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p className="max-w-xs">
                      One-time payments like performance bonuses, project
                      completion rewards, signing bonuses, or special
                      recognition payments that are not recurring.
                    </p>
                  </TooltipContent>
                </Tooltip>
              </div>
              <div className="flex gap-2 items-center">
                <FormField
                  control={form.control}
                  name="oneOff.amount"
                  render={({ field }) => (
                    <FormItem>
                      <FormControl>
                        <Input
                          {...field}
                          className="border-0 shadow-none h-8 text-custom-grey-900 w-16 focus-visible:ring-0 focus-visible:border-custom-base-green"
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <button
                  type="button"
                  onClick={() => toggleSection('oneOff')}
                  className="p-1 hover:bg-custom-grey-100 rounded"
                >
                  {expandedSections.oneOff ? (
                    <ChevronUp className="w-5 h-4 text-custom-grey-600" />
                  ) : (
                    <ChevronDown className="w-5 h-4 text-custom-grey-600" />
                  )}
                </button>
              </div>
            </div>

            {/* One-off Items Table - Collapsible */}
            {expandedSections.oneOff && (
              <div className="mt-4">
                <div className="flex justify-between items-center mb-3">
                  <h4 className="text-custom-grey-900 font-medium text-sm">
                    One-off Items
                  </h4>
                  <button
                    type="button"
                    onClick={addOneOffItem}
                    className="flex items-center gap-1 text-custom-base-green text-sm hover:text-custom-grey-800"
                  >
                    <Plus className="w-4 h-4" />
                    Add Item
                  </button>
                </div>
                <table className="w-full">
                  <thead>
                    <tr className="bg-custom-grey-100">
                      <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                        Item
                      </th>
                      <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                        Type
                      </th>
                      <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                        Amount
                      </th>
                      <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                        Date
                      </th>
                      <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {form.watch('oneOff.items')?.map((_, index) => (
                      <tr
                        key={index}
                        className="border-b border-custom-grey-200"
                      >
                        <td className="p-3">
                          <FormField
                            control={form.control}
                            name={`oneOff.items.${index}.item`}
                            render={({ field }) => (
                              <FormItem>
                                <FormControl>
                                  <Input
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
                            name={`oneOff.items.${index}.type`}
                            render={({ field }) => (
                              <FormItem>
                                <FormControl>
                                  <Input
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
                            name={`oneOff.items.${index}.amount`}
                            render={({ field }) => (
                              <FormItem>
                                <FormControl>
                                  <Input
                                    {...field}
                                    onChange={(e) => {
                                      field.onChange(e)
                                      setTimeout(calculateOneOffTotal, 100)
                                    }}
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
                            name={`oneOff.items.${index}.date`}
                            render={({ field }) => (
                              <FormItem>
                                <FormControl>
                                  <Input
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
                          <button
                            type="button"
                            onClick={() => removeOneOffItem(index)}
                            className="text-red-500 hover:text-red-700"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Time-off Section */}
          <div className="py-5 px-6 flex flex-col gap-3 space-y-4 mt-6 border border-custom-grey-200 rounded-2xl">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <Label className="text-custom-grey-900 font-semibold text-[16px]">
                  Time-off
                </Label>
                <Tooltip>
                  <TooltipTrigger>
                    <HelpCircle className="w-4 h-4 text-custom-grey-400 hover:text-custom-grey-600" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p className="max-w-xs">
                      Leave management including vacation days, sick leave,
                      personal time off, and other paid time away from work.
                      Tracks days used vs. available.
                    </p>
                  </TooltipContent>
                </Tooltip>
              </div>
              <div className="flex gap-2 items-center">
                <FormField
                  control={form.control}
                  name="timeOff.amount"
                  render={({ field }) => (
                    <FormItem>
                      <FormControl>
                        <Input
                          {...field}
                          className="border-0 shadow-none h-8 text-custom-grey-900 w-16 focus-visible:ring-0 focus-visible:border-custom-base-green"
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <button
                  type="button"
                  onClick={() => toggleSection('timeOff')}
                  className="p-1 hover:bg-custom-grey-100 rounded"
                >
                  {expandedSections.timeOff ? (
                    <ChevronUp className="w-5 h-4 text-custom-grey-600" />
                  ) : (
                    <ChevronDown className="w-5 h-4 text-custom-grey-600" />
                  )}
                </button>
              </div>
            </div>

            {/* Time-off Items Table - Collapsible */}
            {expandedSections.timeOff && (
              <div className="mt-4">
                <div className="flex justify-between items-center mb-3">
                  <h4 className="text-custom-grey-900 font-medium text-sm">
                    Time-off Items
                  </h4>
                  <button
                    type="button"
                    onClick={addTimeOffItem}
                    className="flex items-center gap-1 text-custom-base-green text-sm hover:text-custom-grey-800"
                  >
                    <Plus className="w-4 h-4" />
                    Add Item
                  </button>
                </div>
                <table className="w-full">
                  <thead>
                    <tr className="bg-custom-grey-100">
                      <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                        Type
                      </th>
                      <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                        Days Used
                      </th>
                      <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                        Days Remaining
                      </th>
                      <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                        Amount
                      </th>
                      <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {form.watch('timeOff.items')?.map((_, index) => (
                      <tr
                        key={index}
                        className="border-b border-custom-grey-200"
                      >
                        <td className="p-3">
                          <FormField
                            control={form.control}
                            name={`timeOff.items.${index}.type`}
                            render={({ field }) => (
                              <FormItem>
                                <FormControl>
                                  <Input
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
                            name={`timeOff.items.${index}.daysUsed`}
                            render={({ field }) => (
                              <FormItem>
                                <FormControl>
                                  <Input
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
                            name={`timeOff.items.${index}.daysRemaining`}
                            render={({ field }) => (
                              <FormItem>
                                <FormControl>
                                  <Input
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
                            name={`timeOff.items.${index}.amount`}
                            render={({ field }) => (
                              <FormItem>
                                <FormControl>
                                  <Input
                                    {...field}
                                    onChange={(e) => {
                                      field.onChange(e)
                                      setTimeout(calculateTimeOffTotal, 100)
                                    }}
                                    className="border-0 shadow-none h-8 text-custom-grey-900 w-full focus-visible:ring-0 focus-visible:border-custom-base-green"
                                  />
                                </FormControl>
                                <FormMessage />
                              </FormItem>
                            )}
                          />
                        </td>
                        <td className="p-3">
                          <button
                            type="button"
                            onClick={() => removeTimeOffItem(index)}
                            className="text-red-500 hover:text-red-700"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Overtime Section */}
          <div className="py-5 px-6 flex flex-col gap-3 space-y-4 mt-6 border border-custom-grey-200 rounded-2xl">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <Label className="text-custom-grey-900 font-semibold text-[16px]">
                  Overtime
                </Label>
                <Tooltip>
                  <TooltipTrigger>
                    <HelpCircle className="w-4 h-4 text-custom-grey-400 hover:text-custom-grey-600" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p className="max-w-xs">
                      Extra hours worked beyond normal schedule, typically paid
                      at 1.5x or 2x the regular rate. Tracks date, hours, rate,
                      and calculated amount for each overtime instance.
                    </p>
                  </TooltipContent>
                </Tooltip>
              </div>
              <div className="flex gap-2 items-center">
                <FormField
                  control={form.control}
                  name="overtime.amount"
                  render={({ field }) => (
                    <FormItem>
                      <FormControl>
                        <Input
                          {...field}
                          className="border-0 shadow-none h-8 text-custom-grey-900 w-16 focus-visible:ring-0 focus-visible:border-custom-base-green"
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <button
                  type="button"
                  onClick={() => toggleSection('overtime')}
                  className="p-1 hover:bg-custom-grey-100 rounded"
                >
                  {expandedSections.overtime ? (
                    <ChevronUp className="w-5 h-4 text-custom-grey-600" />
                  ) : (
                    <ChevronDown className="w-5 h-4 text-custom-grey-600" />
                  )}
                </button>
              </div>
            </div>

            {/* Overtime Items Table - Collapsible */}
            {expandedSections.overtime && (
              <div className="mt-4">
                <div className="flex justify-between items-center mb-3">
                  <h4 className="text-custom-grey-900 font-medium text-sm">
                    Overtime Items
                  </h4>
                  <button
                    type="button"
                    onClick={addOvertimeItem}
                    className="flex items-center gap-1 text-custom-base-green text-sm hover:text-custom-grey-800"
                  >
                    <Plus className="w-4 h-4" />
                    Add Item
                  </button>
                </div>
                <table className="w-full">
                  <thead>
                    <tr className="bg-custom-grey-100">
                      <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                        Date
                      </th>
                      <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                        Hours
                      </th>
                      <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                        Rate
                      </th>
                      <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                        Amount
                      </th>
                      <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {form.watch('overtime.items')?.map((_, index) => (
                      <tr
                        key={index}
                        className="border-b border-custom-grey-200"
                      >
                        <td className="p-3">
                          <FormField
                            control={form.control}
                            name={`overtime.items.${index}.date`}
                            render={({ field }) => (
                              <FormItem>
                                <FormControl>
                                  <Input
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
                            name={`overtime.items.${index}.hours`}
                            render={({ field }) => (
                              <FormItem>
                                <FormControl>
                                  <Input
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
                            name={`overtime.items.${index}.rate`}
                            render={({ field }) => (
                              <FormItem>
                                <FormControl>
                                  <Input
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
                            name={`overtime.items.${index}.amount`}
                            render={({ field }) => (
                              <FormItem>
                                <FormControl>
                                  <Input
                                    {...field}
                                    onChange={(e) => {
                                      field.onChange(e)
                                      setTimeout(calculateOvertimeTotal, 100)
                                    }}
                                    className="border-0 shadow-none h-8 text-custom-grey-900 w-full focus-visible:ring-0 focus-visible:border-custom-base-green"
                                  />
                                </FormControl>
                                <FormMessage />
                              </FormItem>
                            )}
                          />
                        </td>
                        <td className="p-3">
                          <button
                            type="button"
                            onClick={() => removeOvertimeItem(index)}
                            className="text-red-500 hover:text-red-700"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Deficit Section */}
          <div className="py-5 px-6 flex flex-col gap-3 space-y-4 mt-6 border border-custom-grey-200 rounded-2xl">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <Label className="text-custom-grey-900 font-semibold text-[16px]">
                  Deficit
                </Label>
                <Tooltip>
                  <TooltipTrigger>
                    <HelpCircle className="w-4 h-4 text-custom-grey-400 hover:text-custom-grey-600" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p className="max-w-xs">
                      Shortfalls or negative balances like time deficits
                      (working fewer hours than required), performance issues,
                      or attendance problems that result in deductions.
                    </p>
                  </TooltipContent>
                </Tooltip>
              </div>
              <div className="flex gap-2 items-center">
                <FormField
                  control={form.control}
                  name="deficit.totalAmount"
                  render={({ field }) => (
                    <FormItem>
                      <FormControl>
                        <Input
                          {...field}
                          className="border-0 shadow-none h-8 text-custom-grey-900 w-20 focus-visible:ring-0 focus-visible:border-custom-base-green"
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <button
                  type="button"
                  onClick={() => toggleSection('deficit')}
                  className="p-1 hover:bg-custom-grey-100 rounded"
                >
                  {expandedSections.deficit ? (
                    <ChevronUp className="w-5 h-4 text-custom-grey-600" />
                  ) : (
                    <ChevronDown className="w-5 h-4 text-custom-grey-600" />
                  )}
                </button>
              </div>
            </div>

            {/* Deficit Table - Collapsible */}
            {expandedSections.deficit && (
              <div className="mt-4">
                <div className="flex justify-between items-center mb-3">
                  <h4 className="text-custom-grey-900 font-medium text-sm">
                    Deficit Entries
                  </h4>
                  <button
                    type="button"
                    onClick={() => {
                      const currentEntries =
                        form.getValues('deficit.entries') || []
                      form.setValue('deficit.entries', [
                        ...currentEntries,
                        { deficit: '', type: '', amount: '' },
                      ])
                    }}
                    className="flex items-center gap-1 text-custom-base-green text-sm hover:text-custom-grey-800"
                  >
                    <Plus className="w-4 h-4" />
                    Add Entry
                  </button>
                </div>
                <table className="w-full">
                  <thead>
                    <tr className="bg-custom-grey-100">
                      <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                        Deficit
                      </th>
                      <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                        Type
                      </th>
                      <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                        Amount
                      </th>
                      <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {form.watch('deficit.entries')?.map((_, index) => (
                      <tr
                        key={index}
                        className="border-b border-custom-grey-200"
                      >
                        <td className="p-3">
                          <FormField
                            control={form.control}
                            name={`deficit.entries.${index}.deficit`}
                            render={({ field }) => (
                              <FormItem>
                                <FormControl>
                                  <Input
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
                            name={`deficit.entries.${index}.type`}
                            render={({ field }) => (
                              <FormItem>
                                <FormControl>
                                  <Input
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
                            name={`deficit.entries.${index}.amount`}
                            render={({ field }) => (
                              <FormItem>
                                <FormControl>
                                  <Input
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
                          <button
                            type="button"
                            onClick={() => {
                              const currentEntries =
                                form.getValues('deficit.entries') || []
                              form.setValue(
                                'deficit.entries',
                                currentEntries.filter((_, i) => i !== index),
                              )
                            }}
                            className="text-red-500 hover:text-red-700"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Attendance Section */}
          <div className="py-5 px-6 flex flex-col gap-3 space-y-4 mt-6 border border-custom-grey-200 rounded-2xl">
            <div className="flex justify-between items-center">
              <Label className="text-custom-grey-900 font-semibold text-[16px]">
                Attendance
              </Label>
              <div className="flex gap-2 items-center">
                <FormField
                  control={form.control}
                  name="attendance.totalHours"
                  render={({ field }) => (
                    <FormItem>
                      <FormControl>
                        <Input
                          {...field}
                          className="border-0 shadow-none h-8 text-custom-grey-900 w-20 focus-visible:ring-0 focus-visible:border-custom-base-green"
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <button
                  type="button"
                  onClick={() => toggleSection('attendance')}
                  className="p-1 hover:bg-custom-grey-100 rounded"
                >
                  {expandedSections.attendance ? (
                    <ChevronUp className="w-5 h-4 text-custom-grey-600" />
                  ) : (
                    <ChevronDown className="w-5 h-4 text-custom-grey-600" />
                  )}
                </button>
              </div>
            </div>

            {/* Attendance Table - Collapsible */}
            {expandedSections.attendance && (
              <div className="mt-4">
                <div className="flex justify-between items-center mb-3">
                  <h4 className="text-custom-grey-900 font-medium text-sm">
                    Attendance Entries
                  </h4>
                  <button
                    type="button"
                    onClick={() => {
                      const currentEntries =
                        form.getValues('attendance.entries') || []
                      form.setValue('attendance.entries', [
                        ...currentEntries,
                        { period: '', actualWorkHours: '' },
                      ])
                    }}
                    className="flex items-center gap-1 text-custom-base-green text-sm hover:text-custom-grey-800"
                  >
                    <Plus className="w-4 h-4" />
                    Add Entry
                  </button>
                </div>
                <table className="w-full">
                  <thead>
                    <tr className="bg-custom-grey-100">
                      <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                        Period
                      </th>
                      <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                        Actual Work Hours
                      </th>
                      <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {form.watch('attendance.entries')?.map((_, index) => (
                      <tr
                        key={index}
                        className="border-b border-custom-grey-200"
                      >
                        <td className="p-3">
                          <FormField
                            control={form.control}
                            name={`attendance.entries.${index}.period`}
                            render={({ field }) => (
                              <FormItem>
                                <FormControl>
                                  <Input
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
                            name={`attendance.entries.${index}.actualWorkHours`}
                            render={({ field }) => (
                              <FormItem>
                                <FormControl>
                                  <Input
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
                          <button
                            type="button"
                            onClick={() => {
                              const currentEntries =
                                form.getValues('attendance.entries') || []
                              form.setValue(
                                'attendance.entries',
                                currentEntries.filter((_, i) => i !== index),
                              )
                            }}
                            className="text-red-500 hover:text-red-700"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Carry Over of Overtime Section */}
          <div className="py-5 px-6 flex flex-col gap-3 space-y-4 mt-6 border border-custom-grey-200 rounded-2xl">
            <div className="flex justify-between items-center">
              <Label className="text-custom-grey-900 font-semibold text-[16px]">
                Carry Over of Overtime
              </Label>
              <div className="flex gap-2 items-center">
                <FormField
                  control={form.control}
                  name="carryOverOvertime"
                  render={({ field }) => (
                    <FormItem>
                      <FormControl>
                        <Input
                          {...field}
                          className="border-0 shadow-none h-8 text-custom-grey-900 w-16 focus-visible:ring-0 focus-visible:border-custom-base-green"
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <button
                  type="button"
                  onClick={() => toggleSection('carryOverOvertime')}
                  className="p-1 hover:bg-custom-grey-100 rounded"
                >
                  {expandedSections.carryOverOvertime ? (
                    <ChevronUp className="w-5 h-4 text-custom-grey-600" />
                  ) : (
                    <ChevronDown className="w-5 h-4 text-custom-grey-600" />
                  )}
                </button>
              </div>
            </div>

            {/* Carry Over of Overtime Details - Collapsible */}
            {expandedSections.carryOverOvertime && (
              <div className="mt-4">
                <div className="bg-custom-grey-50 p-4 rounded-lg">
                  <h4 className="text-custom-grey-900 font-medium text-sm mb-3">
                    Overtime Carry Over Details
                  </h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label className="text-custom-grey-600 text-xs">
                        Previous Period Overtime
                      </Label>
                      <div className="text-custom-grey-900 text-sm font-medium">
                        8.5 hours
                      </div>
                    </div>
                    <div>
                      <Label className="text-custom-grey-600 text-xs">
                        Used This Period
                      </Label>
                      <div className="text-custom-grey-900 text-sm font-medium">
                        2.0 hours
                      </div>
                    </div>
                    <div>
                      <Label className="text-custom-grey-600 text-xs">
                        Remaining Balance
                      </Label>
                      <div className="text-custom-grey-900 text-sm font-medium">
                        6.5 hours
                      </div>
                    </div>
                    <div>
                      <Label className="text-custom-grey-600 text-xs">
                        Expiry Date
                      </Label>
                      <div className="text-custom-grey-900 text-sm font-medium">
                        Dec 31, 2024
                      </div>
                    </div>
                  </div>
                  <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
                    <p className="text-yellow-800 text-xs">
                      <strong>Note:</strong> Unused overtime hours will expire
                      at the end of the year. Please use remaining hours before
                      the expiry date.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Dependents Section */}
          <div className="py-5 px-6 flex flex-col gap-3 space-y-4 mt-6 border border-custom-grey-200 rounded-2xl">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <Label className="text-custom-grey-900 font-semibold text-[16px]">
                  Dependents
                </Label>
                <Tooltip>
                  <TooltipTrigger>
                    <HelpCircle className="w-4 h-4 text-custom-grey-400 hover:text-custom-grey-600" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p className="max-w-xs">
                      Family members (spouse, children, parents) that qualify
                      for tax benefits. Each dependent can reduce taxable income
                      and provide tax savings.
                    </p>
                  </TooltipContent>
                </Tooltip>
              </div>
              <div className="flex gap-2 items-center">
                <FormField
                  control={form.control}
                  name="dependents.count"
                  render={({ field }) => (
                    <FormItem>
                      <Select
                        onValueChange={field.onChange}
                        defaultValue={field.value}
                      >
                        <FormControl>
                          <SelectTrigger className="border-0 shadow-none h-8 w-32 focus-visible:ring-0 focus-visible:border-custom-base-green">
                            <SelectValue placeholder="0 Dependents" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="0">0 Dependents</SelectItem>
                          <SelectItem value="1">1 Dependent</SelectItem>
                          <SelectItem value="2">2 Dependents</SelectItem>
                          <SelectItem value="3">3 Dependents</SelectItem>
                          <SelectItem value="4">4 Dependents</SelectItem>
                          <SelectItem value="5+">5+ Dependents</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <button
                  type="button"
                  onClick={() => toggleSection('dependents')}
                  className="p-1 hover:bg-custom-grey-100 rounded"
                >
                  {expandedSections.dependents ? (
                    <ChevronUp className="w-5 h-4 text-custom-grey-600" />
                  ) : (
                    <ChevronDown className="w-5 h-4 text-custom-grey-600" />
                  )}
                </button>
              </div>
            </div>

            {/* Dependents Details Table - Collapsible */}
            {expandedSections.dependents && (
              <div className="mt-4">
                <div className="flex justify-between items-center mb-3">
                  <h4 className="text-custom-grey-900 font-medium text-sm">
                    Dependent Details
                  </h4>
                  <button
                    type="button"
                    onClick={addDependentItem}
                    className="flex items-center gap-1 text-custom-base-green text-sm hover:text-custom-grey-800"
                  >
                    <Plus className="w-4 h-4" />
                    Add Dependent
                  </button>
                </div>
                <table className="w-full">
                  <thead>
                    <tr className="bg-custom-grey-100">
                      <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                        Name
                      </th>
                      <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                        Relationship
                      </th>
                      <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                        Date of Birth
                      </th>
                      <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                        Tax Benefit
                      </th>
                      <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {form.watch('dependents.items')?.map((_, index) => (
                      <tr
                        key={index}
                        className="border-b border-custom-grey-200"
                      >
                        <td className="p-3">
                          <FormField
                            control={form.control}
                            name={`dependents.items.${index}.name`}
                            render={({ field }) => (
                              <FormItem>
                                <FormControl>
                                  <Input
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
                            name={`dependents.items.${index}.relationship`}
                            render={({ field }) => (
                              <FormItem>
                                <FormControl>
                                  <Input
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
                            name={`dependents.items.${index}.dateOfBirth`}
                            render={({ field }) => (
                              <FormItem>
                                <FormControl>
                                  <Input
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
                            name={`dependents.items.${index}.taxBenefit`}
                            render={({ field }) => (
                              <FormItem>
                                <FormControl>
                                  <Input
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
                          <button
                            type="button"
                            onClick={() => removeDependentItem(index)}
                            className="text-red-500 hover:text-red-700"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Offset Sections */}
          {form.watch('offset').map((_, index) => (
            <div
              key={index}
              className="h-[75px] py-5 px-6 flex flex-col gap-3 space-y-4 mt-6 border border-custom-grey-200 rounded-3xl"
            >
              <div className="flex justify-between items-center">
                <Label className="text-custom-grey-900 font-semibold text-[16px]">
                  Offset
                </Label>
                <div className="flex gap-2">
                  <FormField
                    control={form.control}
                    name={`offset.${index}.amount`}
                    render={({ field }) => (
                      <FormItem>
                        <FormControl>
                          <Input
                            placeholder="Amount"
                            {...field}
                            className="border-0 shadow-none h-8 text-custom-grey-900 w-24 focus-visible:ring-0 focus-visible:border-custom-base-green"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name={`offset.${index}.currency`}
                    render={({ field }) => (
                      <FormItem>
                        <FormControl>
                          <Select
                            onValueChange={field.onChange}
                            defaultValue={field.value}
                          >
                            <SelectTrigger className="border-0 shadow-none h-8 w-16 focus-visible:ring-0 focus-visible:border-custom-base-green">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="USD">USD</SelectItem>
                              <SelectItem value="EUR">EUR</SelectItem>
                              <SelectItem value="GBP">GBP</SelectItem>
                            </SelectContent>
                          </Select>
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  {form.watch('offset').length > 1 && (
                    <Button
                      type="button"
                      onClick={() => removeOffset(index)}
                      className="bg-red-500 text-white h-6 w-6 p-0 rounded-full"
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  )}
                </div>
              </div>
            </div>
          ))}

          {/* Add Offset Button */}
          <div className="flex justify-end mt-4">
            <Button
              type="button"
              onClick={addOffset}
              className="bg-custom-base-green text-white h-8 px-4 rounded-full"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Offset
            </Button>
          </div>

          {/* Bank Information Section */}
          <div className="flex flex-col gap-3 space-y-4 mt-6 p-6 border border-custom-grey-200 rounded-2xl">
            <div className="grid grid-cols-2 gap-6">
              {/* Left Column */}
              <div className="flex flex-col gap-4">
                <div className="flex flex-row gap-2 w-full">
                  <Label className="text-custom-grey-600 text-[14px] w-[120px]">
                    Bank Name
                  </Label>
                  <FormField
                    control={form.control}
                    name="bankInfo.bankName"
                    render={({ field }) => (
                      <FormItem className="w-full">
                        <FormControl>
                          <Input
                            {...field}
                            className="border-0 shadow-none h-8 text-custom-grey-900 w-full focus-visible:ring-0 focus-visible:border-custom-base-green"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
                <div className="flex flex-row gap-2 w-full">
                  <Label className="text-custom-grey-600 text-[14px] w-[120px]">
                    Branch
                  </Label>
                  <FormField
                    control={form.control}
                    name="bankInfo.branch"
                    render={({ field }) => (
                      <FormItem className="w-full">
                        <FormControl>
                          <Input
                            {...field}
                            className="border-0 shadow-none h-8 text-custom-grey-900 w-full focus-visible:ring-0 focus-visible:border-custom-base-green"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
                <div className="flex flex-row gap-2 w-full">
                  <Label className="text-custom-grey-600 text-[14px] w-[120px]">
                    SWIFT/BIC
                  </Label>
                  <FormField
                    control={form.control}
                    name="bankInfo.swiftBic"
                    render={({ field }) => (
                      <FormItem className="w-full">
                        <FormControl>
                          <Input
                            {...field}
                            className="border-0 shadow-none h-8 text-custom-grey-900 w-full focus-visible:ring-0 focus-visible:border-custom-base-green"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
              </div>

              {/* Right Column */}
              <div className="flex flex-col gap-4">
                <div className="flex flex-row gap-2 w-full">
                  <Label className="text-custom-grey-600 text-[14px] w-[120px]">
                    Account Name
                  </Label>
                  <FormField
                    control={form.control}
                    name="bankInfo.accountName"
                    render={({ field }) => (
                      <FormItem className="w-full">
                        <FormControl>
                          <Input
                            {...field}
                            className="border-0 shadow-none h-8 text-custom-grey-900 w-full focus-visible:ring-0 focus-visible:border-custom-base-green"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
                <div className="flex flex-row gap-2 w-full">
                  <Label className="text-custom-grey-600 text-[14px] w-[120px]">
                    Account Number
                  </Label>
                  <FormField
                    control={form.control}
                    name="bankInfo.accountNumber"
                    render={({ field }) => (
                      <FormItem className="w-full">
                        <FormControl>
                          <Input
                            {...field}
                            className="border-0 shadow-none h-8 text-custom-grey-900 w-full focus-visible:ring-0 focus-visible:border-custom-base-green"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
                <div className="flex flex-row gap-2 w-full">
                  <Label className="text-custom-grey-600 text-[14px] w-[120px]">
                    IBAN
                  </Label>
                  <FormField
                    control={form.control}
                    name="bankInfo.iban"
                    render={({ field }) => (
                      <FormItem className="w-full">
                        <FormControl>
                          <Input
                            {...field}
                            className="border-0 shadow-none h-8 text-custom-grey-900 w-full focus-visible:ring-0 focus-visible:border-custom-base-green"
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

          <Button
            type="submit"
            onClick={() => form.handleSubmit(onSubmit)}
            className="bg-custom-grey-900 text-white cursor-pointer w-full mt-10"
          >
            Submit
          </Button>
        </form>
      </Form>
    </TooltipProvider>
  )
}
