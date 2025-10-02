'use client'

import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { Button } from '@/components/ui/button'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import Image from 'next/image'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'
import Link from 'next/link'
import { EyeIcon, EyeOffIcon, Loader2 } from 'lucide-react'
import { useState } from 'react'
import { useSignin } from '@/data/hooks/useAuth'
import { useRouter } from 'next/navigation'

const formSchema = z.object({
  email: z.email({
    message: 'Invalid email address.',
  }),
  password: z.string().min(8, {
    message: 'Password must be at least 8 characters.',
  }),
})

export default function SigninForm() {
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { signin } = useSignin()
  const router = useRouter()

  // 1. Define your form.
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  })

  // 2. Define a submit handler.
  async function onSubmit(values: z.infer<typeof formSchema>) {
    setIsLoading(true)
    setError(null)

    try {
      const result = await signin(values.email, values.password)

      if (result.success) {
        console.log('Login successful:', result.data)
        // Redirect to dashboard or home page
        router.push('/dashboard') // or wherever you want to redirect after login
      } else {
        setError('Invalid email or password. Please try again.')
      }
    } catch (err) {
      setError('An error occurred. Please try again.')
      console.error('Login error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="space-y-8 w-full p-20 max-w-[600px] mx-auto"
      >
        {/* Login to you account header */}
        <div className="flex flex-col mt-2">
          <Image
            src="/images/ornament.png"
            className="mb-4"
            alt="ornament"
            width={100}
            height={100}
          />
          <h1 className="text-2xl text-center font-medium">
            Login first to your account
          </h1>
        </div>

        {/* Error message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>
                Email Address <span className="text-red-500">*</span>
              </FormLabel>

              <FormControl>
                <Input
                  className="h-12 rounded-[10px] focus-visible:ring-0 focus-visible:border-custom-base-green"
                  placeholder="Input your registered email address"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>
                Password <span className="text-red-500">*</span>
              </FormLabel>
              <FormControl>
                <div className="relative">
                  <Input
                    className="h-12 rounded-[10px] focus-visible:ring-0 focus-visible:border-custom-base-green pr-12"
                    placeholder="Password"
                    {...field}
                    type={showPassword ? 'text' : 'password'}
                  />
                  {showPassword ? (
                    <EyeIcon
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-[#687588] cursor-pointer"
                      onClick={() => setShowPassword(!showPassword)}
                    />
                  ) : (
                    <EyeOffIcon
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-[#687588] cursor-pointer"
                      onClick={() => setShowPassword(!showPassword)}
                    />
                  )}
                </div>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        {/* Remember me and Forgot password */}
        <div className="flex justify-between">
          <div className="flex items-center">
            <Checkbox id="remember-me" />
            <Label
              htmlFor="remember-me"
              className="text-sm ml-2 text-[#687588] "
            >
              Remember me
            </Label>
          </div>
          <Link href="/forgot-password" className="text-sm text-[#687588] ">
            Forgot password?
          </Link>
        </div>
        <Button
          className="w-full h-14 rounded-[10px] bg-[#F1F2F4] hover:bg-custom-grey-900 text-[#A0AEC0] font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          type="submit"
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Logging in...
            </>
          ) : (
            'Login'
          )}
        </Button>

        {/* Or login with */}
        <div className="flex justify-center mt-4">
          <div className="w-full h-1 border-t border-[#E2E8F0]"></div>
          <span className="text-sm text-[#687588] w-full text-center -mt-2">
            Or login with
          </span>
          <div className="w-full h-1 border-t border-[#E2E8F0]"></div>
        </div>
        {/* Google login and Apple login */}
        <div className="flex justify-between">
          <Button
            className="h-12 w-[180px] flex items-center justify-center gap-2 rounded-[10px] "
            variant="outline"
          >
            <Image src="/logo/google.png" alt="Google" width={20} height={20} />
            Google
          </Button>
          <Button
            className="h-12 w-[180px] flex items-center justify-center gap-2 rounded-[10px] "
            variant="outline"
          >
            <Image src="/logo/apple.png" alt="Apple" width={20} height={20} />
            Apple
          </Button>
        </div>

        {/* Don't have an account? */}
        <div className="flex justify-center">
          <p className="text-sm text-[#687588]">
            You’re new in here?{' '}
            <Link href="/signup" className="text-custom-base-green font-medium">
              Create Account
            </Link>
          </p>
        </div>
      </form>
    </Form>
  )
}
