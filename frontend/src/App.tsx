import { Layout } from './components'
import { DashboardPage, BedrockPage, IAMPage, PluginsPage, BootstrapPage } from './pages'
import { Routes, Route, Navigate } from 'react-router-dom'

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<DashboardPage />} />
      <Route path="/bedrock" element={<BedrockPage />} />
      <Route path="/iam" element={<IAMPage />} />
      <Route path="/plugins" element={<PluginsPage />} />
      <Route path="/bootstrap" element={<BootstrapPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <Layout>
      <AppRoutes />
    </Layout>
  )
}