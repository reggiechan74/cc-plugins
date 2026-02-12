import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

const dotBgMap = {
  completed: 'var(--color-success)',
  active: 'var(--color-accent-primary)',
  warning: 'var(--color-warning)',
  pending: 'var(--color-border-primary)',
}

const badgeClasses = {
  completed: 'bg-[rgba(52,211,153,0.08)] text-success border-[rgba(52,211,153,0.2)]',
  warning: 'bg-[rgba(251,191,36,0.08)] text-warning border-[rgba(251,191,36,0.2)]',
  active: 'bg-[rgba(212,168,83,0.08)] text-accent-primary border-[rgba(212,168,83,0.2)]',
  pending: 'bg-[rgba(212,168,83,0.08)] text-accent-primary border-[rgba(212,168,83,0.2)]',
}

/**
 * Timeline visualization with expandable events.
 *
 * Props:
 * - title: string
 * - events: Array<{ date, title, description?, status?, badge? }>
 */
export default function TimelineView({ title, events }) {
  const [expandedIndex, setExpandedIndex] = useState(null)

  return (
    <div className="my-5 relative">
      {title && (
        <div className="font-body text-sm font-semibold uppercase tracking-wide text-accent-primary mb-5">
          {title}
        </div>
      )}

      <div className="relative pl-12">
        {/* Timeline line */}
        <div
          className="absolute left-[11px] top-0 bottom-0 w-0.5 rounded-sm bg-gradient-timeline"
        />

        {events.map((event, index) => {
          const isActive = expandedIndex === index
          const status = event.status || 'pending'
          const dotBg = dotBgMap[status] || dotBgMap.pending

          return (
            <motion.div
              key={index}
              className="relative mb-5 cursor-pointer"
              role="button"
              tabIndex={0}
              initial={{ opacity: 0, x: -12 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05, duration: 0.4 }}
              onClick={() => setExpandedIndex(isActive ? null : index)}
              onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setExpandedIndex(isActive ? null : index) } }}
            >
              {/* Dot */}
              <div
                className={cn(
                  'absolute -left-[37px] top-1.5 w-3 h-3 rounded-full transition-[border-color,box-shadow,background] duration-200',
                  isActive ? 'border-2 border-text-primary' : 'border-2 border-transparent'
                )}
                style={{
                  background: dotBg,
                  boxShadow: isActive
                    ? `0 0 0 4px var(--color-bg-primary), 0 0 12px ${status === 'completed' ? 'var(--color-success)' : 'var(--color-accent-primary)'}40`
                    : 'none',
                  animation: (status === 'active' && !isActive) ? 'pulse-dot 2s ease-in-out infinite' : 'none',
                }}
              />

              <div className="font-mono text-xs text-text-tertiary mb-1">{event.date}</div>
              <div className={cn(
                'font-body text-base font-semibold mb-2 transition-colors duration-150',
                isActive ? 'text-accent-primary' : 'text-text-primary'
              )}>
                {event.title}
                {event.badge && (
                  <Badge
                    variant="outline"
                    className={cn(
                      'ml-2 text-xs font-medium gap-1 align-middle',
                      badgeClasses[status] || badgeClasses.pending
                    )}
                  >
                    <span className="w-[5px] h-[5px] rounded-full bg-current inline-block" />
                    {event.badge}
                  </Badge>
                )}
              </div>

              <AnimatePresence>
                {isActive && event.description && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.2 }}
                    className="overflow-hidden"
                  >
                    <div className="border border-border-primary rounded-md p-4 mt-3 text-text-secondary text-sm leading-relaxed shadow-sm bg-gradient-surface"
                    >
                      {event.description}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
