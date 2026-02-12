import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import { transitions } from '../theme/motion'

/**
 * Interactive calculator component.
 *
 * Props:
 * - title: string
 * - formulaDisplay: string
 * - inputs: Array<{ id, label, defaultValue, prefix?, suffix?, step? }>
 * - calculate: (values) => { result, breakdown? }
 */
export default function Calculator({ title, formulaDisplay, inputs, calculate }) {
  const [values, setValues] = useState(() => {
    const initial = {}
    inputs.forEach((input) => {
      initial[input.id] = input.defaultValue
    })
    return initial
  })

  const [output, setOutput] = useState(null)

  useEffect(() => {
    try {
      const result = calculate(values)
      setOutput(result)
    } catch {
      setOutput(null)
    }
  }, [values, calculate])

  const handleChange = (id, raw) => {
    const num = parseFloat(raw)
    setValues((prev) => ({ ...prev, [id]: isNaN(num) ? 0 : num }))
  }

  return (
    <Card className="border-l-3 border-l-accent-primary rounded-r-lg py-5 my-5 shadow-md bg-gradient-gold-subtle"
    >
      <CardContent className="space-y-5">
        <div className="font-body text-sm font-semibold uppercase tracking-wide text-accent-primary">
          {title}
        </div>

        {formulaDisplay && (
          <div className="font-mono text-sm text-text-secondary bg-[rgba(15,17,23,0.5)] px-4 py-3 rounded-md border border-border-primary shadow-inset">
            {formulaDisplay}
          </div>
        )}

        <div className="grid grid-cols-[repeat(auto-fit,minmax(200px,1fr))] gap-4">
          {inputs.map((input) => (
            <div key={input.id} className="flex flex-col gap-2">
              <Label
                htmlFor={`calc-${input.id}`}
                className="text-xs uppercase tracking-wide text-text-secondary"
              >
                {input.label}
              </Label>
              <div className="relative flex items-center">
                {input.prefix && (
                  <span className="absolute left-3 text-text-tertiary font-mono text-sm pointer-events-none z-10">
                    {input.prefix}
                  </span>
                )}
                <Input
                  id={`calc-${input.id}`}
                  type="number"
                  inputMode="decimal"
                  name={input.id}
                  autoComplete="off"
                  step={input.step || 'any'}
                  value={values[input.id]}
                  onChange={(e) => handleChange(input.id, e.target.value)}
                  className="font-mono bg-bg-primary border-border-primary text-text-primary shadow-inset focus-visible:border-accent-primary focus-visible:ring-[rgba(212,168,83,0.15)]"
                  style={{
                    paddingLeft: input.prefix ? '2.5rem' : undefined,
                    paddingRight: input.suffix ? '2.5rem' : undefined,
                  }}
                />
                {input.suffix && (
                  <span className="absolute right-3 text-text-tertiary font-mono text-sm pointer-events-none">
                    {input.suffix}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>

        {output && (
          <>
            <Separator className="bg-border-primary" />
            <motion.div
              key={output.result.formatted}
              className="flex flex-col gap-3"
              initial={{ opacity: 0, scale: 0.95, y: 4 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              transition={transitions.spring}
            >
              <div className="text-xs uppercase tracking-wide font-medium text-text-secondary">
                {output.result.label}
              </div>
              <div className="font-mono text-[length:var(--font-size-hero)] font-semibold text-accent-primary tabular-nums leading-none">
                {output.result.formatted}
              </div>

              {output.breakdown && output.breakdown.length > 0 && (
                <div className="flex flex-col gap-2 mt-3">
                  {output.breakdown.map((item, i) => (
                    <div
                      key={i}
                      className="flex justify-between items-center py-2 px-3 rounded-sm text-sm"
                      style={{
                        background: i % 2 === 0 ? 'rgba(15, 17, 23, 0.4)' : 'transparent',
                      }}
                    >
                      <span className="text-text-secondary">{item.label}</span>
                      <span className="font-mono text-text-primary tabular-nums">
                        {item.formatted}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </motion.div>
          </>
        )}
      </CardContent>
    </Card>
  )
}
