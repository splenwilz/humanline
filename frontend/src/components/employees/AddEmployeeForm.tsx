'use client'

import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

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
import { Button } from '@/components/ui/button'

const formSchema = z.object({
  first_name: z.string().min(2, {
    message: 'First Name must be at least 2 characters.',
  }),
  last_name: z.string().min(2, {
    message: 'Last Name must be at least 2 characters.',
  }),
  email: z.string().email({
    message: 'Invalid email address.',
  }),
  phone: z.string().min(10, {
    message: 'Phone number must be at least 10 characters.',
  }),
  join_date: z.string().min(1, {
    message: 'Join date is required.',
  }),
  employment_status: z.enum(['ACTIVE', 'INACTIVE', 'TERMINATED', 'ON_LEAVE', 'SUSPENDED'], {
    message: 'Please select a valid employment status.',
  }),
})

interface AddEmployeeFormProps {
  onSubmit: (data: z.infer<typeof formSchema>) => Promise<void>
  isLoading?: boolean
}

export function AddEmployeeForm({ onSubmit, isLoading = false }: AddEmployeeFormProps) {
  // 1. Define your form.
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      first_name: '',
      last_name: '',
      email: '',
      phone: '',
      join_date: '',
      employment_status: 'ACTIVE',
    },
  })

  // 2. Define a submit handler.
  async function handleSubmit(values: z.infer<typeof formSchema>) {
    try {
      await onSubmit(values)
      form.reset()
    } catch {
      // Error handling is done in the parent component
    }
  }
  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="first_name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>First Name</FormLabel>
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
              <FormLabel>Last Name</FormLabel>
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
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
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
              <FormLabel>Phone</FormLabel>
              <FormControl>
                <Input
                  placeholder="1234567890"
                  {...field}
                  className="h-11 rounded-[10px] focus-visible:ring-0 focus-visible:border-custom-base-green"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        {/* Join Date with Calender Input */}
        <FormField
          control={form.control}
          name="join_date"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Join Date</FormLabel>
              <FormControl>
                <div className="relative">
                  <Input
                    type="date"
                    placeholder="Select Join Date"
                    {...field}
                    className="h-11 rounded-[10px] focus-visible:ring-0 focus-visible:border-custom-base-green"
                  />
                </div>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        {/* Employment Status */}
        <FormField
          control={form.control}
          name="employment_status"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Employment Status</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger className="w-full h-11 rounded-[10px] focus-visible:ring-0 focus-visible:border-custom-base-green">
                    <SelectValue placeholder="Select employment status" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="ACTIVE">Active</SelectItem>
                  <SelectItem value="INACTIVE">Inactive</SelectItem>
                  <SelectItem value="TERMINATED">Terminated</SelectItem>
                  <SelectItem value="ON_LEAVE">On Leave</SelectItem>
                  <SelectItem value="SUSPENDED">Suspended</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button
          type="submit"
          disabled={isLoading}
          className="bg-custom-grey-900 text-white cursor-pointer disabled:opacity-50"
        >
          {isLoading ? 'Adding Employee...' : 'Add Employee'}
        </Button>
      </form>
    </Form>
  )
}
