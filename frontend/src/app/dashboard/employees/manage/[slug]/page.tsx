import { EmploymentInformationForm } from '@/components/employees/EmploymentInformationForm'
import PayrollForm from '@/components/employees/PayrollForm'
import { PersonalInformationForm } from '@/components/employees/PersonalInformationForm'
import DocumentForm from '@/components/employees/DocumentForm'
import SettingsForm from '@/components/employees/SettingsForm'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  ChevronDownIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  Globe,
  MailIcon,
  PhoneIcon,
} from 'lucide-react'

export default async function Page({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  return (
    <div className="w-full p-10 ">
      <div className="flex items-center gap-2">
        <ChevronLeftIcon className="text-custom-grey-500" />
        <h4 className="text-custom-grey-900 font-bold text-[22px]">
          Detail Employee
        </h4>
      </div>
      <div className="flex flex-row gap-6 mt-5 w-full">
        <Card className=" basis-[27%] flex-col shadow-none border-none">
          {/* Avatar */}
          <div className="flex flex-col mt-10 justify-center items-center">
            <Avatar className="w-24 h-24">
              <AvatarImage src="https://github.com/shadcn.png" />
              <AvatarFallback>CN</AvatarFallback>
            </Avatar>
            <h5 className="text-custom-grey-900 font-bold text-[20px] mt-4">
              Pristia Candra
            </h5>
            <p className="text-custom-grey-600 font-normal text-[14px] mt-2">
              3D Designer
            </p>
            {/* Active Button */}
            <div className="flex justify-center gap-1 items-center">
              <Button className="bg-[#E7F7EF] text-[#27A376] text-xs h-5 rounded-[3px] mt-5 w-18 cursor-pointer">
                Active
              </Button>
              <ChevronDownIcon className="text-custom-grey-600 mt-5 h-4 w-4 cursor-pointer" />
            </div>
          </div>
          <Separator className=" bg-custom-grey-200" />
          <div className="flex flex-col gap-3 justify-left ml-5">
            {/* Email, Phone, and Time ZOne with Icons on the left */}
            <div className="flex justify-left gap-4 items-center">
              <MailIcon className="text-custom-grey-600 h-4 w-4" />
              <p className="text-custom-grey-900 font-semibold text-[14px]">
                lincoln@unpixel.com
              </p>
            </div>
            <div className="flex justify-left gap-4 items-center">
              <PhoneIcon className="text-custom-grey-600 h-4 w-4" />
              <p className="text-custom-grey-900 font-semibold text-[14px]">
                +62 812 3456 7890
              </p>
            </div>
            <div className="flex justify-left gap-4 items-center">
              <Globe className="text-custom-grey-600 h-4 w-4" />
              <p className="text-custom-grey-900 font-semibold text-[14px]">
                GMT +07:00
              </p>
            </div>
          </div>
          <Separator className="mt-2 bg-custom-grey-200" />
          <div className="flex flex-col gap-3 px-5">
            <div className="flex justify-between items-center">
              <div className="">
                <span className="text-custom-grey-600 text-[12px]">
                  Department
                </span>
                <p className="text-custom-grey-900 font-semibold text-[13px] mt-1">
                  Designer
                </p>
              </div>
              <ChevronRightIcon className="text-custom-grey-500 h-4 w-4" />
            </div>
            {/* Office */}
            <div className="flex justify-between items-center">
              <div className="">
                <span className="text-custom-grey-600 text-[12px]">Office</span>
                <p className="text-custom-grey-900 font-semibold text-[13px] mt-1">
                  Unpixel Office
                </p>
              </div>
              <ChevronRightIcon className="text-custom-grey-500 h-4 w-4" />
            </div>
            {/* Line Manager */}
            <div className="flex justify-between items-center">
              <div className="">
                <span className="text-custom-grey-600 text-[12px]">
                  Line Manager
                </span>
                <div className="flex items-center gap-2">
                  <Avatar className="w-6 h-6 mt-1">
                    <AvatarImage src="https://github.com/shadcn.png" />
                    <AvatarFallback>CN</AvatarFallback>
                  </Avatar>
                  <p className="text-custom-grey-900 font-semibold text-[13px] mt-1">
                    Skylar Calzoni
                  </p>
                </div>
              </div>
              <ChevronRightIcon className="text-custom-grey-500 h-4 w-4" />
            </div>

            <Button className="bg-custom-grey-900 font-semibold mb-10 text-white h-11 mt-10 cursor-pointer">
              Action
              <ChevronDownIcon className="text-custom-grey-500 h-4 w-4" />
            </Button>
          </div>
        </Card>

        <Card className="basis-[74%] flex-col shadow-none border-none">
          <Tabs defaultValue="general" className="w-full px-10">
            <div className="w-full border-b border-custom-grey-200">
              <TabsList className="bg-transparent h-auto p-0 rounded-none gap-12 w-fit">
                <TabsTrigger
                  value="general"
                  className="bg-transparent border-none rounded-none px-0 py-3 text-custom-grey-900 font-semibold data-[state=active]:text-custom-base-green data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:outline-none hover:text-custom-grey-800 relative data-[state=active]:after:content-[''] data-[state=active]:after:absolute data-[state=active]:after:bottom-0 data-[state=active]:after:-left-6 data-[state=active]:after:-right-6 data-[state=active]:after:h-0.5 data-[state=active]:after:bg-custom-base-green"
                >
                  General
                </TabsTrigger>
                <TabsTrigger
                  value="job"
                  className="bg-transparent border-none rounded-none px-0 py-3 text-custom-grey-900 font-semibold data-[state=active]:text-custom-base-green data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:outline-none hover:text-custom-grey-800 relative data-[state=active]:after:content-[''] data-[state=active]:after:absolute data-[state=active]:after:bottom-0 data-[state=active]:after:-left-6 data-[state=active]:after:-right-6 data-[state=active]:after:h-0.5 data-[state=active]:after:bg-custom-base-green"
                >
                  Job
                </TabsTrigger>
                <TabsTrigger
                  value="payroll"
                  className="bg-transparent border-none rounded-none px-0 py-3 text-custom-grey-900 font-semibold data-[state=active]:text-custom-base-green data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:outline-none hover:text-custom-grey-800 relative data-[state=active]:after:content-[''] data-[state=active]:after:absolute data-[state=active]:after:bottom-0 data-[state=active]:after:-left-6 data-[state=active]:after:-right-6 data-[state=active]:after:h-0.5 data-[state=active]:after:bg-custom-base-green"
                >
                  Payroll
                </TabsTrigger>
                <TabsTrigger
                  value="document"
                  className="bg-transparent border-none rounded-none px-0 py-3 text-custom-grey-900 font-semibold data-[state=active]:text-custom-base-green data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:outline-none hover:text-custom-grey-800 relative data-[state=active]:after:content-[''] data-[state=active]:after:absolute data-[state=active]:after:bottom-0 data-[state=active]:after:-left-6 data-[state=active]:after:-right-6 data-[state=active]:after:h-0.5 data-[state=active]:after:bg-custom-base-green"
                >
                  Document
                </TabsTrigger>
                <TabsTrigger
                  value="settings"
                  className="bg-transparent border-none rounded-none px-0 py-3 text-custom-grey-900 font-semibold data-[state=active]:text-custom-base-green data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:outline-none hover:text-custom-grey-800 relative data-[state=active]:after:content-[''] data-[state=active]:after:absolute data-[state=active]:after:bottom-0 data-[state=active]:after:-left-6 data-[state=active]:after:-right-6 data-[state=active]:after:h-0.5 data-[state=active]:after:bg-custom-base-green"
                >
                  Settings
                </TabsTrigger>
              </TabsList>
            </div>
            <TabsContent value="general">
              <PersonalInformationForm />
            </TabsContent>
            <TabsContent value="job">
              <EmploymentInformationForm />
            </TabsContent>
            <TabsContent value="payroll">
              <PayrollForm />
            </TabsContent>
            <TabsContent value="document">
              <DocumentForm />
            </TabsContent>
            <TabsContent value="settings">
              <SettingsForm />
            </TabsContent>
          </Tabs>
        </Card>
      </div>
    </div>
  )
}
