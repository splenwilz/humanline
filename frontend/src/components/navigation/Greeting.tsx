import Link from 'next/link'

export default function Greeting() {
  return (
    <div className="flex justify-between bg-custom-grey-800 h-[200px] px-20 py-6">
      <div className="flex flex-col  mr-10">
        <h3 className="text-white text-2xl font-bold">Hi, Pristia</h3>
        <p className="text-custom-grey-600 text-sm">
          This is your HR report so far
        </p>
      </div>
      <div className="flex gap-8 text-white text-[13px] mt-3 ">
        <Link href="dashboard/employees">Employees</Link>
        <Link href="dashboard/check-list">Check List</Link>
        <Link href="dashboard/time-off">Time off</Link>
        <Link href="dashboard/attendance">Attendance</Link>
        <Link href="dashboard/payroll">Payroll</Link>
        <Link href="dashboard/performance">Performance</Link>
        <Link href="dashboard/recruitment">Recruitment</Link>
      </div>
    </div>
  )
}
