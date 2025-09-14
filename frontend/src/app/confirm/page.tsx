'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { XCircle, Loader2 } from 'lucide-react'
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { Button } from '@/components/ui/button'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormMessage,
} from '@/components/ui/form'
import {
  InputOTP,
  InputOTPGroup,
  InputOTPSlot,
} from '@/components/ui/input-otp'
import { getPendingEmail } from '@/lib/auth'
import { useOTPVerification, useResendOTP, useSignin } from '@/data/hooks'
import Image from 'next/image'
import Link from 'next/link'

interface ConfirmationStatus {
  loading: boolean
  success: boolean
  error: string | null
  userEmail: string | null
}

const OTPFormSchema = z.object({
  pin: z
    .string()
    .min(6, {
      message: 'Your one-time password must be 6 characters.',
    })
    .max(6, {
      message: 'Your one-time password must be 6 characters.',
    }),
})

export default function EmailConfirmationPage() {
  const router = useRouter()
  const [status, setStatus] = useState<ConfirmationStatus>({
    loading: false,
    success: false,
    error: null,
    userEmail: null,
  })
  const [userEmail, setUserEmail] = useState<string>('')
  const [isAutoLoggingIn, setIsAutoLoggingIn] = useState<boolean>(false)

  const { verifyOTP, isLoading: isVerifying } = useOTPVerification()
  const { resendOTP, isLoading: isResending } = useResendOTP()
  const { signin } = useSignin()

  const form = useForm<z.infer<typeof OTPFormSchema>>({
    resolver: zodResolver(OTPFormSchema),
    defaultValues: {
      pin: '',
    },
  })

  // Get email from localStorage instead of URL params
  useEffect(() => {
    const email = getPendingEmail()
    if (email) {
      setUserEmail(email)
    } else {
      // No pending email found, redirect to signup
      // router.push('/signup')
    }
  }, [router])

  // Auto-login after successful OTP verification
  useEffect(() => {
    if (status.success && userEmail && !isAutoLoggingIn) {
      handleAutoLogin()
    }
  }, [status.success, userEmail, isAutoLoggingIn])

  const handleAutoLogin = async () => {
    if (!userEmail) return

    setIsAutoLoggingIn(true)

    try {
      // The OTP verification already stored the tokens in localStorage
      // We just need to redirect to the onboarding page

      toast.success('Login successful!', {
        description: 'Welcome to Humanline! Setting up your workspace...',
      })

      // Redirect to onboarding page after a short delay
      setTimeout(() => {
        router.push('/onboarding')
      }, 1500)
    } catch (error) {
      console.error('Auto-login failed:', error)
      toast.error('Auto-login failed', {
        description: 'Please login manually.',
      })

      // Fallback to manual login
      setTimeout(() => {
        router.push('/signin')
      }, 2000)
    } finally {
      setIsAutoLoggingIn(false)
    }
  }

  const onSubmit = async (data: z.infer<typeof OTPFormSchema>) => {
    if (!userEmail) {
      toast.error('Email not found', {
        description: 'Please try signing up again.',
      })
      return
    }

    try {
      const result = await verifyOTP(userEmail, data.pin)

      if (result.success && result.data) {
        toast.success('OTP verified successfully!', {
          description:
            'Your account is now active. You can sign in to continue.',
        })

        // Mark as successful
        setStatus({
          loading: false,
          success: true,
          error: null,
          userEmail: result.data.user?.email || null,
        })

        // Redirect to dashboard or home after a short delay
        setTimeout(() => {
          router.push('/onboarding')
        }, 2000)
      } else {
        setStatus({
          loading: false,
          success: false,
          error:
            result.error instanceof Error
              ? result.error.message
              : 'Failed to verify OTP',
          userEmail: null,
        })
      }
    } catch (error) {
      console.error('OTP verification error:', error)
      toast.error('OTP verification failed', {
        description:
          error instanceof Error
            ? error.message
            : 'Please check your OTP and try again.',
      })
    }
  }

  const handleSignIn = () => {
    router.push('/signin')
  }

  const handleGoHome = () => {
    router.push('/')
  }

  const handleResendOTP = async () => {
    if (!userEmail) {
      toast.error('Email not found', {
        description: 'Please try signing up again.',
      })
      return
    }

    try {
      const result = await resendOTP(userEmail)

      if (result.success) {
        toast.success('OTP resent successfully!', {
          description: 'Please check your email for the new OTP code.',
        })
      } else {
        toast.error('Failed to resend OTP', {
          description:
            result.error instanceof Error
              ? result.error.message
              : 'Please try again.',
        })
      }
    } catch (error) {
      toast.error('Network error', {
        description: 'Please check your connection and try again.',
      })
    }
  }

  // Show success state with auto-login
  if (status.success) {
    return (
      <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
        <Image
          src="/images/otpbg.png"
          alt="Onboarding Background"
          width={500}
          height={500}
          className="absolute top-0 left-0 w-full h-full object-cover"
        />
        <div className="w-full max-w-md mx-4 bg-white/95 backdrop-blur-sm rounded-lg shadow-lg p-8 text-center relative z-10">
          <div className="flex justify-center items-center mb-6">
            <Image
              src="/icons/success.png"
              alt="Success"
              width={265}
              height={140}
            />
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Email verified successfully!
          </h2>
          <p className="text-gray-600 mb-6">
            {isAutoLoggingIn
              ? 'Automatically logging you in...'
              : 'Email verified successfully!'}
          </p>

          {/* Loading indicator */}
          <div className="flex flex-col items-center space-y-4 mb-6">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-custom-base-green"></div>
            <p className="text-sm text-gray-500">
              {isAutoLoggingIn
                ? 'Setting up your workspace...'
                : 'Preparing your account...'}
            </p>
          </div>

          <div className="space-y-3">
            <Button
              onClick={() => router.push('/onboarding')}
              variant="outline"
              className="w-full"
            >
              Go to Onboarding
            </Button>
          </div>
        </div>
      </div>
    )
  }

  // Show error state
  if (status.error) {
    return (
      <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
        <Image
          src="/images/otpbg.png"
          alt="Onboarding Background"
          width={1000}
          height={1000}
          className="absolute top-0 left-0 w-full h-full object-cover"
        />
        <div className="w-full max-w-md mx-4 bg-white/95 backdrop-blur-sm rounded-lg shadow-lg p-8 text-center relative z-10">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-red-100">
            <XCircle className="h-8 w-8 text-red-600" />
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Verification Failed
          </h2>
          <p className="text-gray-600 mb-6">{status.error}</p>
          <div className="space-y-3">
            <Button onClick={() => window.location.reload()} className="w-full">
              Try Again
            </Button>
            <Button onClick={handleGoHome} variant="outline" className="w-full">
              Go Home
            </Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
      <Image
        src="/images/otpbg.png"
        alt="Onboarding Background"
        width={1000}
        height={1000}
        className="absolute top-0 left-0 w-full h-full object-cover"
      />
      <div className="w-full max-w-md mx-4 bg-white/95 backdrop-blur-sm rounded-lg shadow-lg p-8 relative z-10">
        <div className="flex flex-col items-center justify-center text-center space-y-4 mb-6">
          <Image
            src="/logo/humanlineblack.png"
            alt="Success"
            width={100}
            height={100}
          />

          <h2 className="text-xl font-semibold text-gray-900">
            OTP Verification
          </h2>
          <p className="text-gray-600 text-sm">
            We have sent a verification code to email address{' '}
            <b>{userEmail ? userEmail : 'pristia@gmail.com'}</b>.{' '}
            <Link href="/signup" className="text-custom-base-green">
              Wrong Email?
            </Link>
          </p>
        </div>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6 ">
            <FormField
              control={form.control}
              name="pin"
              render={({ field }) => (
                <FormItem>
                  <FormControl className="">
                    <InputOTP maxLength={6} {...field}>
                      <InputOTPGroup className="flex gap-1 justify-center items-center ml-18">
                        <InputOTPSlot index={0} />
                        <InputOTPSlot index={1} />
                        <InputOTPSlot index={2} />
                        <InputOTPSlot index={3} />
                        <InputOTPSlot index={4} />
                        <InputOTPSlot index={5} />
                      </InputOTPGroup>
                    </InputOTP>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="space-y-3 mx-8">
              <Button
                type="submit"
                className="w-full cursor-pointer"
                disabled={isVerifying}
              >
                {isVerifying ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Verifying...
                  </>
                ) : (
                  'Submit'
                )}
              </Button>
            </div>
          </form>
        </Form>
      </div>
    </div>
  )
}
