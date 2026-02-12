import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { ExternalLink } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

const dotClasses = {
  verified: 'bg-success',
  estimate: 'bg-warning',
  illustrative: 'bg-info',
}

const badgeStyles = {
  verified: 'bg-[rgba(52,211,153,0.08)] text-success border-[rgba(52,211,153,0.25)]',
  estimate: 'bg-[rgba(251,191,36,0.08)] text-warning border-[rgba(251,191,36,0.25)]',
  illustrative: 'bg-[rgba(96,165,250,0.08)] text-info border-[rgba(96,165,250,0.25)]',
}

const sectionVariants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0 },
}

/**
 * Custom markdown components for rendering report content
 * with the dark professional theme.
 */
const markdownComponents = {
  h3: ({ children }) => (
    <h3 className="font-display text-text-primary mb-4 pb-3 relative text-xl">{children}</h3>
  ),
  h4: ({ children }) => (
    <h4 className="font-display text-text-primary mb-4 pb-3 relative text-lg">{children}</h4>
  ),
  p: ({ children }) => {
    if (typeof children === 'string' || (Array.isArray(children) && typeof children[0] === 'string')) {
      const text = Array.isArray(children) ? children : [children]
      return (
        <p className="max-w-[72ch] mb-4">
          {text.map((child, i) => {
            if (typeof child !== 'string') return child
            return child
              .replace(/\*\*\[VERIFIED\]\*\*/g, '%%VERIFIED%%')
              .replace(/\*\*\[PROFESSIONAL ESTIMATE\]\*\*/g, '%%ESTIMATE%%')
              .replace(/\*\*\[ILLUSTRATIVE FRAMEWORK\]\*\*/g, '%%ILLUSTRATIVE%%')
              .split(/(%%VERIFIED%%|%%ESTIMATE%%|%%ILLUSTRATIVE%%)/)
              .map((part, j) => {
                if (part === '%%VERIFIED%%')
                  return (
                    <Badge
                      key={`${i}-${j}`}
                      variant="outline"
                      className={cn('font-mono text-xs font-semibold tracking-wide gap-1.5 mr-2', badgeStyles.verified)}
                    >
                      <span className={cn('w-1.5 h-1.5 rounded-full shrink-0', dotClasses.verified)} />
                      VERIFIED
                    </Badge>
                  )
                if (part === '%%ESTIMATE%%')
                  return (
                    <Badge
                      key={`${i}-${j}`}
                      variant="outline"
                      className={cn('font-mono text-xs font-semibold tracking-wide gap-1.5 mr-2', badgeStyles.estimate)}
                    >
                      <span className={cn('w-1.5 h-1.5 rounded-full shrink-0', dotClasses.estimate)} />
                      ESTIMATE
                    </Badge>
                  )
                if (part === '%%ILLUSTRATIVE%%')
                  return (
                    <Badge
                      key={`${i}-${j}`}
                      variant="outline"
                      className={cn('font-mono text-xs font-semibold tracking-wide gap-1.5 mr-2', badgeStyles.illustrative)}
                    >
                      <span className={cn('w-1.5 h-1.5 rounded-full shrink-0', dotClasses.illustrative)} />
                      ILLUSTRATIVE
                    </Badge>
                  )
                return part
              })
          })}
        </p>
      )
    }
    return <p className="max-w-[72ch] mb-4">{children}</p>
  },
  a: ({ href, children }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-accent-tertiary no-underline border-b border-transparent hover:border-accent-tertiary transition-[border-color] duration-150"
    >
      {children}
      <ExternalLink size={12} aria-hidden="true" className="inline ml-1 align-middle opacity-60" />
    </a>
  ),
  blockquote: ({ children }) => (
    <blockquote className="border-l-3 border-l-accent-primary py-4 px-5 my-5 bg-bg-secondary rounded-r-md italic text-text-secondary">
      {children}
    </blockquote>
  ),
  strong: ({ children }) => (
    <strong className="text-text-primary font-semibold">{children}</strong>
  ),
  table: ({ children }) => (
    <div className="overflow-x-auto my-5">
      <table className="w-full border-collapse text-sm">
        {children}
      </table>
    </div>
  ),
}

/**
 * Renders a report section with animation on scroll.
 *
 * Props:
 * - id: string
 * - title: string
 * - content: string — Markdown content
 * - level?: number — Heading level (default 3)
 * - index?: number — Section index for alternating background
 * - children?: ReactNode
 */
export default function SectionRenderer({ id, title, content, level = 3, index, children }) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-50px' })

  const hasAltBackground = typeof index === 'number' && index % 2 === 1

  return (
    <motion.section
      ref={ref}
      id={id}
      className={cn(
        'mb-16',
        hasAltBackground && 'p-6 rounded-lg -mx-6 bg-gradient-gold-subtle'
      )}
      variants={sectionVariants}
      initial="hidden"
      animate={isInView ? 'visible' : 'hidden'}
      transition={{ duration: 0.4, ease: [0.25, 0.1, 0.25, 1] }}
    >
      {title && (() => {
        const Heading = level === 2 ? 'h2' : 'h3'
        return (
          <Heading className={cn(
            'font-display text-text-primary mb-4 pb-3 relative',
            level === 2 ? 'text-2xl' : 'text-xl'
          )}>
            {title}
            {/* Gradient accent line */}
            <span className="absolute bottom-0 left-0 w-[60px] h-0.5 rounded-sm block bg-gradient-accent-line" />
          </Heading>
        )
      })()}

      <div className="text-text-primary leading-[1.7]">
        <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
          {content}
        </ReactMarkdown>
      </div>

      {children}
    </motion.section>
  )
}
