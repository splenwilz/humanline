import { apiClient } from './client'

// Employee types
export interface Employee {
  id: string
  first_name: string
  last_name: string
  email: string
  phone?: string
  job_title: string
  department: string
  office: string
  employment_status: 'active' | 'inactive' | 'terminated'
  hire_date: string
  salary?: number
  manager_id?: string
  created_at: string
  updated_at: string
}

export interface EmployeeStats {
  total: number
  byStatus: Record<string, number>
  byDepartment: Record<string, number>
  byOffice: Record<string, number>
}

export interface CreateEmployeeRequest {
  first_name: string
  last_name: string
  email: string
  phone?: string
  job_title: string
  department: string
  office: string
  employment_status?: 'active' | 'inactive'
  hire_date: string
  salary?: number
  manager_id?: string
}

export interface UpdateEmployeeRequest extends Partial<CreateEmployeeRequest> {
  id: string
}

// Employee API functions
export const employeeApi = {
  // Get all employees
  async getAll(): Promise<Employee[]> {
    return apiClient.get<Employee[]>('/employees')
  },

  // Get employee by ID
  async getById(id: string): Promise<Employee> {
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
    id: string,
    data: Partial<UpdateEmployeeRequest>,
  ): Promise<Employee> {
    return apiClient.put<Employee>(`/employees/${id}`, data)
  },

  // Delete employee
  async delete(id: string): Promise<void> {
    return apiClient.delete<void>(`/employees/${id}`)
  },
}
