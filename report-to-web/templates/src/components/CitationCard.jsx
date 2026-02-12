import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ExternalLink, ChevronDown } from 'lucide-react'
import { Collapsible, CollapsibleTrigger, CollapsibleContent } from '@/components/ui/collapsible'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import { transitions } from '../theme/motion'

/**
 * Expandable citation card.
 *
 * Props:
 * - number: number
 * - title: string
 * - content: string
 * - links: Array<{ label: string, url: string }>
 */
export function CitationCard({ number, title, content, links }) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className="my-3">
      <Collapsible open={isOpen} onOpenChange={setIsOpen}>
        <div className={cn(
          "rounded-r-md border-l-3 border-l-accent-tertiary overflow-hidden transition-[border-color,box-shadow] duration-200",
          isOpen
            ? "border border-accent-tertiary bg-bg-secondary shadow-md"
            : "border border-border-primary bg-bg-secondary shadow-xs"
        )}>
          <CollapsibleTrigger asChild>
            <div
              className="flex items-center justify-between p-3 px-4 cursor-pointer select-none gap-3"
              role="button"
              tabIndex={0}
            >
              <Badge
                variant="outline"
                className="font-mono text-xs font-semibold text-accent-tertiary bg-[rgba(99,102,241,0.08)] border-[rgba(99,102,241,0.2)] rounded-full shrink-0 px-2.5"
              >
                [{number}]
              </Badge>
              <span className="flex-1 font-body text-sm text-text-primary font-medium leading-[1.4]">
                {title}
              </span>
              <motion.div
                animate={{ rotate: isOpen ? 180 : 0 }}
                transition={transitions.base}
                className="shrink-0 flex text-text-tertiary"
              >
                <ChevronDown size={16} />
              </motion.div>
            </div>
          </CollapsibleTrigger>

          <CollapsibleContent forceMount>
            <AnimatePresence>
              {isOpen && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.2 }}
                  className="overflow-hidden"
                >
                  <div className="px-4 pb-4 text-sm text-text-secondary leading-relaxed">
                    {content}

                    {links && links.length > 0 && (
                      <div className="flex flex-col gap-2 mt-3">
                        {links.map((link, i) => (
                          <motion.a
                            key={i}
                            href={link.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-2 text-accent-tertiary text-xs font-mono no-underline px-3 py-2 bg-bg-tertiary rounded-sm transition-[background,box-shadow] duration-150 break-all"
                            whileHover={{
                              y: -1,
                              boxShadow: 'var(--shadow-sm)',
                              background: 'var(--color-bg-hover)',
                            }}
                            transition={transitions.fast}
                          >
                            <ExternalLink size={12} aria-hidden="true" />
                            {link.label}
                          </motion.a>
                        ))}
                      </div>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </CollapsibleContent>
        </div>
      </Collapsible>
    </div>
  )
}

/**
 * Inline citation reference (superscript number).
 */
export function InlineCitation({ number, onClick }) {
  return (
    <span
      className="inline cursor-pointer font-mono text-xs text-accent-tertiary align-super leading-none px-0.5 rounded-sm transition-colors duration-100 hover:bg-[rgba(99,102,241,0.2)]"
      onClick={onClick}
      onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onClick?.() } }}
      role="button"
      tabIndex={0}
      aria-label={`Citation ${number}`}
    >
      [{number}]
    </span>
  )
}

export default CitationCard
