'use client'

import * as React from 'react'
import { Moon, Sun } from 'lucide-react'
import { useTheme } from 'next-themes'

import { Button } from '@/components/ui/button'

export function ModeToggle() {
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = React.useState(false)

  React.useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return (
      <div className="flex items-center justify-between w-full h-[45px] bg-custom-grey-100 rounded-full px-2">
        <Button
          variant="default"
          className="bg-custom-grey-100 cursor-pointer rounded-full h-[30px] w-1/2 flex items-center justify-center px-2"
        >
          <Sun className="h-[1.2rem] w-[1.2rem] scale-100 rotate-0 transition-all text-custom-grey-900" />
          <span className="text-custom-grey-900 font-bold text-xs">Light</span>
        </Button>
        <Button
          variant="default"
          className="bg-custom-grey-100 cursor-pointer rounded-full h-[30px] w-1/2 flex items-center justify-center px-2"
        >
          <Moon className="h-[1.2rem] w-[1.2rem] scale-100 rotate-0 transition-all text-custom-grey-900" />
          <span className="text-custom-grey-900 font-bold text-xs">Dark</span>
        </Button>
      </div>
    )
  }

  return (
    <div className="flex items-center justify-between w-full h-[45px] bg-custom-grey-100 rounded-full px-2">
      <Button
        variant="default"
        className={`${theme === 'light' ? 'bg-white hover:bg-gray-50' : 'bg-custom-grey-100 hover:bg-gray-200'} cursor-pointer rounded-full h-[30px] w-1/2 flex items-center justify-center px-2`}
        onClick={() => setTheme('light')}
      >
        <Sun className="h-[1.2rem] w-[1.2rem] scale-100 rotate-0 transition-all text-custom-grey-900 dark:scale-0 dark:-rotate-90" />
        <span className="text-custom-grey-900 font-bold text-xs">Light</span>
      </Button>
      <Button
        variant="default"
        className={`${theme === 'dark' ? 'bg-white hover:bg-gray-50' : 'bg-custom-grey-100 hover:bg-gray-200'} cursor-pointer rounded-full h-[30px] w-1/2 flex items-center justify-center px-2`}
        onClick={() => setTheme('dark')}
      >
        <Moon className="h-[1.2rem] w-[1.2rem] scale-100 rotate-0 transition-all text-custom-grey-900 dark:scale-0 dark:-rotate-90" />
        <span className="text-custom-grey-900 font-bold text-xs">Dark</span>
      </Button>
    </div>
  )
}
