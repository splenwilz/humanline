import { AppSidebar } from '@/components/app-sidebar'
import Navigation from '@/components/navigation/Navigation'
import { SidebarInset, SidebarProvider } from '@/components/ui/sidebar'

export default function ManageEmployeeLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <SidebarProvider className="">
      <AppSidebar />
      <SidebarInset className="bg-custom-grey-50 w-full !m-0 !p-0 flex flex-col min-w-0">
        <Navigation
          variant="navigationWithSidebar"
          className="bg-white w-full"
        />
        {children}
      </SidebarInset>
    </SidebarProvider>
  )
}
