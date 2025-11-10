import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Navigation from './components/Navigation'
import HomePage from './pages/HomePage'
import ChatPage from './pages/ChatPage'
import IDEPage from './pages/IDEPage'
import InterviewWizardPage from './pages/InterviewWizardPage'
import StrategyPage from './pages/StrategyPage'
import DifficultConversationsPage from './pages/DifficultConversationsPage'
import DecisionMakingPage from './pages/DecisionMakingPage'
import ManagePerformancePage from './pages/ManagePerformancePage'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <Navigation />
        <div className="app-content">
          <Routes>
            <Route path="/" element={<Navigate to="/ide" replace />} />
            <Route path="/home" element={<HomePage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/ide" element={<IDEPage />} />
            <Route path="/interview-wizard" element={<InterviewWizardPage />} />
            <Route path="/strategy" element={<StrategyPage />} />
            <Route path="/difficult-conversations" element={<DifficultConversationsPage />} />
            <Route path="/decision-making" element={<DecisionMakingPage />} />
            <Route path="/manage-performance" element={<ManagePerformancePage />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  )
}

export default App
