'use client'

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  Dot,
} from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Calendar } from 'lucide-react'

// Sample data for team performance over 7 months
const performanceData = [
  { month: 'Jan', projectTeam: 38000, productTeam: 42000 },
  { month: 'Feb', projectTeam: 44000, productTeam: 39000 },
  { month: 'Mar', projectTeam: 43000, productTeam: 44000 },
  { month: 'Apr', projectTeam: 47000, productTeam: 46000 },
  { month: 'May', projectTeam: 44000, productTeam: 50000 },
  { month: 'Jun', projectTeam: 51000, productTeam: 44000 },
  { month: 'Jul', projectTeam: 49000, productTeam: 40000 },
]

// Custom dot component for the highlighted point
const CustomDot = (props: any) => {
  const { cx, cy, payload } = props
  // Show dot on April data point
  if (payload.month === 'Apr') {
    return (
      <Dot
        cx={cx}
        cy={cy}
        r={4}
        fill="#000000"
        stroke="#ffffff"
        strokeWidth={2}
      />
    )
  }
  return null
}

export default function TeamPerformance({ className }: { className: string }) {
  return (
    <Card
      className={`w-full flex flex-col shadow-none border-none rounded-xl ${className}`}
    >
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-6">
        <CardTitle className="text-custom-grey-900 font-bold text-[20px]">
          Team Performance
        </CardTitle>
        <Select defaultValue="7months">
          <SelectTrigger className="w-[170px] bg-white border-gray-200 focus-active:ring-0 focus-visible:ring-0 ">
            <SelectValue />
            <Calendar className="ml-2 h-4 w-4 text-gray-500" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="7months">Last 7 month</SelectItem>
            <SelectItem value="3months">Last 3 months</SelectItem>
            <SelectItem value="1year">Last year</SelectItem>
          </SelectContent>
        </Select>
      </CardHeader>
      <CardContent>
        {/* Legend */}
        <div className="flex items-center gap-6 mb-8">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-emerald-500"></div>
            <span className="text-sm font-semibold text-gray-700">
              Project Team
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-amber-400"></div>
            <span className="text-sm font-semibold text-gray-700">
              Product Team
            </span>
          </div>
        </div>

        {/* Chart */}
        <div className="h-[300px] w-full -ml-5">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={performanceData}
              margin={{ top: 20, right: 30, left: 0, bottom: 20 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis
                dataKey="month"
                axisLine={false}
                tickLine={false}
                tick={{ fill: '#9ca3af', fontSize: 14 }}
              />
              <YAxis
                axisLine={false}
                tickLine={false}
                tick={{ fill: '#9ca3af', fontSize: 14 }}
                tickFormatter={(value) => `${value / 1000}k`}
                domain={[30000, 60000]}
              />
              <Line
                type="monotone"
                dataKey="projectTeam"
                stroke="#10b981"
                strokeWidth={3}
                dot={false}
                activeDot={{ r: 4, fill: '#10b981' }}
              />
              <Line
                type="monotone"
                dataKey="productTeam"
                stroke="#fbbf24"
                strokeWidth={3}
                dot={<CustomDot />}
                activeDot={{ r: 4, fill: '#fbbf24' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}
