import { Suspense, lazy } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import TopNav from './components/TopNav'

// Lazy load pages
const Overview = lazy(() => import('./pages/Overview'))
const Playground = lazy(() => import('./pages/Playground'))
const SecurityGateway = lazy(() => import('./pages/SecurityGateway'))
const ThreatDetection = lazy(() => import('./pages/ThreatDetection'))
const ActivityLogs = lazy(() => import('./pages/ActivityLogs'))
const SecurityPolicies = lazy(() => import('./pages/SecurityPolicies'))
const AttackSimulationLab = lazy(() => import('./pages/AttackSimulationLab'))
const Settings = lazy(() => import('./pages/Settings'))

// Suspense fallback
function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="w-12 h-12 border-4 border-slate-700 border-t-blue-500 rounded-full animate-spin" />
    </div>
  )
}

// Layout wrapper for routes
function LayoutWrapper({ children }: { children: React.ReactNode }) {
  return (
    <div className="ml-64 mt-16 p-6 min-h-screen bg-slate-950">
      {children}
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Sidebar />
      <TopNav title="AgentShield" />
      
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
          <Route path="/" element={<LayoutWrapper><Overview /></LayoutWrapper>} />
          <Route path="/playground" element={<LayoutWrapper><Playground /></LayoutWrapper>} />
          <Route path="/gateway" element={<LayoutWrapper><SecurityGateway /></LayoutWrapper>} />
          <Route path="/threats" element={<LayoutWrapper><ThreatDetection /></LayoutWrapper>} />
          <Route path="/logs" element={<LayoutWrapper><ActivityLogs /></LayoutWrapper>} />
          <Route path="/policies" element={<LayoutWrapper><SecurityPolicies /></LayoutWrapper>} />
          <Route path="/lab" element={<LayoutWrapper><AttackSimulationLab /></LayoutWrapper>} />
          <Route path="/settings" element={<LayoutWrapper><Settings /></LayoutWrapper>} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  )
}
