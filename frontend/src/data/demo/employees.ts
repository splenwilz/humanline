export interface EmployeeDetails {
  id: string
  name: string
  email: string
  avatar?: string
  job_title: string
  line_manager: string
  department: string
  office: string
  employement_status: string
  account: string
}

// Demo employee data - to be replaced with real API calls
export const demoEmployees: EmployeeDetails[] = [
  {
    id: '1',
    name: 'Pristia Candra',
    email: 'lincoln@unpixel.com',
    job_title: 'UI UX Designer',
    line_manager: '@SarahJohnson',
    department: 'Team Product',
    office: 'Unpixel Office',
    employement_status: 'ACTIVE',
    account: 'Activated',
  },
  {
    id: '2',
    name: 'Hanna Baptista',
    email: 'hanna@unpixel.com',
    job_title: 'Graphic Designer',
    line_manager: '@PristiaCandra',
    department: 'Team Product',
    office: 'Unpixel Office',
    employement_status: 'ON BOARDING',
    account: 'Activated',
  },
  {
    id: '3',
    name: 'Miracle Geidt',
    email: 'miracle@unpixel.com',
    job_title: 'Finance',
    line_manager: '@MichaelChen',
    department: 'Team Product',
    office: 'Unpixel Office',
    employement_status: 'PROBATION',
    account: 'Need Invitation',
  },
  {
    id: '4',
    name: 'Rayna Torff',
    email: 'rayna@unpixel.com',
    job_title: 'Project Manager',
    line_manager: '@PristiaCandra',
    department: 'Team Product',
    office: 'Unpixel Office',
    employement_status: 'ACTIVE',
    account: 'Activated',
  },
  {
    id: '5',
    name: 'Giana Lipshutz',
    email: 'giana@unpixel.com',
    job_title: 'Creative Director',
    line_manager: '@SarahJohnson',
    department: 'Team Product',
    office: 'Unpixel Office',
    employement_status: 'ON LEAVE',
    account: 'Need Invitation',
  },
  {
    id: '6',
    name: 'James Wilson',
    email: 'james.wilson@unpixel.com',
    job_title: 'DevOps Engineer',
    line_manager: '@MichaelChen',
    department: 'Team Engineering',
    office: 'Unpixel Office',
    employement_status: 'ACTIVE',
    account: 'Activated',
  },
  {
    id: '7',
    name: 'Maria Garcia',
    email: 'maria.garcia@unpixel.com',
    job_title: 'HR Specialist',
    line_manager: '@SarahJohnson',
    department: 'Team HR',
    office: 'Unpixel Office',
    employement_status: 'ACTIVE',
    account: 'Activated',
  },
  {
    id: '8',
    name: 'Alex Patel',
    email: 'alex.patel@unpixel.com',
    job_title: 'Frontend Developer',
    line_manager: '@JamesWilson',
    department: 'Team Engineering',
    office: 'Unpixel Office',
    employement_status: 'PROBATION',
    account: 'Need Invitation',
  },
  {
    id: '9',
    name: 'Jennifer Lee',
    email: 'jennifer.lee@unpixel.com',
    job_title: 'Sales Director',
    line_manager: '@PristiaCandra',
    department: 'Team Sales',
    office: 'Unpixel Office',
    employement_status: 'ACTIVE',
    account: 'Activated',
  },
  {
    id: '10',
    name: 'Robert Taylor',
    email: 'robert.taylor@unpixel.com',
    job_title: 'Backend Developer',
    line_manager: '@MichaelChen',
    department: 'Team Engineering',
    office: 'Unpixel Office',
    employement_status: 'ACTIVE',
    account: 'Activated',
  },
  {
    id: '11',
    name: 'Amanda Brown',
    email: 'amanda.brown@unpixel.com',
    job_title: 'Content Writer',
    line_manager: '@JenniferLee',
    department: 'Team Marketing',
    office: 'Unpixel Office',
    employement_status: 'ON BOARDING',
    account: 'Need Invitation',
  },
  {
    id: '12',
    name: 'Kevin Zhang',
    email: 'kevin.zhang@unpixel.com',
    job_title: 'QA Engineer',
    line_manager: '@JamesWilson',
    department: 'Team Engineering',
    office: 'Unpixel Office',
    employement_status: 'ACTIVE',
    account: 'Activated',
  },
  {
    id: '13',
    name: 'Rachel Davis',
    email: 'rachel.davis@unpixel.com',
    job_title: 'Financial Analyst',
    line_manager: '@MichaelChen',
    department: 'Team Finance',
    office: 'Unpixel Office',
    employement_status: 'ACTIVE',
    account: 'Activated',
  },
  {
    id: '14',
    name: 'Daniel Martinez',
    email: 'daniel.martinez@unpixel.com',
    job_title: 'Mobile Developer',
    line_manager: '@RobertTaylor',
    department: 'Team Engineering',
    office: 'Unpixel Office',
    employement_status: 'PROBATION',
    account: 'Need Invitation',
  },
  {
    id: '15',
    name: 'Sophie Anderson',
    email: 'sophie.anderson@unpixel.com',
    job_title: 'Operations Manager',
    line_manager: '@SarahJohnson',
    department: 'Team Operations',
    office: 'Unpixel Office',
    employement_status: 'ACTIVE',
    account: 'Activated',
  },
  {
    id: '16',
    name: 'Chris Johnson',
    email: 'chris.johnson@unpixel.com',
    job_title: 'Security Engineer',
    line_manager: '@JamesWilson',
    department: 'Team Engineering',
    office: 'Unpixel Office',
    employement_status: 'ACTIVE',
    account: 'Activated',
  },
  {
    id: '17',
    name: 'Nina Kumar',
    email: 'nina.kumar@unpixel.com',
    job_title: 'Business Analyst',
    line_manager: '@SophieAnderson',
    department: 'Team Strategy',
    office: 'Unpixel Office',
    employement_status: 'ACTIVE',
    account: 'Activated',
  },
  {
    id: '18',
    name: 'Tom Wilson',
    email: 'tom.wilson@unpixel.com',
    job_title: 'Customer Success Manager',
    line_manager: '@JenniferLee',
    department: 'Team Customer Success',
    office: 'Unpixel Office',
    employement_status: 'ACTIVE',
    account: 'Activated',
  },
  {
    id: '19',
    name: 'Priya Singh',
    email: 'priya.singh@unpixel.com',
    job_title: 'Machine Learning Engineer',
    line_manager: '@MichaelChen',
    department: 'Team AI/ML',
    office: 'Unpixel Office',
    employement_status: 'ON BOARDING',
    account: 'Need Invitation',
  },
  {
    id: '20',
    name: 'Mark Thompson',
    email: 'mark.thompson@unpixel.com',
    job_title: 'Technical Writer',
    line_manager: '@RobertTaylor',
    department: 'Team Engineering',
    office: 'Unpixel Office',
    employement_status: 'ON LEAVE',
    account: 'Need Invitation',
  },
]

// Mock API functions to simulate backend calls
export const employeeApi = {
  // Get all employees
  getAll: async (): Promise<EmployeeDetails[]> => {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500))
    return demoEmployees
  },

  // Get employee by ID
  getById: async (id: string): Promise<EmployeeDetails | null> => {
    await new Promise((resolve) => setTimeout(resolve, 300))
    return demoEmployees.find((emp) => emp.id === id) || null
  },

  // Search employees
  search: async (query: string): Promise<EmployeeDetails[]> => {
    await new Promise((resolve) => setTimeout(resolve, 400))
    const lowercaseQuery = query.toLowerCase()
    return demoEmployees.filter(
      (emp) =>
        emp.name.toLowerCase().includes(lowercaseQuery) ||
        emp.job_title.toLowerCase().includes(lowercaseQuery) ||
        emp.department.toLowerCase().includes(lowercaseQuery) ||
        emp.office.toLowerCase().includes(lowercaseQuery),
    )
  },

  // Filter by department
  getByDepartment: async (department: string): Promise<EmployeeDetails[]> => {
    await new Promise((resolve) => setTimeout(resolve, 300))
    return demoEmployees.filter((emp) => emp.department === department)
  },

  // Filter by employment status
  getByStatus: async (status: string): Promise<EmployeeDetails[]> => {
    await new Promise((resolve) => setTimeout(resolve, 300))
    return demoEmployees.filter((emp) => emp.employement_status === status)
  },

  // Get employees by office
  getByOffice: async (office: string): Promise<EmployeeDetails[]> => {
    await new Promise((resolve) => setTimeout(resolve, 300))
    return demoEmployees.filter((emp) => emp.office === office)
  },

  // Get employee statistics
  getStats: async () => {
    await new Promise((resolve) => setTimeout(resolve, 200))
    const total = demoEmployees.length
    const byStatus = demoEmployees.reduce(
      (acc, emp) => {
        acc[emp.employement_status] = (acc[emp.employement_status] || 0) + 1
        return acc
      },
      {} as Record<string, number>,
    )

    const byDepartment = demoEmployees.reduce(
      (acc, emp) => {
        acc[emp.department] = (acc[emp.department] || 0) + 1
        return acc
      },
      {} as Record<string, number>,
    )

    const byOffice = demoEmployees.reduce(
      (acc, emp) => {
        acc[emp.office] = (acc[emp.office] || 0) + 1
        return acc
      },
      {} as Record<string, number>,
    )

    return {
      total,
      byStatus,
      byDepartment,
      byOffice,
    }
  },
}
