import Image from 'next/image'

export default function MessageIcon({ variant }: { variant: string }) {
  return (
    <div className="relative">
      <Image
        src={
          variant === 'navigationWithSidebar'
            ? '/icons/mailwhite.png'
            : '/icons/mail.png'
        }
        alt="notification"
        width={20}
        height={20}
      />
      {/* notification red dot */}
      <div className="absolute top-0 right-0 w-2 h-2 bg-custom-base-red rounded-full"></div>
    </div>
  )
}
