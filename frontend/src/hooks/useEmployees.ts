'use client'

import useSWR from 'swr'
import useSWRMutation from 'swr/mutation'
import { mutate } from 'swr'
import { employeeApi, type Employee, type EmployeeStats, type CreateEmployeeRequest, type UpdateEmployeeRequest } from '@/data/api/employees'
import { type EmployeeDetails } from '@/components/table/column'
import { createCacheKey, invalidateCache } from '@/lib/swr-config'
import { toast } from 'sonner'

// Mutation fetchers
async function createEmployeeFetcher(_: string, { arg }: { arg: CreateEmployeeRequest }) {
  return employeeApi.create(arg)
}

async function updateEmployeeFetcher(_: string, { arg }: { arg: { id: string; data: Partial<UpdateEmployeeRequest> } }) {
  return employeeApi.update(arg.id, arg.data)
}

async function deleteEmployeeFetcher(_: string, { arg }: { arg: { id: string } }) {
  return employeeApi.delete(arg.id)
}

// Transform Employee to EmployeeDetails for table compatibility
function transformEmployeeToTableFormat(employee: Employee): EmployeeDetails {
  return {
    id: employee.id,
    name: `${employee.first_name} ${employee.last_name}`,
    email: employee.email,
    job_title: employee.job_title,
    line_manager: '', // Will need to be populated from manager_id lookup
    department: employee.department,
    office: employee.office,
    employement_status: employee.employment_status.toUpperCase(),
    account: employee.email, // Using email as account for now
  }
}

// Hook to get all employees
export const useEmployees = () => {
  const {
    data: employees,
    error,
    isLoading,
    mutate: refetch
  } = useSWR(
    createCacheKey.employees(),
    () => employeeApi.getAll(),
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
    }
  )

  return {
    employees: employees ? employees.map(transformEmployeeToTableFormat) : [],
    loading: isLoading,
    error: error?.message || null,
    refetch,
  }
}

// Hook to get employee by ID
export const useEmployee = (id: string | null) => {
  const {
    data: employee,
    error,
    isLoading,
    mutate: refetch
  } = useSWR(
    id ? createCacheKey.employee(id) : null,
    id ? () => employeeApi.getById(id) : null,
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
    }
  )

  return {
    employee,
    loading: isLoading,
    error: error?.message || null,
    refetch,
  }
}

// Hook to search employees
export const useEmployeeSearch = () => {
  const {
    data: employees,
    error,
    isLoading,
    mutate: performSearch
  } = useSWR(
    null, // Will be set dynamically
    null,
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
    }
  )

  const search = async (query: string) => {
    if (!query.trim()) {
      await performSearch([], false)
      return
    }

    try {
      const cacheKey = createCacheKey.employeeSearch(query)
      const results = await mutate(cacheKey, () => employeeApi.search(query))
      const transformedResults = results ? results.map(transformEmployeeToTableFormat) : []
      await performSearch(transformedResults, false)
    } catch (error: any) {
      console.error('Employee search error:', error)
      toast.error('Search failed. Please try again.')
    }
  }

  return {
    employees: employees ? employees.map(transformEmployeeToTableFormat) : [],
    loading: isLoading,
    error: error?.message || null,
    search,
  }
}

// Hook to get employee statistics
export const useEmployeeStats = () => {
  const {
    data: stats,
    error,
    isLoading,
    mutate: refetch
  } = useSWR(
    createCacheKey.employeeStats(),
    () => employeeApi.getStats(),
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
    }
  )

  return {
    stats,
    loading: isLoading,
    error: error?.message || null,
    refetch,
  }
}

// Hook to get employees by department
export const useEmployeesByDepartment = (department: string | null) => {
  const {
    data: employees,
    error,
    isLoading,
    mutate: refetch
  } = useSWR(
    department ? createCacheKey.employeesByDepartment(department) : null,
    department ? () => employeeApi.getByDepartment(department) : null,
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
    }
  )

  return {
    employees: employees ? employees.map(transformEmployeeToTableFormat) : [],
    loading: isLoading,
    error: error?.message || null,
    refetch,
  }
}

// Hook to get employees by status
export const useEmployeesByStatus = (status: string | null) => {
  const {
    data: employees,
    error,
    isLoading,
    mutate: refetch
  } = useSWR(
    status ? createCacheKey.employeesByStatus(status) : null,
    status ? () => employeeApi.getByStatus(status) : null,
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
    }
  )

  return {
    employees: employees ? employees.map(transformEmployeeToTableFormat) : [],
    loading: isLoading,
    error: error?.message || null,
    refetch,
  }
}

// Hook to create employee
export const useCreateEmployee = () => {
  const { trigger, data, error, isMutating } = useSWRMutation('/employees', createEmployeeFetcher)

  const createEmployee = async (employeeData: CreateEmployeeRequest) => {
    try {
      const newEmployee = await trigger(employeeData)
      
      // Invalidate employee caches
      await mutate(
        key => typeof key === 'string' && key.startsWith('/employees'),
        undefined,
        { revalidate: true }
      )

      toast.success('Employee created successfully!')
      return { success: true, data: newEmployee }
    } catch (error: any) {
      const errorMessage = error?.message || 'Failed to create employee'
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
export const useUpdateEmployee = () => {
  const { trigger, data, error, isMutating } = useSWRMutation('/employees/update', updateEmployeeFetcher)

  const updateEmployee = async (id: string, employeeData: Partial<UpdateEmployeeRequest>) => {
    try {
      const updatedEmployee = await trigger({ id, data: employeeData })
      
      // Invalidate specific employee and related caches
      const keysToInvalidate = invalidateCache.employee(id)
      await Promise.all(
        keysToInvalidate.map(key => 
          typeof key === 'function' 
            ? mutate(key, undefined, { revalidate: true })
            : mutate(key, undefined, { revalidate: true })
        )
      )

      toast.success('Employee updated successfully!')
      return { success: true, data: updatedEmployee }
    } catch (error: any) {
      const errorMessage = error?.message || 'Failed to update employee'
      toast.error(errorMessage)
      throw error
    }
  }

  return {
    updateEmployee,
    data,
    error,
    isLoading: isMutating,
  }
}

// Hook to delete employee
export const useDeleteEmployee = () => {
  const { trigger, data, error, isMutating } = useSWRMutation('/employees/delete', deleteEmployeeFetcher)

  const deleteEmployee = async (id: string) => {
    try {
      await trigger({ id })
      
      // Invalidate employee caches
      await mutate(
        key => typeof key === 'string' && key.startsWith('/employees'),
        undefined,
        { revalidate: true }
      )

      toast.success('Employee deleted successfully!')
      return { success: true }
    } catch (error: any) {
      const errorMessage = error?.message || 'Failed to delete employee'
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