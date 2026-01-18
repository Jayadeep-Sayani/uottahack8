import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import * as Sentry from '@sentry/react'
import './index.css'
import App from './App.jsx'

// Initialize Sentry for error tracking
Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN || '',
  integrations: [
    Sentry.browserTracingIntegration(),
    Sentry.replayIntegration(),
  ],
  tracesSampleRate: 1.0,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
  environment: import.meta.env.MODE,
})

// Helper function to test Sentry (can be called from console)
window.testSentry = () => {
  const dsn = import.meta.env.VITE_SENTRY_DSN
  if (!dsn) {
    console.log('❌ Sentry DSN not configured. Add VITE_SENTRY_DSN to your .env file.')
    return false
  }
  Sentry.captureMessage('Sentry test from React frontend - get-into.tech')
  console.log('✅ Sentry test message sent! Check your Sentry dashboard.')
  return true
}

// Helper to trigger a test error
window.testSentryError = () => {
  throw new Error('Intentional test error from get-into.tech frontend!')
}

console.log('🔍 Sentry initialized. Use window.testSentry() to test.')

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
