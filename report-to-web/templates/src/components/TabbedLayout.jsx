import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Play, Pause } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { transitions } from '../theme/motion'

const contentVariants = {
  enter: { opacity: 0, y: 8 },
  center: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -8 },
}

export default function TabbedLayout({
  tabs,
  title,
  subtitle,
  activeTab,
  onTabChange,
  isPresenting,
  setIsPresenting,
  progress,
}) {
  const tabsRef = useRef(null)
  const [scrolled, setScrolled] = useState(false)

  // Scroll-aware sticky header
  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.target.getAttribute('role') !== 'tab') return
      if (e.key === 'ArrowRight') {
        e.preventDefault()
        onTabChange((activeTab + 1) % tabs.length)
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault()
        onTabChange((activeTab - 1 + tabs.length) % tabs.length)
      }
    }
    const el = tabsRef.current
    el?.addEventListener('keydown', handleKeyDown)
    return () => el?.removeEventListener('keydown', handleKeyDown)
  }, [tabs.length, activeTab, onTabChange])

  return (
    <div>
      {/* Header */}
      <header className="bg-bg-secondary px-6 pt-12 pb-5 border-b border-border-primary">
        <div className="max-w-[var(--max-content-width)] mx-auto">
          <h1
            className="font-display text-3xl mb-3 bg-clip-text text-transparent bg-gradient-hero-text"
          >
            {title}
          </h1>
          {subtitle && (
            <p className="font-body text-lg text-text-secondary max-w-[72ch]">
              {subtitle}
            </p>
          )}
        </div>
      </header>

      {/* Tab bar — scroll-aware glassmorphism */}
      <nav
        className={cn(
          'sticky top-0 z-100 border-b border-border-primary transition-[background,box-shadow,backdrop-filter] duration-300',
          scrolled
            ? 'glass shadow-lg'
            : 'bg-bg-secondary'
        )}
        role="tablist"
        ref={tabsRef}
      >
        <div className="max-w-[var(--max-content-width)] mx-auto flex items-center relative">
          <div className="flex gap-0 overflow-x-auto scrollbar-none flex-1 relative">
            {tabs.map((tab, index) => (
              <button
                key={tab.id}
                role="tab"
                aria-selected={activeTab === index}
                aria-controls={`tabpanel-${tab.id}`}
                tabIndex={activeTab === index ? 0 : -1}
                className={cn(
                  'px-5 py-4 font-body text-sm font-medium uppercase tracking-[0.08em] bg-transparent border-none border-b-2 border-b-transparent cursor-pointer whitespace-nowrap transition-[color,background] duration-200 relative rounded-t-sm',
                  activeTab === index
                    ? 'text-accent-primary'
                    : 'text-text-tertiary hover:text-text-secondary hover:bg-[rgba(212,168,83,0.04)]'
                )}
                onClick={() => onTabChange(index)}
              >
                {tab.label}

                {/* Animated tab indicator */}
                {activeTab === index && (
                  <motion.div
                    layoutId="tab-indicator"
                    className="absolute bottom-0 left-0 right-0 h-0.5 rounded-t-sm bg-gradient-tab-indicator shadow-glow-gold"
                    transition={transitions.spring}
                  />
                )}
              </button>
            ))}
          </div>

          {/* Presentation mode toggle */}
          {setIsPresenting && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsPresenting(!isPresenting)}
              aria-label={isPresenting ? 'Stop presentation' : 'Start presentation'}
              className={cn(
                'mr-4 shrink-0 text-xs uppercase tracking-wide font-medium gap-2',
                isPresenting
                  ? 'bg-[rgba(212,168,83,0.12)] border-accent-primary text-accent-primary hover:bg-[rgba(212,168,83,0.2)]'
                  : 'bg-bg-tertiary border-border-primary text-text-tertiary hover:bg-bg-hover'
              )}
            >
              {isPresenting ? <Pause size={14} aria-hidden="true" /> : <Play size={14} aria-hidden="true" />}
              {isPresenting ? 'Stop' : 'Auto'}
            </Button>
          )}
        </div>

        {/* Progress bar for presentation mode */}
        {isPresenting && (
          <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-bg-tertiary">
            <motion.div
              className="h-full bg-gradient-tab-indicator shadow-glow-gold"
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.05, ease: 'linear' }}
            />
          </div>
        )}
      </nav>

      {/* Tab content */}
      <main className="max-w-[var(--max-content-width)] mx-auto px-6 py-12 min-h-[calc(100vh-var(--tab-bar-height))]">
        <AnimatePresence mode="wait">
          <motion.div
            key={tabs[activeTab].id}
            id={`tabpanel-${tabs[activeTab].id}`}
            role="tabpanel"
            aria-labelledby={tabs[activeTab].id}
            variants={contentVariants}
            initial="enter"
            animate="center"
            exit="exit"
            transition={{ duration: 0.3, ease: [0.25, 0.1, 0.25, 1] }}
          >
            {tabs[activeTab].content}
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  )
}
