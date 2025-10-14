"use client"

import * as React from "react"
import { Check, ChevronsUpDown } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import type { State, StatesData } from "@/types/geography"

interface StateSelectProps {
  value?: string
  onValueChange?: (value: string) => void
  placeholder?: string
  disabled?: boolean
  className?: string
  countryId?: number // Filter states by country ID
}

export function StateSelect({
  value,
  onValueChange,
  placeholder = "Select state...",
  disabled = false,
  className,
  countryId,
}: StateSelectProps) {
  const [open, setOpen] = React.useState(false)
  const [statesData, setStatesData] = React.useState<StatesData[] | null>(null)
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  // Load states data dynamically when country is selected
  React.useEffect(() => {
    if (!countryId || statesData) return

    const loadStatesData = async () => {
      setLoading(true)
      setError(null)
      try {
        const response = await fetch('/data/statesminified.json')
        if (!response.ok) {
          throw new Error('Failed to load states data')
        }
        const data = await response.json()
        setStatesData(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load states')
        console.error('Error loading states:', err)
      } finally {
        setLoading(false)
      }
    }

    loadStatesData()
  }, [countryId, statesData])

  const filteredStates = React.useMemo(() => {
    if (!countryId || !statesData) {
      return []
    }
    // Find the country by ID and return its states
    const country = statesData.find((country: StatesData) => country.id === countryId)
    return country?.states || []
  }, [countryId, statesData])

  const selectedState = React.useMemo(() => {
    if (!value) return null
    return filteredStates.find((state: State) => state.state_code === value)
  }, [value, filteredStates])

  const getPlaceholderText = () => {
    if (loading) return "Loading states..."
    if (error) return "Error loading states"
    if (!countryId) return "Select country first"
    return placeholder
  }

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className={cn(
            "w-full justify-between h-11 rounded-[10px] focus-visible:ring-0 focus-visible:border-custom-base-green",
            className
          )}
          disabled={disabled || !countryId || loading}
        >
          {selectedState ? (
            <span className="truncate">{selectedState.name}</span>
          ) : (
            <span className="text-muted-foreground">
              {getPlaceholderText()}
            </span>
          )}
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-full p-0" align="start">
        <Command>
          <CommandInput placeholder="Search states..." />
          <CommandList>
            <CommandEmpty>
              {loading ? "Loading states..." : error ? "Error loading states" : "No state found."}
            </CommandEmpty>
            <CommandGroup>
              {filteredStates.map((state: State) => (
                <CommandItem
                  key={state.id}
                  value={state.name}
                  onSelect={() => {
                    onValueChange?.(state.state_code)
                    setOpen(false)
                  }}
                  className="flex items-center gap-2"
                >
                  <span className="flex-1">{state.name}</span>
                  <Check
                    className={cn(
                      "ml-auto h-4 w-4",
                      value === state.state_code ? "opacity-100" : "opacity-0"
                    )}
                  />
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}
