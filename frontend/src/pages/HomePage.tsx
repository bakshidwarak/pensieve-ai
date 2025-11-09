import { Link } from 'react-router-dom'
import './HomePage.css'

function HomePage() {
  return (
    <div className="home-page">
      <div className="container">
        <header className="header">
          <h1 className="title">Pensieve.ai</h1>
          <p className="subtitle">IDE for Leaders</p>
        </header>

        <main className="main">
          <p className="description">
            An intelligent development environment designed to help leaders
            navigate complexity, make informed decisions, and drive strategic outcomes.
          </p>

          <div className="actions">
            <Link to="/ide" className="btn btn-primary">
              Open IDE
            </Link>
            <Link to="/chat" className="btn btn-secondary">
              Simple Chat
            </Link>
          </div>

          <div className="features">
            <div className="feature">
              <h3>AI-Powered Insights</h3>
              <p>Get intelligent recommendations powered by advanced RAG</p>
            </div>
            <div className="feature">
              <h3>Knowledge Base</h3>
              <p>Access curated information from your documents</p>
            </div>
            <div className="feature">
              <h3>Agentic Workflows</h3>
              <p>Leverage AI agents for complex research and analysis</p>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}

export default HomePage
