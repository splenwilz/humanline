'use client'

import { useState, useEffect } from 'react'
import { employeeApi, type EmployeeDetails } from '@/data/demo'
import { type EmployeeDetails as ColumnEmployeeDetails } from '@/components/table/column'

interface UseEmployeesReturn {
  employees: ColumnEmployeeDetails[]
  loading: boolean
  error: string | null
  refetch: () => Promise<void>
}

interface UseEmployeeSearchReturn {
  employees: ColumnEmployeeDetails[]
  loading: boolean
  error: string | null
  search: (query: string) => Promise<void>
}

interface UseEmployeeStatsReturn {
  stats: {
    total: number
    byStatus: Record<string, number>
    byDepartment: Record<string, number>
    byOffice: Record<string, number>
  } | null
  loading: boolean
  error: string | null
  refetch: () => Promise<void>
}

// Hook to get all employees
export const useEmployees = (): UseEmployeesReturn => {
  const [employees, setEmployees] = useState<ColumnEmployeeDetails[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchEmployees = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await employeeApi.getAll()
      setEmployees(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch employees')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchEmployees()
  }, [])

  return {
    employees,
    loading,
    error,
    refetch: fetchEmployees,
  }
}

// Hook to search employees
export const useEmployeeSearch = (): UseEmployeeSearchReturn => {
  const [employees, setEmployees] = useState<EmployeeDetails[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const search = async (query: string) => {
    if (!query.trim()) {
      setEmployees([])
      return
    }

    try {
      setLoading(true)
      setError(null)
      const data = await employeeApi.search(query)
      setEmployees(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed')
    } finally {
      setLoading(false)
    }
  }

  return {
    employees,
    loading,
    error,
    search,
  }
}

// Hook to get employee statistics
export const useEmployeeStats = (): UseEmployeeStatsReturn => {
  const [stats, setStats] = useState<UseEmployeeStatsReturn['stats']>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchStats = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await employeeApi.getStats()
      setStats(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch stats')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStats()
  }, [])

  return {
    stats,
    loading,
    error,
    refetch: fetchStats,
  }
}

// Hook to get employees by department
export const useEmployeesByDepartment = (department: string) => {
  const [employees, setEmployees] = useState<EmployeeDetails[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchByDepartment = async (dept: string) => {
    try {
      setLoading(true)
      setError(null)
      const data = await employeeApi.getByDepartment(dept)
      setEmployees(data)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Failed to fetch employees by department',
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (department) {
      fetchByDepartment(department)
    }
  }, [department])

  return {
    employees,
    loading,
    error,
    refetch: () => fetchByDepartment(department),
  }
}

// Hook to get employees by status
export const useEmployeesByStatus = (status: string) => {
  const [employees, setEmployees] = useState<EmployeeDetails[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchByStatus = async (empStatus: string) => {
    try {
      setLoading(true)
      setError(null)
      const data = await employeeApi.getByStatus(empStatus)
      setEmployees(data)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Failed to fetch employees by status',
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (status) {
      fetchByStatus(status)
    }
  }, [status])

  return {
    employees,
    loading,
    error,
    refetch: () => fetchByStatus(status),
  }
}
