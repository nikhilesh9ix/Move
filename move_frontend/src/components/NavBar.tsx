'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

export function NavBar() {
  const pathname = usePathname()

  const today = new Intl.DateTimeFormat('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  }).format(new Date())

  return (
    <nav
      className="sticky top-0 z-50 backdrop-blur-xl"
      style={{
        background: 'rgba(2,6,23,0.85)',
        borderBottom: '1px solid rgba(255,255,255,0.05)',
        boxShadow: '0 1px 0 rgba(255,255,255,0.03)',
      }}
    >
      <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
        <div className="flex items-center">
          <span
            className="text-lg font-extrabold tracking-[-0.045em]"
            style={{
              background: 'linear-gradient(90deg, #fff 0%, rgba(255,255,255,0.55) 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
            }}
          >
            move
          </span>
        </div>

        {/* Nav links */}
        <div className="flex items-center gap-1">
          {[
            { href: '/', label: 'Dashboard' },
            { href: '/analyze', label: 'Analyze' },
          ].map(({ href, label }) => {
            const active = pathname === href
            return (
              <Link
                key={href}
                href={href}
                className="px-3 py-1.5 rounded-lg text-sm transition-all duration-150"
                style={
                  active
                    ? {
                        background: 'rgba(59,130,246,0.1)',
                        color: '#93c5fd',
                        border: '1px solid rgba(59,130,246,0.2)',
                      }
                    : {
                        color: 'rgba(100,116,139,0.8)',
                        border: '1px solid transparent',
                      }
                }
              >
                {label}
              </Link>
            )
          })}
        </div>

        {/* Date */}
        <span
          className="text-xs font-mono hidden md:block"
          style={{ color: 'rgba(71,85,105,0.8)' }}
        >
          {today}
        </span>
      </div>
    </nav>
  )
}
