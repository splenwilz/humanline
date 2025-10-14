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
import type { City, CitiesData } from "@/types/geography"

interface CitySelectProps {
  value?: string
  onValueChange?: (value: string) => void
  placeholder?: string
  disabled?: boolean
  className?: string
  countryId?: number // Filter cities by country ID
  stateId?: number // Filter cities by state ID
}

export function CitySelect({
  value,
  onValueChange,
  placeholder = "Select city...",
  disabled = false,
  className,
  countryId,
  stateId,
}: CitySelectProps) {
  const [open, setOpen] = React.useState(false)
  const [citiesData, setCitiesData] = React.useState<CitiesData[] | null>(null)
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  // Load cities data dynamically when country is selected
  React.useEffect(() => {
    if (!countryId || citiesData) return

    const loadCitiesData = async () => {
      setLoading(true)
      setError(null)
      try {
        const response = await fetch('/data/citiesminified.json')
        if (!response.ok) {
          throw new Error('Failed to load cities data')
        }
        const data = await response.json()
        setCitiesData(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load cities')
        console.error('Error loading cities:', err)
      } finally {
        setLoading(false)
      }
    }

    loadCitiesData()
  }, [countryId, citiesData])

  const filteredCities = React.useMemo(() => {
    if (!countryId || !citiesData) {
      return []
    }

    const country = citiesData.find((country: CitiesData) => country.id === countryId)
    if (!country) return []

    if (stateId) {
      // Filter by specific state
      const state = country.states.find((state) => state.id === stateId)
      return state?.cities || []
    } else {
      // Return all cities from the country
      return country.states.flatMap((state) => state.cities)
    }
  }, [countryId, stateId, citiesData])

  const selectedCity = React.useMemo(() => {
    if (!value) return null
    return filteredCities.find((city: City) => city.name === value)
  }, [value, filteredCities])

  const getPlaceholderText = () => {
    if (loading) return "Loading cities..."
    if (error) return "Error loading cities"
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
          {selectedCity ? (
            <span className="truncate">{selectedCity.name}</span>
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
          <CommandInput placeholder="Search cities..." />
          <CommandList>
            <CommandEmpty>
              {loading ? "Loading cities..." : error ? "Error loading cities" : "No city found."}
            </CommandEmpty>
            <CommandGroup>
              {filteredCities.map((city: City) => (
                <CommandItem
                  key={city.id}
                  value={city.name}
                  onSelect={() => {
                    onValueChange?.(city.name)
                    setOpen(false)
                  }}
                  className="flex items-center gap-2"
                >
                  <span className="flex-1">{city.name}</span>
                  <Check
                    className={cn(
                      "ml-auto h-4 w-4",
                      value === city.name ? "opacity-100" : "opacity-0"
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
