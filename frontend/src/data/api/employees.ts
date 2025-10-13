import type { CreateEmployeeRequest, Employee, Employees } from '@/types/employees'
import { apiClient } from './client'

// Employee API functions
export const employeeApi = {
  // Get all employees
  async getAll(): Promise<Employees[]> {
    return apiClient.get<Employees[]>('/employees')
  },

  // Get employee by ID
  async getById(id: number): Promise<Employee> {
    return apiClient.get<Employee>(`/employees/${id}`)
  },

  // Create new employee
  async create(data: CreateEmployeeRequest): Promise<Employees> {
    return apiClient.post<Employees>('/employees', data)
  },

  // // Update employee
  // async update(
  //   id: number,
  //   data: Partial<UpdateEmployeeRequest>,
  // ): Promise<Employee> {
  //   return apiClient.put<Employee>(`/employees/${id}`, data)
  // },

  // Delete employee
  async delete(id: number): Promise<void> {
    return apiClient.delete<void>(`/employees/${id}`)
  },
}
