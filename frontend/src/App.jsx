import { NavLink, Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Predict from './pages/Predict'
import Explorer from './pages/Explorer'
import PersonFraud from './pages/PersonFraud'

function App() {
  return (
    <div className="app">
      <header className="nav-top">
        <div className="nav-inner">
          <div className="nav-brand">
            Shield<span>Fraud</span>
          </div>
          <nav className="nav-links">
            <NavLink to="/" end>Dashboard</NavLink>
            <NavLink to="/predict">Predict</NavLink>
            <NavLink to="/explorer">Explorer</NavLink>
            <NavLink to="/person">By Person</NavLink>
          </nav>
        </div>
      </header>
      <main className="main">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/predict" element={<Predict />} />
          <Route path="/explorer" element={<Explorer />} />
          <Route path="/person" element={<PersonFraud />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
