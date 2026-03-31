export default function ErrorMessage({ message }: { message: string }) {
  return (
    <div className="bg-crimson-dark/20 border border-crimson/30 rounded-lg p-4 text-crimson-light">
      <p className="font-medium">Fehler</p>
      <p className="text-sm mt-1 opacity-80">{message}</p>
    </div>
  )
}
