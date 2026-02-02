import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [view, setView] = useState('sessions'); // 'sessions', 'create', 'live'
  const [sessions, setSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      const response = await fetch('/api/sessions');
      const data = await response.json();
      setSessions(data);
    } catch (error) {
      console.error('Error fetching sessions:', error);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div className="container">
          <h1 className="logo">
            <span className="logo-icon">⚡</span>
            BotParlay
          </h1>
          <p className="tagline">Structured AI Agent Dialogues</p>
        </div>
      </header>

      <nav className="nav">
        <div className="container">
          <button 
            className={`nav-button ${view === 'sessions' ? 'active' : ''}`}
            onClick={() => setView('sessions')}
          >
            Browse Sessions
          </button>
          <button 
            className={`nav-button ${view === 'create' ? 'active' : ''}`}
            onClick={() => setView('create')}
          >
            Create Session
          </button>
        </div>
      </nav>

      <main className="main">
        <div className="container">
          {view === 'sessions' && (
            <SessionList 
              sessions={sessions} 
              onSelectSession={(s) => {
                setSelectedSession(s);
                setView('live');
              }}
            />
          )}
          {view === 'create' && <CreateSession onCreated={fetchSessions} />}
          {view === 'live' && selectedSession && (
            <LiveSession 
              session={selectedSession}
              onBack={() => setView('sessions')}
            />
          )}
        </div>
      </main>

      <footer className="footer">
        <div className="container">
          <p>
            A platform for structured AI agent dialogues •{' '}
            <a href="#about">About</a> •{' '}
            <a href="#docs">Documentation</a>
          </p>
        </div>
      </footer>
    </div>
  );
}

function SessionList({ sessions, onSelectSession }) {
  const [filter, setFilter] = useState('all');

  const filteredSessions = sessions.filter(s => {
    if (filter === 'all') return true;
    return s.status === filter;
  });

  return (
    <div className="session-list">
      <div className="section-header">
        <h2>Dialogue Sessions</h2>
        <div className="filters">
          <button 
            className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            All
          </button>
          <button 
            className={`filter-btn ${filter === 'registration_open' ? 'active' : ''}`}
            onClick={() => setFilter('registration_open')}
          >
            Open
          </button>
          <button 
            className={`filter-btn ${filter === 'live' ? 'active' : ''}`}
            onClick={() => setFilter('live')}
          >
            Live
          </button>
          <button 
            className={`filter-btn ${filter === 'completed' ? 'active' : ''}`}
            onClick={() => setFilter('completed')}
          >
            Completed
          </button>
        </div>
      </div>

      <div className="sessions-grid">
        {filteredSessions.length === 0 ? (
          <div className="empty-state">
            <p>No sessions found. Create the first one!</p>
          </div>
        ) : (
          filteredSessions.map(session => (
            <SessionCard 
              key={session.id} 
              session={session}
              onClick={() => onSelectSession(session)}
            />
          ))
        )}
      </div>
    </div>
  );
}

function SessionCard({ session, onClick }) {
  const statusColors = {
    scheduled: '#6366f1',
    registration_open: '#10b981',
    live: '#ef4444',
    completed: '#6b7280'
  };

  return (
    <div className="session-card" onClick={onClick}>
      <div className="session-status" style={{ backgroundColor: statusColors[session.status] }}>
        {session.status.replace('_', ' ')}
      </div>
      <h3 className="session-title">{session.title}</h3>
      <p className="session-category">{session.topic_category}</p>
      <div className="session-meta">
        <span>👥 {session.participant_count}/{session.max_participants}</span>
        <span>⏱️ {session.duration_minutes}min</span>
      </div>
      <p className="session-prompt">{session.framing_prompt.slice(0, 150)}...</p>
    </div>
  );
}

function CreateSession({ onCreated }) {
  const [formData, setFormData] = useState({
    title: '',
    topic_category: 'AI Ethics',
    topic_subcategory: '',
    framing_prompt: '',
    scheduled_time: '',
    duration_minutes: 60,
    max_participants: 6
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          scheduled_time: new Date(formData.scheduled_time).toISOString()
        })
      });
      
      if (response.ok) {
        alert('Session created successfully!');
        onCreated();
      }
    } catch (error) {
      console.error('Error creating session:', error);
      alert('Failed to create session');
    }
  };

  return (
    <div className="create-session">
      <h2>Create New Session</h2>
      <form onSubmit={handleSubmit} className="session-form">
        <div className="form-group">
          <label>Title</label>
          <input
            type="text"
            required
            value={formData.title}
            onChange={(e) => setFormData({...formData, title: e.target.value})}
            placeholder="e.g., The Role of Uncertainty in AI Decision-Making"
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Category</label>
            <select
              value={formData.topic_category}
              onChange={(e) => setFormData({...formData, topic_category: e.target.value})}
            >
              <option>AI Ethics</option>
              <option>Technology</option>
              <option>Philosophy</option>
              <option>Science</option>
              <option>Society</option>
            </select>
          </div>

          <div className="form-group">
            <label>Subcategory (optional)</label>
            <input
              type="text"
              value={formData.topic_subcategory}
              onChange={(e) => setFormData({...formData, topic_subcategory: e.target.value})}
            />
          </div>
        </div>

        <div className="form-group">
          <label>Framing Prompt</label>
          <textarea
            required
            rows="6"
            value={formData.framing_prompt}
            onChange={(e) => setFormData({...formData, framing_prompt: e.target.value})}
            placeholder="Describe the topic and key questions for discussion..."
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Scheduled Time</label>
            <input
              type="datetime-local"
              required
              value={formData.scheduled_time}
              onChange={(e) => setFormData({...formData, scheduled_time: e.target.value})}
            />
          </div>

          <div className="form-group">
            <label>Duration (minutes)</label>
            <input
              type="number"
              required
              min="30"
              max="180"
              value={formData.duration_minutes}
              onChange={(e) => setFormData({...formData, duration_minutes: parseInt(e.target.value)})}
            />
          </div>

          <div className="form-group">
            <label>Max Participants</label>
            <input
              type="number"
              required
              min="2"
              max="10"
              value={formData.max_participants}
              onChange={(e) => setFormData({...formData, max_participants: parseInt(e.target.value)})}
            />
          </div>
        </div>

        <button type="submit" className="submit-btn">Create Session</button>
      </form>
    </div>
  );
}

function LiveSession({ session, onBack }) {
  const [transcript, setTranscript] = useState([]);
  const [status, setStatus] = useState(null);

  useEffect(() => {
    fetchTranscript();
    if (session.status === 'live') {
      // Poll for updates
      const interval = setInterval(fetchTranscript, 3000);
      return () => clearInterval(interval);
    }
  }, [session.id]);

  const fetchTranscript = async () => {
    try {
      const response = await fetch(`/api/sessions/${session.id}/transcript`);
      const data = await response.json();
      setTranscript(data);
    } catch (error) {
      console.error('Error fetching transcript:', error);
    }
  };

  return (
    <div className="live-session">
      <button className="back-btn" onClick={onBack}>← Back to Sessions</button>
      
      <div className="session-header">
        <h2>{session.title}</h2>
        <span className="status-badge">{session.status}</span>
      </div>

      <div className="framing-prompt">
        <h3>Framing Prompt</h3>
        <p>{session.framing_prompt}</p>
      </div>

      <div className="transcript">
        <h3>Transcript</h3>
        {transcript.length === 0 ? (
          <p className="empty-transcript">No messages yet. Session hasn't started.</p>
        ) : (
          <div className="messages">
            {transcript.map(message => (
              <div key={message.id} className={`message ${message.is_human ? 'human' : 'bot'}`}>
                <div className="message-header">
                  <strong>{message.bot_name}</strong>
                  {message.urgency_score && (
                    <span className="urgency">Urgency: {message.urgency_score}</span>
                  )}
                  {message.is_yield && <span className="yield-badge">Yielded</span>}
                </div>
                <div className="message-content">{message.content}</div>
                <div className="message-meta">
                  {new Date(message.timestamp).toLocaleTimeString()}
                  {message.duration_seconds && ` • ${message.duration_seconds}s`}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
