import { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Fuse from 'fuse.js'
import { Search, ChevronDown, BookOpen } from 'lucide-react'
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from '@/components/ui/accordion'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { transitions } from '../theme/motion'

/**
 * Searchable knowledge vault — full report content with fuzzy search.
 *
 * Props:
 * - sections: Array<{ id, title, content: string }>
 */
export default function KnowledgeVault({ sections }) {
  const [query, setQuery] = useState('')
  const [expandedSections, setExpandedSections] = useState([])

  const fuse = useMemo(
    () =>
      new Fuse(sections, {
        keys: ['title', 'content'],
        threshold: 0.35,
        includeMatches: true,
        minMatchCharLength: 2,
      }),
    [sections]
  )

  const filtered = useMemo(() => {
    if (!query.trim()) return sections
    return fuse.search(query).map((r) => r.item)
  }, [query, fuse, sections])

  const expandAll = () => {
    if (expandedSections.length === filtered.length) {
      setExpandedSections([])
    } else {
      setExpandedSections(filtered.map((s) => s.id))
    }
  }

  const highlightText = (text, searchQuery) => {
    if (!searchQuery.trim()) return text
    try {
      const regex = new RegExp(`(${searchQuery.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi')
      const parts = text.split(regex)
      return parts.map((part, i) =>
        regex.test(part) ? (
          <mark key={i} className="bg-[rgba(212,168,83,0.2)] text-accent-primary px-[3px] rounded-sm shadow-[0_0_0_1px_rgba(212,168,83,0.15)]">{part}</mark>
        ) : (
          part
        )
      )
    } catch {
      return text
    }
  }

  const hasQuery = query.trim().length > 0

  return (
    <div className="grid grid-cols-1 gap-5">
      {/* Search */}
      <div className="sticky z-50 bg-bg-primary pb-4" style={{ top: 'calc(var(--tab-bar-height) + 1rem)' }}>
        <div className="relative">
          <Search
            size={18}
            aria-hidden="true"
            className={cn(
              'absolute left-4 top-1/2 -translate-y-1/2 pointer-events-none transition-colors duration-200',
              hasQuery ? 'text-accent-primary' : 'text-text-tertiary'
            )}
          />
          <Input
            type="text"
            placeholder="Search the knowledge vault\u2026"
            aria-label="Search the knowledge vault"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="pl-12 pr-5 py-4 font-mono bg-bg-primary border-border-primary text-text-primary shadow-inset focus-visible:border-accent-primary focus-visible:ring-[rgba(212,168,83,0.15)] h-auto"
          />
        </div>
        <div className="flex justify-between items-center mt-2">
          <div className="font-mono text-xs text-text-tertiary">
            {query ? `${filtered.length} of ${sections.length} sections` : `${sections.length} sections`}
          </div>
          <Button
            variant="outline"
            size="xs"
            onClick={expandAll}
            className="text-accent-secondary border-border-primary hover:border-accent-secondary hover:text-accent-secondary"
          >
            {expandedSections.length === filtered.length ? 'Collapse all' : 'Expand all'}
          </Button>
        </div>
      </div>

      {/* Sections */}
      <div className="flex flex-col gap-3">
        {filtered.length === 0 ? (
          <div className="text-center py-24 px-5 text-text-tertiary">
            <Search size={48} className="text-text-tertiary opacity-30 mb-4 mx-auto" />
            <div className="font-display text-xl text-text-tertiary mb-2">
              No sections match
            </div>
            <div className="text-sm">
              Try a different search term
            </div>
          </div>
        ) : (
          <Accordion
            type="multiple"
            value={expandedSections}
            onValueChange={setExpandedSections}
            className="flex flex-col gap-3"
          >
            {filtered.map((section, index) => {
              const isOpen = expandedSections.includes(section.id)
              return (
                <motion.div
                  key={section.id}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.03, duration: 0.3 }}
                >
                  <AccordionItem
                    value={section.id}
                    className={cn(
                      'bg-bg-secondary rounded-md overflow-hidden border-b-0 transition-[border-color,box-shadow] duration-200',
                      isOpen
                        ? 'border border-border-accent shadow-md'
                        : 'border border-border-primary shadow-xs'
                    )}
                  >
                    <AccordionTrigger className="px-5 py-4 hover:no-underline gap-3 [&>svg]:text-text-tertiary">
                      <div className="flex items-center gap-3 flex-1 text-left">
                        <BookOpen size={18} aria-hidden="true" className="text-accent-primary shrink-0" />
                        <span className="font-display text-lg text-text-primary">
                          {highlightText(section.title, query)}
                        </span>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent className="px-5 pb-5 text-text-secondary text-base leading-[1.7]">
                      {typeof section.content === 'string'
                        ? section.content.split('\n').map((line, i) => (
                            <p key={i} className="mb-3">
                              {highlightText(line, query)}
                            </p>
                          ))
                        : section.content}
                    </AccordionContent>
                  </AccordionItem>
                </motion.div>
              )
            })}
          </Accordion>
        )}
      </div>
    </div>
  )
}
