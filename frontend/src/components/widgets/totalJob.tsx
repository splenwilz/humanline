'use client'

import { useState } from 'react'
import { Pie, PieChart, Cell } from 'recharts'
import { Calendar } from 'lucide-react'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from '@/components/ui/chart'

const chartData = [
  { name: 'Active Jobs', value: 71, fill: '#8C62FF' },
  { name: 'UnActive', value: 27, fill: '#2DD4BF' },
  { name: 'Closed', value: 23, fill: '#FE964A' },
]

const chartConfig = {
  value: {
    label: 'Jobs',
  },
  activeJobs: {
    label: 'ActiveJobs',
    color: '#8C62FF',
  },
  unActive: {
    label: 'UnActive',
    color: '#2DD4BF',
  },
  closed: {
    label: 'Closed',
    color: '#FE964A',
  },
} satisfies ChartConfig

export default function TotalJob({ className }: { className: string }) {
  const [activeIndex, setActiveIndex] = useState<number | null>(null)
  const [selectedPeriod, setSelectedPeriod] = useState<string>('all-time')

  // Sample data for different time periods
  const getDataForPeriod = (period: string) => {
    switch (period) {
      case 'yearly':
        return [
          { name: 'Active Jobs', value: 65, fill: '#8C62FF' },
          { name: 'UnActive', value: 32, fill: '#2DD4BF' },
          { name: 'Closed', value: 18, fill: '#FE964A' },
        ]
      case 'monthly':
        return [
          { name: 'Active Jobs', value: 45, fill: '#8C62FF' },
          { name: 'UnActive', value: 15, fill: '#2DD4BF' },
          { name: 'Closed', value: 8, fill: '#FE964A' },
        ]
      default: // all-time
        return chartData
    }
  }

  const currentData = getDataForPeriod(selectedPeriod)
  const currentTotal = currentData.reduce((sum, item) => sum + item.value, 0)

  return (
    <Card
      className={`flex flex-col shadow-none border-none rounded-xl ${className}`}
    >
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-6">
        <CardTitle className="text-custom-grey-900 font-bold text-[20px]">
          Job Summary
        </CardTitle>
        <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
          <SelectTrigger className="bg-transparent border-0 ring-0 focus:ring-0 focus-visible:ring-0 focus-visible:border-0 focus:border-0 hover:border-0 shadow-none outline-none focus:outline-none focus-visible:outline-none">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all-time">All Time</SelectItem>
            <SelectItem value="yearly">Yearly</SelectItem>
            <SelectItem value="monthly">Monthly</SelectItem>
          </SelectContent>
        </Select>
      </CardHeader>
      <CardContent className="flex-1 pb-0">
        <div className="relative">
          <ChartContainer
            config={chartConfig}
            className="mx-auto aspect-square max-h-[250px] relative z-10"
          >
            <PieChart>
              <ChartTooltip
                cursor={false}
                content={<ChartTooltipContent hideLabel />}
              />
              <Pie
                data={currentData}
                dataKey="value"
                nameKey="name"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={4}
                onMouseEnter={(_, index) => setActiveIndex(index)}
                onMouseLeave={() => setActiveIndex(null)}
              >
                {currentData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={entry.fill}
                    stroke={entry.fill}
                    strokeWidth={activeIndex === index ? 3 : 1}
                    style={{
                      filter:
                        activeIndex === index
                          ? 'drop-shadow(0 4px 8px rgba(0,0,0,0.2))'
                          : 'none',
                      transform:
                        activeIndex === index ? 'scale(1.05)' : 'scale(1)',
                      transformOrigin: 'center',
                      transition: 'all 0.2s ease-in-out',
                    }}
                  />
                ))}
              </Pie>
            </PieChart>
          </ChartContainer>
          {/* Center text */}
          <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none z-0">
            <div
              className="w-24 h-24 rounded-full border-0.5 border-custom-grey-600 bg-white flex flex-col items-center justify-center pointer-events-none"
              style={{ boxShadow: '0 0 8px rgba(0, 0, 0, 0.15)' }}
            >
              <h4 className="text-2xl font-bold text-gray-900">
                {currentTotal}
              </h4>
              <div className="text-xs text-custom-grey-500">Total Jobs</div>
            </div>
          </div>
        </div>
        {/* Legend */}
        <div className="mt-6 space-y-3">
          {currentData.map((item, index) => (
            <div
              key={`${item.name}-${index}`}
              className="flex items-center justify-between"
            >
              <div className="flex items-center gap-3">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{
                    backgroundColor: item.fill,
                    minWidth: '12px',
                    minHeight: '12px',
                  }}
                />
                <span className="text-sm text-gray-600">{item.name}</span>
              </div>
              <span className="text-sm font-medium text-gray-900">
                {item.value}
              </span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
