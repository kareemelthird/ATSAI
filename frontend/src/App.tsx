import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/Layout'
import ErrorBoundary from './components/ErrorBoundary'
import Dashboard from './pages/Dashboard'
import Candidates from './pages/Candidates'
import CandidateDetailEnhanced from './pages/CandidateDetailEnhanced'
import EditCandidateEnhanced from './pages/EditCandidateEnhanced'
import Jobs from './pages/Jobs'
import JobDetail from './pages/JobDetail'
import Applications from './pages/Applications'
import AIChat from './pages/AIChat'
import UploadResume from './pages/UploadResume'
import Login from './pages/Login'
import Profile from './pages/Profile'
import AdminUsers from './pages/admin/Users'
import UnifiedSettings from './pages/admin/UnifiedSettings'

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <AuthProvider>
          <Routes>
            {/* Login route (no layout, no auth required) */}
            <Route path="/login" element={<Login />} />
            
            {/* Main app routes (with layout, auth required) */}
            <Route path="/" element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }>
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="candidates" element={<Candidates />} />
              <Route path="candidates/:id" element={<CandidateDetailEnhanced />} />
              <Route path="candidates/:id/edit" element={<EditCandidateEnhanced />} />
              <Route path="jobs" element={<Jobs />} />
              <Route path="jobs/:id" element={<JobDetail />} />
              <Route path="applications" element={<Applications />} />
              <Route path="ai-chat" element={<AIChat />} />
              <Route path="upload" element={<UploadResume />} />
              <Route path="profile" element={<Profile />} />
              
              {/* Admin routes (require admin role) */}
              <Route path="admin/users" element={
                <ProtectedRoute requireAdmin={true}>
                  <AdminUsers />
                </ProtectedRoute>
              } />
              <Route path="admin/settings" element={
                <ProtectedRoute requireAdmin={true}>
                  <UnifiedSettings />
                </ProtectedRoute>
              } />
            </Route>
          </Routes>
        </AuthProvider>
      </Router>
    </ErrorBoundary>
  )
}

export default App
