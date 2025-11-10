import { Link, useLocation } from 'react-router-dom'
import './Navigation.css'

function Navigation() {
  const location = useLocation()

  const menuItems = [
    { path: '/ide', label: 'Daily Playground' },
    { path: '/interview-wizard', label: 'Interview Wizard' },
    { path: '/strategy', label: 'Strategy' },
    { path: '/difficult-conversations', label: 'Practice Difficult Conversations' },
    { path: '/decision-making', label: 'Decision Making' },
    { path: '/manage-performance', label: 'Manage Performance' },
  ]

  return (
    <nav className="main-navigation">
      <div className="nav-brand">
        <h1 className="nav-logo">Pensieve.ai</h1>
        <span className="nav-subtitle">IDE for Leaders</span>
      </div>
      <div className="nav-menu">
        {menuItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
          >
            {item.label}
          </Link>
        ))}
      </div>
    </nav>
  )
}

export default Navigation
