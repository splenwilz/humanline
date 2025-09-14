// Demo API exports - to be replaced with real API calls when backend is ready
export { employeeApi, demoEmployees, type EmployeeDetails } from './employees'

// Demo API configuration
export const DEMO_API_CONFIG = {
  baseUrl: '/api/demo', // This will be replaced with real API base URL
  timeout: 5000,
  retries: 3,
}

// Helper function to simulate API errors (for testing error handling)
export const simulateApiError = (probability: number = 0.1): boolean => {
  return Math.random() < probability
}

// Helper function to add random delay to simulate network latency
export const addRandomDelay = (
  min: number = 100,
  max: number = 1000,
): Promise<void> => {
  const delay = Math.random() * (max - min) + min
  return new Promise((resolve) => setTimeout(resolve, delay))
}
