import DashboardNavigation from './NavigationWithSidebar'
import MainNavigation from './MainNavigation'
import NavigationWithSidebar from './NavigationWithSidebar'

interface NavigationProps {
  variant: 'navigationWithSidebar' | 'navigation'
  className?: string
}

export default function Navigation({ variant, className }: NavigationProps) {
  if (variant === 'navigationWithSidebar') {
    return <NavigationWithSidebar className={className} />
  }

  return <MainNavigation className={className} />
}
