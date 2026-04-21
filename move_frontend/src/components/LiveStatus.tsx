interface Props {
  connected: boolean
  eventCount?: number
}

export function LiveStatus({ connected, eventCount }: Props) {
  return (
    <div
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium transition-all duration-300 ${
        connected
          ? 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-400'
          : 'bg-slate-800 border border-slate-700 text-slate-500'
      }`}
    >
      <span
        className={`w-1.5 h-1.5 rounded-full ${
          connected ? 'bg-emerald-400 animate-pulse' : 'bg-slate-600'
        }`}
      />
      {connected ? 'LIVE' : 'OFFLINE'}
      {connected && eventCount !== undefined && eventCount > 0 && (
        <span className="text-emerald-600 font-mono">{eventCount}</span>
      )}
    </div>
  )
}
