import { EmployeeManagementTable } from '../table/EmployeeManagementTable'
import { employeeApi } from '@/data/api/employees'
import type { Employees } from '@/types/employees'
import type { EmployeeDetails } from '../table/EmployeeColumns'

// Transform Employees to EmployeeDetails for table compatibility
function transformEmployeeToTableFormat(employee: Employees): EmployeeDetails {
  return {
    id: employee.id.toString(),
    name: `${employee.first_name} ${employee.last_name}`,
    email: employee.email,
    job_title: employee.job_title || '',
    department: employee.department || '',
    office: employee.office || '',
    employment_status: employee.employment_status.toUpperCase(),
    account: employee.email, // Using email as account for now
  }
}

export default async function EmployeeTableMain() {
  const employees = await employeeApi.getAll()
  const transformedData = employees.map(transformEmployeeToTableFormat)
  
  return (
    <div className="flex flex-col gap-2 mt-5 w-full min-w-0">
      <EmployeeManagementTable data={transformedData} />
    </div>
  )
}
