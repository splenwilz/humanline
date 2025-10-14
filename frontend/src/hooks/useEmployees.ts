'use client'

import useSWR from 'swr'
import useSWRMutation from 'swr/mutation'
import { mutate } from 'swr'
import {
  employeeApi,
} from '@/data/api/employees'
import type { EmployeeDetails } from '@/components/table/EmployeeColumns'
import { createCacheKey } from '@/lib/swr-config'
import { toast } from 'sonner'
import type { CreateEmployeeRequest, Employees } from '@/types/employees'

// Mutation fetchers
async function createEmployeeFetcher(
  _: string,
  { arg }: { arg: CreateEmployeeRequest },
) {
  return employeeApi.create(arg)
}

// async function updateEmployeeFetcher(
//   _: string,
//   { arg }: { arg: { id: number; data: Partial<UpdateEmployeeRequest> } },
// ) {
//   return employeeApi.update(arg.id, arg.data)
// }

async function deleteEmployeeFetcher(
  _: string,
  { arg }: { arg: { id: number } },
) {
  return employeeApi.delete(arg.id)
}

// Transform Employee to EmployeeDetails for table compatibility
function transformEmployeeToTableFormat(employee: Employees): EmployeeDetails {
  return {
    id: employee.id.toString(),
    name: `${employee.first_name} ${employee.last_name}`,
    email: employee.email,
    job_title: employee.job_title || '',
    department: employee.department || '',
    office: employee.office || '',
    employment_status: String(employee.employment_status).toUpperCase(),
    account: employee.email, // Using email as account for now
  }
}

// Hook to get all employees
export const useEmployees = () => {
  const {
    data: employees,
    error,
    isLoading,
    mutate: refetch,
  } = useSWR(createCacheKey.employees(), () => employeeApi.getAll(), {
    revalidateOnFocus: false,
    revalidateOnReconnect: true,
  })

  return {
    employees: employees ? employees.map(transformEmployeeToTableFormat) : [],
    loading: isLoading,
    error: error?.message || null,
    refetch,
  }
}

// Hook to get employee by ID
export const useEmployee = (id: number | null) => {
  const {
    data: employee,
    error,
    isLoading,
    mutate: refetch,
  } = useSWR(
    id ? createCacheKey.employee(id.toString()) : null,
    id ? () => employeeApi.getById(id) : null,
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
    },
  )

  return {
    employee,
    loading: isLoading,
    error: error?.message || null,
    refetch,
  }
}


// Hook to create employee
export const useCreateEmployee = () => {
  const { trigger, data, error, isMutating } = useSWRMutation(
    '/employees',
    createEmployeeFetcher,
  )

  const createEmployee = async (employeeData: CreateEmployeeRequest) => {
    try {
      const newEmployee = await trigger(employeeData)

      // Optimistically add the new employee to the cache
      await mutate(
        createCacheKey.employees(),
        (currentData: Employees[] | undefined) => {
          if (!currentData) return [newEmployee]
          return [...currentData, newEmployee]
        },
        { revalidate: false }
      )

      // Only invalidate stats, not the main list (already updated optimistically)
      await mutate(createCacheKey.employeeStats(), undefined, { revalidate: true })

      toast.success('Employee created successfully!')
      return { success: true, data: newEmployee }
    } catch (error: unknown) {
      // Revert optimistic update on error
      await mutate(createCacheKey.employees(), undefined, { revalidate: true })
      
      const errorMessage = error instanceof Error ? error.message : 'Failed to create employee'
      toast.error(errorMessage)
      throw error
    }
  }

  return {
    createEmployee,
    data,
    error,
    isLoading: isMutating,
  }
}

// Hook to update employee
// export const useUpdateEmployee = () => {
//   const { trigger, data, error, isMutating } = useSWRMutation(
//     '/employees/update',
//     updateEmployeeFetcher,
//   )

//   const updateEmployee = async (
//     id: number,
//     employeeData: Partial<UpdateEmployeeRequest>,
//   ) => {
//     try {
//       const updatedEmployee = await trigger({ id, data: employeeData })

//       // Invalidate specific employee and related caches
//       const keysToInvalidate = invalidateCache.employee(id.toString())
//       await Promise.all(
//         keysToInvalidate.map((key) =>
//           mutate(key, undefined, { revalidate: true }),
//         ),
//       )

//       toast.success('Employee updated successfully!')
//       return { success: true, data: updatedEmployee }
//     } catch (error: unknown) {
//       const errorMessage = error instanceof Error ? error.message : 'Failed to update employee'
//       toast.error(errorMessage)
//       throw error
//     }
//   }

//   return {
//     updateEmployee,
//     data,
//     error,
//     isLoading: isMutating,
//   }
// }

// Hook to delete employee
export const useDeleteEmployee = () => {
  const { trigger, data, error, isMutating } = useSWRMutation(
    '/employees/delete',
    deleteEmployeeFetcher,
  )

  const deleteEmployee = async (id: number) => {
    try {
      // Optimistically remove the employee from the cache
      await mutate(
        createCacheKey.employees(),
        (currentData: Employees[] | undefined) => {
          if (!currentData) return currentData
          return currentData.filter(employee => employee.id !== id)
        },
        { revalidate: false }
      )

      // Perform the actual delete
      await trigger({ id })

      // Only invalidate stats, not the main list (already updated optimistically)
      await mutate(createCacheKey.employeeStats(), undefined, { revalidate: true })

      toast.success('Employee deleted successfully!')
      return { success: true }
    } catch (error: unknown) {
      // Revert optimistic update on error
      await mutate(createCacheKey.employees(), undefined, { revalidate: true })
      
      const errorMessage = error instanceof Error ? error.message : 'Failed to delete employee'
      toast.error(errorMessage)
      throw error
    }
  }

  return {
    deleteEmployee,
    data,
    error,
    isLoading: isMutating,
  }
}
