import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import { transitions } from '../theme/motion'

/**
 * What-if scenario slider for exploring different parameter values.
 *
 * Props:
 * - title: string
 * - description?: string
 * - variables: Array<{ id, label, min, max, step, defaultValue, format }>
 * - calculate: (values) => Array<{ label, value, formatted, color? }>
 */
export default function ScenarioSlider({ title, description, variables, calculate }) {
  const [values, setValues] = useState(() => {
    const initial = {}
    variables.forEach((v) => {
      initial[v.id] = v.defaultValue
    })
    return initial
  })
  const [results, setResults] = useState([])

  useEffect(() => {
    try {
      setResults(calculate(values))
    } catch {
      setResults([])
    }
  }, [values, calculate])

  const handleChange = (id, raw) => {
    setValues((prev) => ({ ...prev, [id]: parseFloat(raw) }))
  }

  return (
    <Card className="border-l-3 border-l-accent-secondary rounded-r-lg py-5 my-5 shadow-md bg-gradient-teal-subtle"
    >
      <CardContent className="space-y-5">
        <div className="font-body text-sm font-semibold uppercase tracking-wide text-accent-secondary">
          {title}
        </div>
        {description && (
          <div className="text-sm text-text-secondary leading-normal">
            {description}
          </div>
        )}

        <div className="flex flex-col gap-5">
          {variables.map((variable) => (
            <div key={variable.id} className="flex flex-col gap-2">
              <div className="flex justify-between items-center">
                <Label className="text-xs uppercase tracking-wide text-text-secondary">
                  {variable.label}
                </Label>
                <motion.span
                  key={values[variable.id]}
                  className="font-mono text-sm tabular-nums"
                  initial={{ color: 'var(--color-accent-primary)' }}
                  animate={{ color: 'var(--color-accent-secondary)' }}
                  transition={{ duration: 0.4 }}
                >
                  {variable.format(values[variable.id])}
                </motion.span>
              </div>
              <input
                type="range"
                className="scenario-slider"
                aria-label={variable.label}
                min={variable.min}
                max={variable.max}
                step={variable.step}
                value={values[variable.id]}
                onChange={(e) => handleChange(variable.id, e.target.value)}
              />
              <div className="flex justify-between font-mono text-xs text-text-tertiary">
                <span>{variable.format(variable.min)}</span>
                <span>{variable.format(variable.max)}</span>
              </div>
            </div>
          ))}
        </div>

        {results.length > 0 && (
          <>
            <Separator className="bg-border-primary" />
            <div className="grid grid-cols-[repeat(auto-fit,minmax(160px,1fr))] gap-4">
              {results.map((result, i) => (
                <motion.div
                  key={result.label}
                  className="border border-border-primary rounded-md p-4 shadow-sm bg-gradient-surface"
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05, duration: 0.3 }}
                  whileHover={{ y: -2, boxShadow: 'var(--shadow-md)', transition: transitions.fast }}
                >
                  <div className="font-body text-xs uppercase tracking-wide font-medium text-text-tertiary mb-2">
                    {result.label}
                  </div>
                  <motion.div
                    key={result.formatted}
                    className="font-mono text-xl font-semibold tabular-nums leading-tight"
                    style={{ color: result.color || 'var(--color-accent-secondary)' }}
                    initial={{ scale: 1 }}
                    animate={{ scale: [1, 1.02, 1] }}
                    transition={{ duration: 0.15 }}
                  >
                    {result.formatted}
                  </motion.div>
                </motion.div>
              ))}
            </div>
          </>
        )}
      </CardContent>
    </Card>
  )
}
