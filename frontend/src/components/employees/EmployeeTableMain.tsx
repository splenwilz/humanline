'use client'

import { useEmployees } from '@/hooks/useEmployees'
import React from 'react'
import { employeeColumns } from '../table/column'
import { DataTable2 } from '../table/data-table2'

export default function EmployeeTable() {
  const { employees: employeeData, loading, error } = useEmployees()
  const data = employeeData || []
  return (
    <div className="flex flex-col gap-2 mt-5 w-full min-w-0">
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-custom-grey-600">Loading employees...</div>
        </div>
      ) : (
        <DataTable2 columns={employeeColumns} data={data} />
      )}
    </div>
  )
}
