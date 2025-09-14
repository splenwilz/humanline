import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// format number to 0,000
export function formatNumber(number: number) {
  return number.toLocaleString('en-US')
}
