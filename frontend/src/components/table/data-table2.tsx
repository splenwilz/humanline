'use client'

import React from 'react'
import {
  ColumnDef,
  ColumnFiltersState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  SortingState,
  useReactTable,
} from '@tanstack/react-table'

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select'

import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet'
import { DownloadIcon, PlusIcon, SearchIcon } from 'lucide-react'
import { Label } from '../ui/label'
import { AddEmployeeForm } from '../employees/AddEmployeeForm'

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[]
  data: TData[]
}

// Helper function to get unique values from data
function getUniqueValues<TData>(data: TData[], key: keyof TData): string[] {
  const values = data.map((item) => String(item[key]))
  return Array.from(new Set(values)).sort()
}

export function DataTable2<TData, TValue>({
  columns,
  data,
}: DataTableProps<TData, TValue>) {
  const [sorting, setSorting] = React.useState<SortingState>([])
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>(
    [],
  )
  const [rowSelection, setRowSelection] = React.useState({})
  const table = useReactTable({
    data,
    columns,
    onSortingChange: setSorting,
    getSortedRowModel: getSortedRowModel(),

    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onColumnFiltersChange: setColumnFilters,
    getFilteredRowModel: getFilteredRowModel(),
    onRowSelectionChange: setRowSelection,
    state: {
      sorting,
      columnFilters,
      rowSelection,
    },
  })

  // Get unique values for filters
  const offices = getUniqueValues(data, 'office' as keyof TData)
  const jobTitles = getUniqueValues(data, 'job_title' as keyof TData)
  const employmentStatuses = getUniqueValues(
    data,
    'employement_status' as keyof TData,
  )

  return (
    <div className="overflow-hidden border bg-white shadow-none border-none rounded-xl w-full min-w-0">
      <div className="flex items-center justify-between px-4 py-4 mt-4">
        <div className="">
          <h5 className="text-custom-grey-900 font-bold text-[18px]">
            Employees
          </h5>
          <p className="text-xs py-1 text-custom-grey-600 tracking-wider">
            Manage your Employee
          </p>
        </div>
        <div className="flex gap-2">
          {/* Download and add new button */}
          <Button
            variant="outline"
            className="border-custom-grey-900 text-custom-grey-900 cursor-pointer"
          >
            <DownloadIcon className="h-4 w-4" />
            Download
          </Button>

          <Sheet>
            <SheetTrigger>
              <Button className="bg-custom-grey-900 text-white cursor-pointer">
                <PlusIcon className="h-4 w-4" />
                Add New
              </Button>
            </SheetTrigger>
            <SheetContent>
              <SheetHeader>
                <SheetTitle className="text-[20px] font-bold text-custom-grey-900 my-2">
                  Add New Profile
                </SheetTitle>
              </SheetHeader>
              <div className="px-4">
                <AddEmployeeForm />
              </div>
              <SheetFooter>
                <Button type="submit">Add Employee</Button>
                <SheetClose asChild>
                  <Button variant="outline">Close</Button>
                </SheetClose>
              </SheetFooter>
            </SheetContent>
          </Sheet>
        </div>
      </div>
      <div className="flex items-center gap-4 py-4 px-4 w-full">
        <div className="relative">
          <Input
            placeholder="Search employees..."
            value={(table.getColumn('name')?.getFilterValue() as string) ?? ''}
            onChange={(event) =>
              table.getColumn('name')?.setFilterValue(event.target.value)
            }
            className="min-w-sm h-11 ring-0 border-custom-grey-300 focus:border-custom-grey-300 focus-visible:border-custom-grey-300 focus-visible:ring-0 placeholder-custom-grey-300 text-xs"
          />
          <SearchIcon className="absolute h-4 w-4 right-2 top-1/2 transform -translate-y-1/2 text-custom-grey-500" />
        </div>
        <Select
          value={(table.getColumn('office')?.getFilterValue() as string) ?? ''}
          onValueChange={(value) =>
            table
              .getColumn('office')
              ?.setFilterValue(value === 'all' ? '' : value)
          }
        >
          <SelectTrigger className="w-1/3 !h-11">
            <SelectValue placeholder="Filter by office" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Offices</SelectItem>
            {offices.map((office) => (
              <SelectItem key={office} value={office}>
                {office}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select
          value={
            (table.getColumn('job_title')?.getFilterValue() as string) ?? ''
          }
          onValueChange={(value) =>
            table
              .getColumn('job_title')
              ?.setFilterValue(value === 'all' ? '' : value)
          }
        >
          <SelectTrigger className="w-1/3 !h-11">
            <SelectValue placeholder="Filter by job title" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Job Titles</SelectItem>
            {jobTitles.map((title) => (
              <SelectItem key={title} value={title}>
                {title}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select
          value={
            (table
              .getColumn('employement_status')
              ?.getFilterValue() as string) ?? ''
          }
          onValueChange={(value) =>
            table
              .getColumn('employement_status')
              ?.setFilterValue(value === 'all' ? '' : value)
          }
        >
          <SelectTrigger className="w-1/3 !h-11">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
            {employmentStatuses.map((status) => (
              <SelectItem key={status} value={status}>
                {status}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="overflow-x-auto">
        <Table>
          <TableHeader className="px-4 py-4">
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  return (
                    <TableHead key={header.id} className="px-4 py-4">
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext(),
                          )}
                    </TableHead>
                  )
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody className="px-4 py-4">
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && 'selected'}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id} className="px-4 py-4">
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext(),
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center"
                >
                  No results.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      <div className="flex items-center justify-between px-4 py-4">
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
            className="h-8 w-8 p-0"
          >
            ‹
          </Button>

          {(() => {
            const currentPage = table.getState().pagination.pageIndex
            const totalPages = table.getPageCount()
            const pages = []

            // Always show page 1
            pages.push(
              <Button
                key={1}
                variant={currentPage === 0 ? 'default' : 'outline'}
                size="sm"
                onClick={() => table.setPageIndex(0)}
                className="h-8 w-8 p-0"
              >
                1
              </Button>,
            )

            // Show pages around current page
            if (currentPage > 2) {
              pages.push(
                <span key="ellipsis1" className="px-2 text-gray-500">
                  ...
                </span>,
              )
            }

            // Show current page and surrounding pages
            for (
              let i = Math.max(2, currentPage - 1);
              i <= Math.min(totalPages - 1, currentPage + 3);
              i++
            ) {
              if (i !== 1) {
                // Don't duplicate page 1
                pages.push(
                  <Button
                    key={i}
                    variant={currentPage === i - 1 ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => table.setPageIndex(i - 1)}
                    className="h-8 w-8 p-0"
                  >
                    {i}
                  </Button>,
                )
              }
            }

            // Show last page if not already shown
            if (totalPages > 1 && currentPage < totalPages - 4) {
              pages.push(
                <span key="ellipsis2" className="px-2 text-gray-500">
                  ...
                </span>,
              )
              pages.push(
                <Button
                  key={totalPages}
                  variant={
                    currentPage === totalPages - 1 ? 'default' : 'outline'
                  }
                  size="sm"
                  onClick={() => table.setPageIndex(totalPages - 1)}
                  className="h-8 w-8 p-0"
                >
                  {totalPages}
                </Button>,
              )
            }

            return pages
          })()}

          <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
            className="h-8 w-8 p-0"
          >
            ›
          </Button>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-700">
            Showing{' '}
            {table.getState().pagination.pageIndex *
              table.getState().pagination.pageSize +
              1}{' '}
            to{' '}
            {Math.min(
              (table.getState().pagination.pageIndex + 1) *
                table.getState().pagination.pageSize,
              table.getFilteredRowModel().rows.length,
            )}{' '}
            of {table.getFilteredRowModel().rows.length} entries
          </div>
          <Select
            value={table.getState().pagination.pageSize.toString()}
            onValueChange={(value) => table.setPageSize(Number(value))}
          >
            <SelectTrigger className="w-20 h-8">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="5">Show 5</SelectItem>
              <SelectItem value="8">Show 8</SelectItem>
              <SelectItem value="10">Show 10</SelectItem>
              <SelectItem value="20">Show 20</SelectItem>
              <SelectItem value="50">Show 50</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  )
}
