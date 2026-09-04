import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../App';
import { api, ApiError } from '../api';

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [officerId, setOfficerId] = useState('OFFICER001');
  const [password, setPassword] = useState('SecurePass123!');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await api.auth.login({ officer_id: officerId, password });
      login(data.access_token, data.officer);
      navigate('/');
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Login failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <div className="login-logo">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
          </div>
          <h1 className="login-title">Identity Screening System</h1>
          <p className="login-subtitle">SIH 2026 - Problem Statement 26188</p>
        </div>

        <div className="login-body">
          <div className="demo-credentials">
            <strong>Demo Credentials:</strong><br/>
            Officer ID: <code>OFFICER001</code><br/>
            Password: <code>SecurePass123!</code>
          </div>

          {error && <div className="alert alert-error">{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="input-group">
              <label className="input-label">Officer ID</label>
              <input
                type="text"
                className="input-field"
                value={officerId}
                onChange={(e) => setOfficerId(e.target.value)}
                placeholder="Enter Officer ID"
                required
                disabled={loading}
              />
            </div>

            <div className="input-group">
              <label className="input-label">Password</label>
              <input
                type="password"
                className="input-field"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter Password"
                required
                disabled={loading}
              />
            </div>

            <button type="submit" className="btn btn-primary w-full" disabled={loading}>
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <div className="mt-16 text-center text-sm text-secondary">
            <p>AI-Based Fake Identity & Document Screening System</p>
            <p className="mt-4">Government Technology × Aviation Security × AI Forensics</p>
          </div>
        </div>
      </div>
    </div>
  );
}