'use client'

import * as React from 'react'
import {
  Bot,
  BriefcaseBusiness,
  CalendarPlus2,
  CircleQuestionMark,
  CreditCard,
  Settings,
  Timer,
  TrendingUp,
  Users,
} from 'lucide-react'

import NavMain from '@/components/sidebar/nav-main'
import NavSecondary from '@/components/sidebar/nav-secondary'
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from '@/components/ui/sidebar'
import Image from 'next/image'
import { ModeToggle } from './theme/nav-theme-switch'

const data = {
  user: {
    name: 'shadcn',
    email: 'm@example.com',
    avatar: '/avatars/shadcn.jpg',
  },
  navMain: [
    {
      title: 'Employees',
      url: '/dashboard/employees',
      icon: Users,
      isActive: true,
      items: [
        {
          title: 'Manage Employees',
          url: '/dashboard/employees/manage',
        },
        {
          title: 'Directories',
          url: '/dashboard/employees/directory',
        },
        {
          title: 'ORG Chart',
          url: '#',
        },
      ],
    },
    {
      title: 'Checklist',
      url: '#',
      icon: Bot,
      items: [
        {
          title: 'Genesis',
          url: '#',
        },
        {
          title: 'Explorer',
          url: '#',
        },
        {
          title: 'Quantum',
          url: '#',
        },
      ],
    },
    {
      title: 'Time Off',
      url: '#',
      icon: Timer,
      items: [
        {
          title: 'Introduction',
          url: '#',
        },
        {
          title: 'Get Started',
          url: '#',
        },
        {
          title: 'Tutorials',
          url: '#',
        },
        {
          title: 'Changelog',
          url: '#',
        },
      ],
    },
    {
      title: 'Attendance',
      url: '#',
      icon: CalendarPlus2,
      items: [
        {
          title: 'General',
          url: '#',
        },
        {
          title: 'Team',
          url: '#',
        },
        {
          title: 'Billing',
          url: '#',
        },
        {
          title: 'Limits',
          url: '#',
        },
      ],
    },
    {
      title: 'Payroll',
      url: '#',
      icon: CreditCard,
      items: [
        {
          title: 'General',
          url: '#',
        },
      ],
    },
    {
      title: 'Performance',
      url: '#',
      icon: TrendingUp,
      items: [
        {
          title: 'General',
          url: '#',
        },
      ],
    },
    {
      title: 'Recruitment',
      url: '#',
      icon: BriefcaseBusiness,
      items: [
        {
          title: 'General',
          url: '#',
        },
      ],
    },
  ],
  navSecondary: [
    {
      title: 'Help Center',
      url: '#',
      icon: CircleQuestionMark,
    },
    {
      title: 'Settings',
      url: '#',
      icon: Settings,
    },
  ],
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
    
  return (
    <Sidebar variant="inset" {...props} className="bg-white border">
      <SidebarHeader className="bg-white">
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <a href="#">
                <Image
                  src="/logo/humanlineblack.png"
                  alt="logo"
                  width={120}
                  height={120}
                />
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent className="bg-white">
        <NavMain items={data.navMain} />
        <NavSecondary items={data.navSecondary} className="mt-auto" />
      </SidebarContent>
      <SidebarFooter className="bg-white">
        <ModeToggle />
      </SidebarFooter>
    </Sidebar>
  )
}
