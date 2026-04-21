function Bone({ className }: { className: string }) {
  return <div className={`animate-pulse rounded-lg bg-slate-800 ${className}`} />
}

export function WhyCardSkeleton() {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 space-y-6">
      <div className="flex justify-between">
        <Bone className="h-4 w-52" />
        <Bone className="h-4 w-24" />
      </div>
      <Bone className="h-14 w-40" />
      <div className="space-y-3 pt-2">
        <Bone className="h-3 w-32" />
        <Bone className="h-5 w-full" />
        <Bone className="h-5 w-4/5" />
        <Bone className="h-5 w-3/5" />
      </div>
      <div className="pt-2 space-y-2 border-t border-slate-800">
        <Bone className="h-3 w-full" />
        <Bone className="h-3 w-4/5" />
        <Bone className="h-3 w-3/5" />
      </div>
    </div>
  )
}

export function PortfolioSkeleton() {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-5">
      <Bone className="h-4 w-40" />
      <Bone className="h-10 w-36" />
      <div className="space-y-2 pt-2">
        {[1, 2, 3].map((i) => (
          <div key={i} className="flex justify-between">
            <Bone className="h-4 w-16" />
            <Bone className="h-4 w-14" />
          </div>
        ))}
      </div>
    </div>
  )
}

export function ChartSkeleton() {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex items-center justify-center">
      <Bone className="h-52 w-52 rounded-full" />
    </div>
  )
}
