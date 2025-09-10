import SigninForm from '@/components/ui/signinform'
import Image from 'next/image'

export default function Signin() {
  return (
    <div className="flex justify-center items-center h-screen">
      <div className="w-1/2 h-full">
        <div className="flex justify-center items-center h-[65vh]">
          <Image
            src="/images/onboarding.png"
            className="w-full h-full object-cover"
            alt="onboarding"
            width={500}
            height={500}
          />
        </div>
        <div className="flex flex-col p-14 h-[35vh] bg-custom-grey-900 border-t-4 border-t-custom-base-green">
          <Image
            src="/logo/humanline.png"
            className=""
            alt="logo"
            width={150}
            height={150}
          />
          <h1 className="text-white text-5xl leading-14 font-bold mt-7">
            Let’s empower your employees today.
          </h1>
          <p className="text-white text-lg mt-6">
            We help to complete all your conveyancing needs easily
          </p>
        </div>
      </div>
      <div className="w-1/2 h-full flex justify-center">
        <SigninForm />
      </div>
    </div>
  )
}
