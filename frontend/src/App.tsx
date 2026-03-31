import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Overview from './pages/Overview'
import Inventory from './pages/Inventory'
import Equipment from './pages/Equipment'
import Quests from './pages/Quests'
import Mercenaries from './pages/Mercenaries'
import Timeline from './pages/Timeline'
import Settings from './pages/Settings'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Overview />} />
        <Route path="inventory" element={<Inventory />} />
        <Route path="equipment" element={<Equipment />} />
        <Route path="quests" element={<Quests />} />
        <Route path="mercenaries" element={<Mercenaries />} />
        <Route path="timeline" element={<Timeline />} />
        <Route path="settings" element={<Settings />} />
      </Route>
    </Routes>
  )
}
