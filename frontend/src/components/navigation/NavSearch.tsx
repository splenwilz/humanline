import { CommandIcon, SearchIcon } from 'lucide-react'
import { Input } from '../ui/input'

export default function NavSearch({ className }: { className: string }) {
  return (
    <div className={`w-[250px] relative ${className}`}>
      <SearchIcon className="absolute h-4 w-4 text-white left-2 top-1/2 transform -translate-y-1/2" />
      <Input
        type="text"
        placeholder="Search anything"
        className="w-full pl-8  border-0 ring-0 focus-visible:ring-0 bg-custom-grey-700 text-white placeholder-custom-grey-600"
      />
      <div className="absolute bg-custom-grey-800 rounded-md h-6 w-11 right-2 top-1/2 transform -translate-y-1/2">
        <div className="flex items-center justify-center mt-0.5">
          <CommandIcon className="h-3 w-3 text-white" />
          <p className="ml-2 text-sm text-white">F</p>
        </div>
      </div>
    </div>
  )
}
