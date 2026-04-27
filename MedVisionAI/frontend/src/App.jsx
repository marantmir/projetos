import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Navigation from './components/Navigation'
import Footer from './components/Footer'

// Lazy load pages
const HomePage = React.lazy(() => import('./pages/HomePage'))
const VideoUploadPage = React.lazy(() => import('./pages/VideoUploadPage'))
const AudioUploadPage = React.lazy(() => import('./pages/AudioUploadPage'))
const AnalysisPage = React.lazy(() => import('./pages/AnalysisPage'))
const ReportsPage = React.lazy(() => import('./pages/ReportsPage'))

function App() {
  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 transition-colors">
      <Navigation />
      <React.Suspense fallback={
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 dark:border-sky-400 mx-auto mb-4"></div>
            <p className="text-gray-600 dark:text-gray-300">Carregando...</p>
          </div>
        </div>
      }>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/upload-video" element={<VideoUploadPage />} />
          <Route path="/upload-audio" element={<AudioUploadPage />} />
          <Route path="/analysis/:analysisId" element={<AnalysisPage />} />
          <Route path="/reports" element={<ReportsPage />} />
        </Routes>
      </React.Suspense>
      <Footer />
    </div>
  );
}

export default App
