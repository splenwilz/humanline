'use client'

import { ProtectedRoute } from '@/components/auth/ProtectedRoute'
import EmployeeTable from '@/components/employees/EmployeeTable'
import Greeting from '@/components/navigation/Greeting'
import Navigation from '@/components/navigation/Navigation'
import { employeeColumns } from '@/components/table/column'
import { DataTable } from '@/components/table/data-table'
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import TeamPerformance from '@/components/widgets/teamPerformance'
import TotalEmployee from '@/components/widgets/totalEmployee'
import TotalJob from '@/components/widgets/totalJob'
import { formatNumber } from '@/lib/utils'
import { MoveDown, MoveUp } from 'lucide-react'
interface Employee {
  title: string
  increased: boolean
  value: number
  percentage: string
}
function DashboardContent() {
  // Static data for summary cards
  const employees: Employee[] = [
    {
      title: 'Permanent Employees',
      increased: true,
      value: 3540,
      percentage: '5.14%',
    },
    {
      title: 'Contract employees',
      increased: false,
      value: 1150,
      percentage: '12.2%',
    },
    {
      title: 'Freelance Employees',
      increased: true,
      value: 500,
      percentage: '5.14%',
    },
    {
      title: 'Internship/Training',
      increased: true,
      value: 93,
      percentage: '5.14%',
    },
  ]

  return (
    <div className="flex flex-col border-0 rounded-none bg-custom-grey-50 mb-52">
      <Navigation variant="navigation" className="bg-custom-grey-800" />
      <Greeting />
      <div className="flex justify-center w-full ">
        <div className=" w-[calc(100%-150px)] shadow-sm -mt-20 bg-custom-grey-50 rounded-xl ">
          {/* Cards */}
          <div className="grid grid-cols-4 gap-2">
            {employees.map((employee) => (
              <Card key={employee.title} className="shadow-none border-none">
                <CardHeader>
                  <CardTitle className="text-sm text-custom-grey-900 font-semibold">
                    {employee.title}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <h1 className="text-3xl text-custom-grey-900 font-bold font-manrope">
                    {formatNumber(employee.value)}
                  </h1>
                </CardContent>
                <CardFooter className="text-[12px]">
                  {employee.increased ? (
                    <MoveUp className="size-4 text-custom-base-green" />
                  ) : (
                    <MoveDown className="size-4 text-custom-base-red" />
                  )}
                  <p
                    className={`text-[12px] mr-2 ${employee.increased ? 'text-custom-base-green' : 'text-custom-base-red'}`}
                  >
                    {employee.percentage}
                  </p>
                  <p className="text-custom-grey-600 text-[12px]">
                    {employee.increased
                      ? 'increased vs last month'
                      : 'decreased vs last month'}
                  </p>
                </CardFooter>
              </Card>
            ))}
          </div>
          <div className="flex  gap-2 mt-5">
            <TotalEmployee className="w-[28.5%]" />
            <TotalJob className="w-[28.5%]" />
            <TeamPerformance className="w-[43%]" />
          </div>
          <EmployeeTable />
        </div>
      </div>
    </div>
  )
}

export default function Dashboard() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  )
}
