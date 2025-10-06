'use client'

import { Button } from '@/components/ui/button'
import Image from 'next/image'
import React from 'react'
import { OnboardingProvider, useOnboarding } from '@/contexts/OnboardingContext'
import { OnboardForm1 } from '@/components/onboarding/form1'
import { OnboardForm2 } from '@/components/onboarding/form2'
import { OnboardForm3 } from '@/components/onboarding/form3'
import { OnboardForm4 } from '@/components/onboarding/form4'

const OnboardingContent = () => {
  const { currentStep, prevStep, canGoNext, canGoPrev, submitCurrentStep } =
    useOnboarding()

  const renderStepIndicator = () => {
    return (
      <div className="flex flex-row gap-2">
        {[1, 2, 3, 4].map((step) => (
          <div
            key={step}
            className={`w-[20px] h-[20px] rounded-[1px] ${
              step <= currentStep ? 'bg-custom-base-green' : 'bg-[#E9EAEC]'
            }`}
          ></div>
        ))}
      </div>
    )
  }

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return <OnboardForm1 />
      case 2:
        return <OnboardForm2 />
      case 3:
        return <OnboardForm3 />
      case 4:
        return <OnboardForm4 />
      case 5:
        return (
          <div className="p-8 bg-white rounded-[10px] h-[80vh] flex flex-col justify-center items-center text-center">
            <div className="mb-8">
              <div className="w-16 h-16 bg-custom-base-green rounded-full flex items-center justify-center mb-4 mx-auto">
                <svg
                  className="w-8 h-8 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
              <h2 className="text-2xl font-bold mb-4">Onboarding Complete!</h2>
              <p className="text-gray-600 mb-6">
                Thank you for providing your information. Your workspace is
                being set up.
              </p>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-500">
                  All your data has been captured and logged to the console.
                </p>
              </div>
            </div>
          </div>
        )
      default:
        return <OnboardForm1 />
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="border-b-1 border-gray-200 pb-4 h-24">
        <Image
          src="/logo/humanlineblack.png"
          alt="Onboarding"
          className="p-8 pt-10"
          width={200}
          height={200}
        />
      </div>

      <div className="flex">
        <div className="w-1/2 p-16 justify-items-center">
          <div className="gap-4">
            <div className="mb-16 mt-10">
              {renderStepIndicator()}
              <p className="text-md mt-3 max-w-[500px] text-[#A0AEC0] font-medium">
                {currentStep <= 4 ? `Step ${currentStep} of 4` : 'Complete!'}
              </p>
            </div>
            <h1 className="text-[38px] tracking-wide max-w-[500px] leading-12 font-semibold mb-4 font-inter">
              {currentStep === 1 && 'We need some of your Company Information'}
              {currentStep === 2 &&
                'We can now create a workspace for your team.'}
              {currentStep === 3 && 'What is your role in your company?'}
              {currentStep === 4 && 'What will you mainly use Grove HR for?'}
            </h1>
            <p className="text-md mt-8 max-w-[500px] text-[#A0AEC0]">
              {currentStep === 1 &&
                "This data is needed so that we can easily provide solutions according to your company's capacity"}
              {currentStep === 2 &&
                "This data is needed so that we can easily provide solutions according to your company's capacity"}
              {currentStep === 3 &&
                "This data is needed so that we can easily provide solutions according to your company's capacity"}
              {currentStep === 4 &&
                "This data is needed so that we can easily provide solutions according to your company's capacity"}
            </p>

            {/* Navigation buttons */}
            {currentStep < 5 && (
              <div className="flex flex-row gap-4 mt-14">
                {canGoPrev() && (
                  <Button
                    onClick={prevStep}
                    className="cursor-pointer w-48 h-12"
                    variant="outline"
                  >
                    Previous
                  </Button>
                )}

                {currentStep < 5 && (
                  <Button
                    onClick={submitCurrentStep}
                    disabled={!canGoNext()}
                    className="cursor-pointer w-48 h-12"
                  >
                    Continue
                  </Button>
                )}
              </div>
            )}
          </div>
        </div>

        <div className="w-1/2 h-full mr-5">
          <div className="bg-[#F1F2F4] rounded-[10px] p-5 w-full h-full">
            {renderStepContent()}
          </div>
        </div>
      </div>
    </div>
  )
}

const OnboardingPage = () => {
  return (
    <OnboardingProvider>
      <OnboardingContent />
    </OnboardingProvider>
  )
}

export default OnboardingPage
