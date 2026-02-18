import Navigation from '@/components/Navigation'

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <>
            <div className="mx-auto min-h-screen max-w-md bg-gray-50 pb-20">
                {children}
            </div>
            <Navigation />
        </>
    )
}
