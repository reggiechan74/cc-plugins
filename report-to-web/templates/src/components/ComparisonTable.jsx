import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  Table,
  TableHeader,
  TableBody,
  TableHead,
  TableRow,
  TableCell,
} from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { transitions } from '../theme/motion'

/**
 * Interactive comparison table.
 *
 * Props:
 * - title: string
 * - headers: string[]
 * - rows: Array<{ dimension: string, values: string[] }>
 * - highlightColumn?: number
 * - filters?: string[] | boolean
 */
export default function ComparisonTable({ title, headers, rows, highlightColumn, filters }) {
  const [visibleCols, setVisibleCols] = useState(() => new Set(headers.map((_, i) => i)))
  const [hoveredRow, setHoveredRow] = useState(null)

  const toggleCol = (index) => {
    setVisibleCols((prev) => {
      const next = new Set(prev)
      if (next.has(index) && next.size > 1) {
        next.delete(index)
      } else {
        next.add(index)
      }
      return next
    })
  }

  return (
    <div className="bg-bg-secondary border border-border-primary rounded-md overflow-hidden my-5 shadow-md">
      <div className="flex justify-between items-center px-5 py-4 border-b border-border-primary bg-gradient-surface"
      >
        <div className="font-body text-sm font-semibold uppercase tracking-wide text-accent-primary">
          {title}
        </div>
        {filters && (
          <div className="flex gap-2">
            {headers.slice(1).map((h, i) => (
              <motion.div key={h} whileTap={{ scale: 0.95 }} transition={transitions.fast}>
                <Button
                  variant={visibleCols.has(i + 1) ? 'default' : 'ghost'}
                  size="xs"
                  onClick={() => toggleCol(i + 1)}
                  className={cn(
                    visibleCols.has(i + 1)
                      ? 'bg-accent-primary text-bg-primary hover:bg-accent-primary/90'
                      : 'bg-bg-primary text-text-secondary hover:bg-bg-tertiary'
                  )}
                >
                  {h}
                </Button>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      <Table>
        <TableHeader>
          <TableRow className="border-b-border-primary hover:bg-transparent">
            {headers.map((header, i) => (
              visibleCols.has(i) && (
                <TableHead
                  key={i}
                  className={cn(
                    'bg-bg-tertiary text-xs uppercase tracking-wide font-semibold px-4 py-3 sticky z-10',
                    i === highlightColumn ? 'text-accent-primary' : 'text-text-secondary'
                  )}
                  style={{ top: 'var(--tab-bar-height)' }}
                >
                  {header}
                </TableHead>
              )
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((row, rowIndex) => (
            <motion.tr
              key={rowIndex}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: rowIndex * 0.03, duration: 0.3 }}
              onMouseEnter={() => setHoveredRow(rowIndex)}
              onMouseLeave={() => setHoveredRow(null)}
              className="border-b border-border-primary transition-colors duration-150"
              style={{
                background: hoveredRow === rowIndex ? 'var(--color-bg-hover)' : 'transparent',
              }}
            >
              {[row.dimension, ...row.values].map((cell, colIndex) => (
                visibleCols.has(colIndex) && (
                  <TableCell
                    key={colIndex}
                    className={cn(
                      'px-4 py-3 align-top leading-normal whitespace-normal',
                      colIndex === 0
                        ? 'font-semibold text-text-secondary'
                        : colIndex === highlightColumn
                          ? 'text-accent-primary'
                          : 'text-text-primary'
                    )}
                    style={
                      colIndex === highlightColumn
                        ? { background: 'linear-gradient(180deg, rgba(212, 168, 83, 0.06) 0%, rgba(212, 168, 83, 0.02) 100%)' }
                        : undefined
                    }
                  >
                    {cell}
                  </TableCell>
                )
              ))}
            </motion.tr>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
