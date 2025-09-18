import { Menubar } from '../ui/menubar'
import Link from 'next/link'
import NavSearch from './NavSearch'
import MessageIcon from './MessageIcon'
import NotificationIcon from './NotificationIcon'
import { ProfileIcon } from './ProfileIcon'
import { SidebarTrigger } from '../ui/sidebar'

export default function NavigationWithSidebar({
  className,
}: {
  className?: string
}) {
  const user = {
    name: 'John Doe',
    email: 'john.doe@example.com',
    avatar: '/icons/avatar.png',
  }

  return (
    <Menubar className={`p-10 px-10 border-0 rounded-none ${className}`}>
      <SidebarTrigger className="-ml-1" />
      <NavSearch variant="navigationWithSidebar" />

      <div className="flex gap-8 ml-10 text-[13px] text-custom-grey-900">
        <Link href="/documents">Documents</Link>
        <Link href="/news">News</Link>
        <Link href="/payslip">Payslip</Link>
        <Link href="/report">Report</Link>
      </div>

      {/* Search, message, notification icons, profile */}
      <div className="flex gap-6 ml-auto justify-center items-center">
        <MessageIcon variant="navigationWithSidebar" />
        <NotificationIcon variant="navigationWithSidebar" />
        <ProfileIcon user={user} variant="navigationWithSidebar" />
      </div>
    </Menubar>
  )
}
