'use client'

import { useEmployees } from '@/hooks/useEmployees'
import React from 'react'
import { DataTable } from '../table/data-table'
import { employeeColumns } from '../table/column'

export default function EmployeeTable() {
  const { employees: employeeData, loading, error } = useEmployees()
  const data = employeeData
  return (
    <div className="flex flex-col gap-2 mt-5 w-full min-w-0">
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-custom-grey-600">Loading employees...</div>
        </div>
      ) : error ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-red-500">Error: {error}</div>
        </div>
      ) : (
        <DataTable columns={employeeColumns} data={data} />
      )}
    </div>
  )
}
