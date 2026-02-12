export default function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center py-16" role="status" aria-label="Loading">
      <div className="h-8 w-8 animate-spin rounded-full border-[3px] border-gray-200 border-t-clara-600" />
    </div>
  )
}
