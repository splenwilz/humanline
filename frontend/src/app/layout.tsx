import type { Metadata } from 'next'
import {
  // Geist,
  // Geist_Mono,
  Inter,
  Manrope,
} from 'next/font/google'
import './globals.css'
import { Toaster } from '@/components/ui/sonner'
import { ThemeProvider } from '@/components/theme/theme-provider'
import { SWRProvider } from '@/lib/swr-config'

// const geistSans = Geist({
//   variable: "--font-geist-sans",
//   subsets: ["latin"],
// });

// const geistMono = Geist_Mono({
//   variable: "--font-geist-mono",
//   subsets: ["latin"],
// });

const manrope = Manrope({
  variable: '--font-manrope',
  subsets: ['latin'],
  display: 'swap',
})

const inter = Inter({
  variable: '--font-inter',
  subsets: ['latin'],
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'Humanline || HR Management Platform',
  description:
    'Humanline is a modern HR management platform that helps you manage your employees and their data.',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body
        className={`${manrope.variable} ${inter.variable} font-manrope antialiased`}
      >
        <SWRProvider>
          <ThemeProvider
            attribute="class"
            defaultTheme="system"
            enableSystem
            disableTransitionOnChange
          >
            {children}
          </ThemeProvider>
        </SWRProvider>
        <Toaster />
      </body>
    </html>
  )
}
