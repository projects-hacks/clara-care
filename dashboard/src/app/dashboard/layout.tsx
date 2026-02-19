import Navigation from '@/components/Navigation'

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <>
            <div className="mx-auto min-h-dvh w-full max-w-md bg-gradient-to-b from-white to-gray-50 sm:max-w-lg md:max-w-2xl pb-[calc(5rem+env(safe-area-inset-bottom))]">
                {children}
            </div>
            <Navigation />
        </>
    )
}
