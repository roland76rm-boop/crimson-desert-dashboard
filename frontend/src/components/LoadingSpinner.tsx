export default function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center py-12">
      <div
        className="w-7 h-7 animate-spin"
        style={{ border: '2px solid var(--accent)', borderTopColor: 'transparent', borderRadius: '50%' }}
      />
    </div>
  )
}
