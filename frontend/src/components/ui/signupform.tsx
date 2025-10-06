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
import { useState } from 'react'
import { EyeIcon, EyeOffIcon, Loader2 } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { useSignup } from '@/data/hooks'

const formSchema = z.object({
  fullName: z.string().min(1, {
    message: 'Full name is required.',
  }),
  email: z.email({
    message: 'Invalid email address.',
  }),
  password: z.string().min(8, {
    message: 'Password must be at least 8 characters.',
  }),
})

export default function SignupForm() {
  const [showPassword, setShowPassword] = useState(false)
  const router = useRouter()
  const { signup, isLoading } = useSignup()

  // 1. Define your form.
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: '',
      password: '',
      fullName: '',
    },
  })

  // 2. Define a submit handler.
  async function onSubmit(values: z.infer<typeof formSchema>) {
    try {
      const result = await signup(
        values.email,
        values.password,
        values.fullName,
      )

      // Registration successful - tokens are handled by auth service

      // Handle different response types based on email confirmation setting
      if (result.type === 'immediate_login') {
        // Email confirmation disabled - user is logged in immediately
        toast.success('Account created successfully!', {
          description: 'Welcome to Humanline! You are now logged in.',
        })

        // Let middleware handle routing based on needs_onboarding
        router.push('/dashboard')
      } else if (result.type === 'email_confirmation_required') {
        // Email confirmation enabled - user needs to check email
        toast.success('Account created successfully!', {
          description:
            result.message ||
            'Please check your email for a confirmation link.',
        })

        // Redirect to confirmation page
        router.push('/confirm')
      } else {
        // Fallback for unexpected response type
        toast.success('Account created successfully!', {
          description: 'Please check your email for further instructions.',
        })

        router.push('/confirm')
      }
    } catch (error) {
      console.error('Unexpected error:', error)
      toast.error('Network error', {
        description: 'Please check your connection and try again.',
      })
    }
  }

  return (
    <div className="flex flex-col justify-between h-full">
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="space-y-8 w-full p-20 pb-0 max-w-[700px] mx-auto"
        >
          {/* Login to you account header */}
          <div className="flex flex-col mt-2">
            <h1 className="text-3xl font-medium">
              Manage employees easily starting from now!
            </h1>
            <p className=" text-[#687588] mt-3">Get started for free today!</p>
          </div>
          {/* Full name */}
          <FormField
            control={form.control}
            name="fullName"
            render={({ field }) => (
              <FormItem>
                <FormLabel>
                  Name <span className="text-red-500">*</span>
                </FormLabel>
                <FormControl>
                  <Input
                    className="h-12 rounded-[10px] focus-visible:ring-0 focus-visible:border-custom-base-green"
                    placeholder="Input your full name"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="email"
            render={({ field }) => (
              <FormItem>
                <FormLabel>
                  Work Email<span className="text-red-500">*</span>
                </FormLabel>

                <FormControl>
                  <Input
                    className="h-12 rounded-[10px] focus-visible:ring-0 focus-visible:border-custom-base-green"
                    placeholder="example@company.com"
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
            className="w-full h-14 cursor-pointer rounded-[10px] bg-[#F1F2F4] hover:bg-custom-grey-900 text-[#A0AEC0] font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            type="submit"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Creating Account...
              </>
            ) : (
              'Create Account'
            )}
          </Button>

          {/* Or register with */}
          <div className="flex justify-center mt-4">
            <div className="w-full h-1 border-t border-[#E2E8F0]"></div>
            <span className="text-sm text-[#687588] w-full text-center -mt-2">
              Or register with
            </span>
            <div className="w-full h-1 border-t border-[#E2E8F0]"></div>
          </div>
          {/* Google login and Apple login */}
          <div className="flex justify-between">
            <Button
              className="h-12 w-[180px] flex items-center justify-center gap-2 rounded-[10px] "
              variant="outline"
            >
              <Image
                src="/logo/google.png"
                alt="Google"
                width={20}
                height={20}
              />
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

          {/* Already have an account? */}
          <div className="flex  ">
            <p className="text-sm text-[#687588]">
              Already have an account?{' '}
              <Link
                href="/signin"
                className="text-custom-base-green font-medium"
              >
                Login Here
              </Link>
            </p>
          </div>
        </form>
      </Form>
      {/* Terms and conditions */}
      <div className="flex w-full mt-20 p-20 pb-0 max-w-[700px] mx-auto">
        <div className="flex justify-between gap-2 w-full">
          <p className="text-sm text-[#687588]">
            © 2023 Humanline . All rights reserved.{' '}
          </p>
          <Link href="/terms" className="text-black text-sm font-medium ">
            Terms and Conditions
          </Link>

          <Link href="/privacy" className="text-black text-sm font-medium">
            Privacy Policy
          </Link>
        </div>
      </div>
    </div>
  )
}
