'use client'

import { ChevronDown, LayoutGrid, type LucideIcon } from 'lucide-react'
import { usePathname } from 'next/navigation'

import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible'
import {
  SidebarGroup,
  SidebarMenu,
  SidebarMenuAction,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
} from '@/components/ui/sidebar'
import { Button } from '../ui/button'
import Link from 'next/link'

export default function NavMain({
  items,
}: {
  items: {
    title: string
    url: string
    icon: LucideIcon
    isActive?: boolean
    items?: {
      title: string
      url: string
    }[]
  }[]
}) {
  const pathname = usePathname()

  const isActive = (url: string) => {
    if (url === '/dashboard') {
      return pathname === '/dashboard'
    }
    return pathname.startsWith(url)
  }

  const isParentActive = (item: { url: string; items?: { url: string }[] }) => {
    // Check if the parent item itself is active
    if (isActive(item.url)) {
      return true
    }

    // Check if any sub-item is active
    if (item.items) {
      return item.items.some((subItem) => isActive(subItem.url))
    }

    return false
  }

  return (
    <SidebarGroup>
      <Link href={'/dashboard'} className="w-full my-4 mb-8">
        <Button
          className={`flex justify-between w-full cursor-pointer h-11 ${isActive('/dashboard') ? 'bg-custom-base-green hover:bg-green-600' : 'bg-[#0CAF60] hover:bg-custom-base-green'}`}
        >
          <span className="text-white font-bold">Dashboard</span>
          <LayoutGrid className="text-white" />
        </Button>
      </Link>
      <SidebarMenu>
        {items.map((item) => (
          <Collapsible
            key={item.title}
            asChild
            defaultOpen={isParentActive(item)}
          >
            <SidebarMenuItem className="mb-4">
              <SidebarMenuButton asChild tooltip={item.title}>
                <Link href={item.url}>
                  <item.icon
                    className={
                      isActive(item.url)
                        ? 'text-custom-base-green'
                        : 'text-custom-grey-500'
                    }
                  />
                  <span
                    className={`font-bold ${isActive(item.url) ? 'text-custom-base-green' : 'text-custom-grey-900'}`}
                  >
                    {item.title}
                  </span>
                </Link>
              </SidebarMenuButton>
              {item.items?.length ? (
                <>
                  <CollapsibleTrigger asChild>
                    <SidebarMenuAction className="data-[state=open]:rotate-90">
                      <ChevronDown className="text-custom-grey-400" />
                      <span className="sr-only">Toggle</span>
                    </SidebarMenuAction>
                  </CollapsibleTrigger>
                  <CollapsibleContent>
                    <SidebarMenuSub className="mt-4">
                      {item.items?.map((subItem) => (
                        <SidebarMenuSubItem
                          key={subItem.title}
                          className="mb-3"
                        >
                          <SidebarMenuSubButton asChild>
                            <Link href={subItem.url}>
                              <span
                                className={`font-semibold text-sm ${isActive(subItem.url) ? 'text-custom-base-green' : 'text-custom-grey-900'}`}
                              >
                                {subItem.title}
                              </span>
                            </Link>
                          </SidebarMenuSubButton>
                        </SidebarMenuSubItem>
                      ))}
                    </SidebarMenuSub>
                  </CollapsibleContent>
                </>
              ) : null}
            </SidebarMenuItem>
          </Collapsible>
        ))}
      </SidebarMenu>
    </SidebarGroup>
  )
}
