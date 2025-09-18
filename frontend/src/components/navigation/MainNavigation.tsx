import Image from 'next/image'
import { Menubar } from '../ui/menubar'
import Link from 'next/link'
import NavSearch from './NavSearch'
import MessageIcon from './MessageIcon'
import NotificationIcon from './NotificationIcon'
import { ProfileIcon } from './ProfileIcon'

export default function MainNavigation({ className }: { className?: string }) {
  const user = {
    name: 'John Doe',
    email: 'john.doe@example.com',
    avatar: '/icons/avatar.png',
  }

  return (
    <Menubar className="p-10 px-[70px] bg-[#1F2937] border-0 rounded-none">
      <Image src="/logo/humanline.png" alt="logo" width={120} height={120} />
      <div className="flex gap-8 text-white ml-10 text-[13px]">
        <Link href="/documents">Documents</Link>
        <Link href="/news">News</Link>
        <Link href="/payslip">Payslip</Link>
        <Link href="/report">Report</Link>
      </div>

      {/* Search, message, notification icons, profile */}
      <div className="flex gap-6 ml-auto justify-center items-center">
        <NavSearch variant="dashboard" />
        <MessageIcon variant="dashboard" />
        <NotificationIcon variant="dashboard" />
        <ProfileIcon user={user} variant="dashboard" />
      </div>
    </Menubar>
  )
}
