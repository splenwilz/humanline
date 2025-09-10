import SignupForm from '@/components/ui/signupform'
import Image from 'next/image'

export default function Signup() {
  return (
    <div className="flex ">
      <div className="w-1/2 h-full">
        <SignupForm />
      </div>
      <div className="w-1/2 h-full flex flex-col bg-custom-base-green">
        <div className="p-20 pb-10">
          <h1 className="text-white text-4xl font-medium w-[400px]">
            Let&apos;s empower your employees today.
          </h1>
          <p className="text-white mt-4">
            We help to complete all your conveyancing needs easily
          </p>
        </div>
        <div className="flex-1 relative pl-20">
          <Image
            src="/images/signupimg.png"
            className="w-full object-cover rounded-lg"
            alt="signupimg"
            width={500}
            height={500}
          />
        </div>
      </div>
    </div>
  )
}
