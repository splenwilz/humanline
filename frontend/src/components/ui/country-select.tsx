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
import countriesData from "@/static-data/countriesminified.json"
import type { Country } from "@/types/geography"

interface CountrySelectProps {
  value?: string
  onValueChange?: (value: string) => void
  placeholder?: string
  disabled?: boolean
  className?: string
}

export function CountrySelect({
  value,
  onValueChange,
  placeholder = "Select country...",
  disabled = false,
  className,
}: CountrySelectProps) {
  const [open, setOpen] = React.useState(false)

  const selectedCountry = React.useMemo(() => {
    if (!value) return null
    return (countriesData as Country[]).find((country: Country) => country.iso3 === value)
  }, [value])

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
          disabled={disabled}
        >
          {selectedCountry ? (
            <div className="flex items-center gap-2">
              <span className="text-lg">{selectedCountry.emoji}</span>
              <span className="truncate">{selectedCountry.name}</span>
            </div>
          ) : (
            <span className="text-muted-foreground">{placeholder}</span>
          )}
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-full p-0" align="start">
        <Command>
          <CommandInput placeholder="Search countries..." />
          <CommandList>
            <CommandEmpty>No country found.</CommandEmpty>
            <CommandGroup>
              {(countriesData as Country[]).map((country: Country) => (
                <CommandItem
                  key={country.id}
                  value={country.name}
                  onSelect={() => {
                    onValueChange?.(country.iso3)
                    setOpen(false)
                  }}
                  className="flex items-center gap-2"
                >
                  <span className="text-lg">{country.emoji}</span>
                  <span className="flex-1">{country.name}</span>
                  <Check
                    className={cn(
                      "ml-auto h-4 w-4",
                      value === country.iso3 ? "opacity-100" : "opacity-0"
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
