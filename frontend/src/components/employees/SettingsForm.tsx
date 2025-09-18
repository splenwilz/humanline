'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Check, X } from 'lucide-react'
import Image from 'next/image'

export default function SettingsForm() {
  const [isEditingTimezone, setIsEditingTimezone] = useState(false)
  const [isEditingBirthday, setIsEditingBirthday] = useState(false)
  const [timezone, setTimezone] = useState(
    'GMT +07:00 Bangkok, Ha Noi, Jakarta',
  )
  const [birthdayVisibility, setBirthdayVisibility] = useState('Everyone')

  const handleTimezoneSave = () => {
    setIsEditingTimezone(false)
    // Here you would typically save to backend
  }

  const handleTimezoneCancel = () => {
    setIsEditingTimezone(false)
    // Reset to original value if needed
  }

  const handleBirthdaySave = () => {
    setIsEditingBirthday(false)
    // Here you would typically save to backend
  }

  const handleBirthdayCancel = () => {
    setIsEditingBirthday(false)
    // Reset to original value if needed
  }

  return (
    <div className="space-y-8">
      {/* Account Settings Section */}
      <Card className="p-6 border border-custom-grey-200 rounded-2xl mt-10 shadow-none">
        <div className="space-y-6 ">
          <div className="flex flex-row gap-3 justify-between w-full">
            <h3 className="text-lg font-semibold text-custom-grey-900">
              Account Settings
            </h3>

            <div className="flex items-center gap-2">
              <Button
                size="sm"
                variant="ghost"
                className="h-6 w-6 p-0 text-custom-grey-400 hover:text-custom-grey-600"
                onClick={() => setIsEditingTimezone(true)}
              >
                <Image src="/icons/edit.svg" alt="edit" width={18} height={18} />
              </Button>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <Label className="text-sm text-custom-grey-600 mb-2 block">
                  Timezone
                </Label>

                {isEditingTimezone ? (
                  <div className="flex items-center gap-2">
                    <Input
                      value={timezone}
                      onChange={(e) => setTimezone(e.target.value)}
                      className="flex-1 h-10 rounded-lg border-custom-grey-200 focus-visible:ring-0 focus-visible:border-custom-base-green"
                    />
                    <Button
                      size="sm"
                      className="h-8 w-8 p-0 bg-custom-base-green hover:bg-green-600"
                      onClick={handleTimezoneSave}
                    >
                      <Check className="h-4 w-4 text-white" />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      className="h-8 w-8 p-0 border-custom-grey-300 hover:bg-custom-grey-50"
                      onClick={handleTimezoneCancel}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-custom-grey-900">
                      {timezone}
                    </span>
                   
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Privacy Section */}
      <Card className="p-6 border border-custom-grey-200 rounded-2xl shadow-none">
        <div className="space-y-6">
          <div className="flex flex-row gap-3 justify-between w-full">
          <h3 className="text-lg font-semibold text-custom-grey-900">
            Privacy
          </h3>

            <div className="flex items-center gap-2">
              <Button
                size="sm"
                variant="ghost"
                className="h-6 w-6 p-0 text-custom-grey-400 hover:text-custom-grey-600"
                onClick={() => setIsEditingBirthday(true)}
              >
                <Image src="/icons/edit.svg" alt="edit" width={18} height={18} />
              </Button>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <Label className="text-sm text-custom-grey-600 mb-2 block">
                  Who can see your birthday on calendar?
                </Label>
                {isEditingBirthday ? (
                  <div className="flex items-center gap-2">
                    <Select
                      value={birthdayVisibility}
                      onValueChange={setBirthdayVisibility}
                    >
                      <SelectTrigger className="flex-1 h-10 rounded-lg border-custom-grey-200 focus-visible:ring-0 focus-visible:border-custom-base-green">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Everyone">Everyone</SelectItem>
                        <SelectItem value="Colleagues">Colleagues</SelectItem>
                        <SelectItem value="Managers">Managers</SelectItem>
                        <SelectItem value="Nobody">Nobody</SelectItem>
                      </SelectContent>
                    </Select>
                    <Button
                      size="sm"
                      className="h-8 w-8 p-0 bg-custom-base-green hover:bg-green-600"
                      onClick={handleBirthdaySave}
                    >
                      <Check className="h-4 w-4 text-white" />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      className="h-8 w-8 p-0 border-custom-grey-300 hover:bg-custom-grey-50"
                      onClick={handleBirthdayCancel}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-custom-grey-900">
                      {birthdayVisibility}
                    </span>
                   
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </Card>
    </div>
  )
}
