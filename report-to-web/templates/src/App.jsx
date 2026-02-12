/**
 * App.jsx — Main application shell.
 *
 * THIS IS A TEMPLATE FILE.
 * The site-builder agent will replace this with a version
 * customized for the specific report, wiring up:
 * - reportData from src/data/reportData.js
 * - interactiveConfig from src/data/interactiveConfig.js
 * - Tab pages from src/pages/
 *
 * This template shows the expected structure for reference.
 */

import { useState, useEffect, useCallback } from 'react'
import TabbedLayout from './components/TabbedLayout'
import SectionRenderer from './components/SectionRenderer'
import KnowledgeVault from './components/KnowledgeVault'

// Example structure — replaced by generated data
const exampleTabs = [
  {
    id: 'overview',
    label: 'Overview',
    content: (
      <SectionRenderer
        id="overview"
        title="Report Overview"
        content="This is a template. The site-builder agent generates real content from your research report."
        level={2}
      />
    ),
  },
  {
    id: 'vault',
    label: 'Knowledge Vault',
    content: (
      <KnowledgeVault
        sections={[
          {
            id: 'example',
            title: 'Example Section',
            content: 'This demonstrates the searchable knowledge vault. All report content appears here.',
          },
        ]}
      />
    ),
  },
]

// Presentation mode auto-advance hook
function usePresentationMode(tabCount) {
  const [isPresenting, setIsPresenting] = useState(false)
  const [progress, setProgress] = useState(0)

  const INTERVAL = 8000

  useEffect(() => {
    if (!isPresenting) {
      setProgress(0)
      return
    }
    const tick = setInterval(() => {
      setProgress((p) => {
        if (p >= 100) return 0
        return p + (100 / (INTERVAL / 50))
      })
    }, 50)
    return () => clearInterval(tick)
  }, [isPresenting])

  return { isPresenting, setIsPresenting, progress }
}

export default function App() {
  const [activeTab, setActiveTab] = useState(0)
  const tabs = exampleTabs
  const { isPresenting, setIsPresenting, progress } = usePresentationMode(tabs.length)

  // Auto-advance when progress hits 100%
  useEffect(() => {
    if (isPresenting && progress >= 100) {
      setActiveTab((prev) => (prev + 1) % tabs.length)
    }
  }, [isPresenting, progress, tabs.length])

  const handleTabChange = useCallback((index) => {
    setActiveTab(index)
  }, [])

  return (
    <TabbedLayout
      title="Research Report"
      subtitle="Interactive presentation generated from markdown"
      tabs={tabs}
      activeTab={activeTab}
      onTabChange={handleTabChange}
      isPresenting={isPresenting}
      setIsPresenting={setIsPresenting}
      progress={progress}
    />
  )
}
