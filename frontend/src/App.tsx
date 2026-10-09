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

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen bg-slate-950">
        {/* Sidebar */}
        <Sidebar />
        
        {/* Main Content Area */}
        <div className="flex-1 flex flex-col overflow-hidden ml-64">
          {/* Top Navigation */}
          <TopNav title="AgentShield" />
          
          {/* Page Content */}
          <div className="flex-1 overflow-y-auto pt-16">
            <Suspense fallback={<LoadingSpinner />}>
              <Routes>
                <Route path="/" element={<Overview />} />
                <Route path="/playground" element={<Playground />} />
                <Route path="/gateway" element={<SecurityGateway />} />
                <Route path="/threats" element={<ThreatDetection />} />
                <Route path="/logs" element={<ActivityLogs />} />
                <Route path="/policies" element={<SecurityPolicies />} />
                <Route path="/lab" element={<AttackSimulationLab />} />
                <Route path="/settings" element={<Settings />} />
              </Routes>
            </Suspense>
          </div>
        </div>
      </div>
    </BrowserRouter>
  )
}
