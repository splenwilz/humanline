import { apiClient } from './client'

// Employee types
export interface Employee {
  id: number
  user_id: number
  first_name: string
  last_name: string
  email: string
  phone: string
  join_date: string
  created_at: string
  updated_at: string
  job_title: string | null
  department: string | null
  office: string | null
  line_manager_id: number | null
  line_manager_name: string | null
  employment_status: 'ACTIVE' | 'INACTIVE' | 'TERMINATED' | 'ON_LEAVE' | 'SUSPENDED'
}

export interface EmployeeStats {
  total: number
  byStatus: Record<string, number>
  byDepartment: Record<string, number>
  byOffice: Record<string, number>
}

export interface CreateEmployeeRequest extends Record<string, unknown> {
  first_name: string
  last_name: string
  email: string
  phone: string
  join_date: string
  employment_status?: 'ACTIVE' | 'INACTIVE' | 'TERMINATED' | 'ON_LEAVE' | 'SUSPENDED'
}

export interface UpdateEmployeeRequest extends Partial<CreateEmployeeRequest> {
  id: number
}

// Employee API functions
export const employeeApi = {
  // Get all employees
  async getAll(): Promise<Employee[]> {
    return apiClient.get<Employee[]>('/employees')
  },

  // Get employee by ID
  async getById(id: number): Promise<Employee> {
    return apiClient.get<Employee>(`/employees/${id}`)
  },

  // Search employees
  async search(query: string): Promise<Employee[]> {
    return apiClient.get<Employee[]>(
      `/employees/search?q=${encodeURIComponent(query)}`,
    )
  },

  // Get employees by department
  async getByDepartment(department: string): Promise<Employee[]> {
    return apiClient.get<Employee[]>(
      `/employees?department=${encodeURIComponent(department)}`,
    )
  },

  // Get employees by status
  async getByStatus(status: string): Promise<Employee[]> {
    return apiClient.get<Employee[]>(
      `/employees?status=${encodeURIComponent(status)}`,
    )
  },

  // Get employee statistics
  async getStats(): Promise<EmployeeStats> {
    return apiClient.get<EmployeeStats>('/employees/stats')
  },

  // Create new employee
  async create(data: CreateEmployeeRequest): Promise<Employee> {
    return apiClient.post<Employee>('/employees', data)
  },

  // Update employee
  async update(
    id: number,
    data: Partial<UpdateEmployeeRequest>,
  ): Promise<Employee> {
    return apiClient.put<Employee>(`/employees/${id}`, data)
  },

  // Delete employee
  async delete(id: number): Promise<void> {
    return apiClient.delete<void>(`/employees/${id}`)
  },
}
