/**
 * Framer-motion animation tokens.
 * CSS design tokens are now in app.css via Tailwind @theme.
 */

export const transitions = {
  fast: { duration: 0.1, ease: 'easeOut' },
  base: { duration: 0.2, ease: 'easeOut' },
  slow: { duration: 0.35, ease: [0.25, 0.1, 0.25, 1] },
  spring: { type: 'spring', stiffness: 400, damping: 30 },
  springGentle: { type: 'spring', stiffness: 300, damping: 25 },
}

export const animation = {
  tabTransition: { duration: 0.3, ease: [0.25, 0.1, 0.25, 1] },
  contentReveal: { duration: 0.4, ease: [0.25, 0.1, 0.25, 1] },
  staggerChildren: 0.05,
  countUp: { duration: 0.6 },
  hoverLift: { y: -2, transition: { duration: 0.15, ease: 'easeOut' } },
  pressScale: { scale: 0.98, transition: { duration: 0.1 } },
  fadeInUp: {
    initial: { opacity: 0, y: 12 },
    animate: { opacity: 1, y: 0 },
  },
}
