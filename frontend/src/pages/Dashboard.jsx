import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api, ApiError } from '../api';

export default function Dashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('cases');
  const [showNewCase, setShowNewCase] = useState(false);
  const [newCaseData, setNewCaseData] = useState({
    passenger_name: '',
    nationality: '',
    date_of_birth: '',
    passport_number: '',
  });
  const [selectedDemo, setSelectedDemo] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [statsData, casesData] = await Promise.all([
        api.dashboard.getStats(),
        api.dashboard.getCases(),
      ]);
      setStats(statsData);
      setCases(casesData);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  const handleNewCase = async (e) => {
    e.preventDefault();
    try {
      const newCase = await api.cases.create(newCaseData);
      setCases([newCase, ...cases]);
      setShowNewCase(false);
      setNewCaseData({ passenger_name: '', nationality: '', date_of_birth: '', passport_number: '' });
      navigate(`/case/${newCase.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to create case');
    }
  };

  const loadDemoCase = async (caseType) => {
    setSelectedDemo(caseType);
    const demoCases = cases.filter(c => c.case_id.includes(caseType === 'valid' ? '001' : caseType === 'suspicious' ? '002' : '003'));
    if (demoCases.length > 0) {
      navigate(`/case/${demoCases[0].id}`);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-64px)]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-4 border-royal-blue border-t-transparent rounded-full animate-spin"></div>
          <p className="text-secondary">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  const riskColors = {
    low: 'badge-low',
    medium: 'badge-medium',
    high: 'badge-high',
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Officer Dashboard</h1>
        <p className="page-subtitle">AI-Based Fake Identity & Document Screening System</p>
      </div>

      {error && <div className="alert alert-error mb-24">{error}</div>}

      <div className="demo-selector mb-24">
        <span className="font-medium text-secondary self-center">Demo Mode:</span>
        <button className={`demo-btn valid ${selectedDemo === 'valid' ? 'active' : ''}`} onClick={() => loadDemoCase('valid')}>
          ✓ Valid Passenger
        </button>
        <button className={`demo-btn suspicious ${selectedDemo === 'suspicious' ? 'active' : ''}`} onClick={() => loadDemoCase('suspicious')}>
          ⚠ Suspicious Document
        </button>
        <button className={`demo-btn high-risk ${selectedDemo === 'high-risk' ? 'active' : ''}`} onClick={() => loadDemoCase('high-risk')}>
          🔴 High-Risk Passenger
        </button>
      </div>

      <div className="grid grid-4 gap-24 mb-24">
        <div className="stat-card">
          <div className="stat-icon stat-icon-blue">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
          </div>
          <div className="stat-value">{stats?.passengers_screened || 0}</div>
          <div className="stat-label">Passengers Screened</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon stat-icon-cyan">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>
            </svg>
          </div>
          <div className="stat-value">{stats?.documents_verified || 0}</div>
          <div className="stat-label">Documents Verified</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon stat-icon-green">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
          </div>
          <div className="stat-value">{stats?.valid_documents || 0}</div>
          <div className="stat-label">Valid Documents</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon stat-icon-red">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
          </div>
          <div className="stat-value">{stats?.high_risk_cases || 0}</div>
          <div className="stat-label">High Risk Cases</div>
        </div>
      </div>

      <div className="card mb-24">
        <div className="card-header">
          <div className="flex justify-between items-center">
            <h2 className="card-title">Risk Distribution</h2>
          </div>
        </div>
        <div className="card-body">
          <div className="grid grid-3 gap-16">
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-4xl font-bold text-green-700">{stats?.risk_distribution?.low || 0}</div>
              <div className="text-sm text-green-600">LOW Risk</div>
            </div>
            <div className="text-center p-4 bg-amber-50 rounded-lg">
              <div className="text-4xl font-bold text-amber-700">{stats?.risk_distribution?.medium || 0}</div>
              <div className="text-sm text-amber-600">MEDIUM Risk</div>
            </div>
            <div className="text-center p-4 bg-red-50 rounded-lg">
              <div className="text-4xl font-bold text-red-700">{stats?.risk_distribution?.high || 0}</div>
              <div className="text-sm text-red-600">HIGH Risk</div>
            </div>
          </div>
        </div>
      </div>

      <div className="tabs mb-8">
        <button className={`tab ${activeTab === 'cases' ? 'active' : ''}`} onClick={() => setActiveTab('cases')}>
          Passenger Cases
        </button>
        <button className={`tab ${activeTab === 'queue' ? 'active' : ''}`} onClick={() => setActiveTab('queue')}>
          Processing Queue
        </button>
      </div>

      {activeTab === 'cases' && (
        <>
          <div className="flex justify-between items-center mb-16">
            <h2 className="card-title">Passenger History</h2>
            <button className="btn btn-primary" onClick={() => setShowNewCase(true)}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
              New Case
            </button>
          </div>

          {cases.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                </svg>
              </div>
              <div className="empty-state-title">No cases yet</div>
              <div className="empty-state-text">Create a new case or select a demo passenger to begin screening.</div>
            </div>
          ) : (
            <div className="grid gap-16">
              {cases.map(caseItem => (
                <Link to={`/case/${caseItem.id}`} key={caseItem.id} className="case-card">
                  <div className="case-card-header">
                    <span className="case-card-id">{caseItem.case_id}</span>
                    <span className={`badge ${riskColors[caseItem.risk_level]}`}>
                      {caseItem.risk_level.toUpperCase()}
                    </span>
                  </div>
                  <div className="case-card-name">{caseItem.passenger_name}</div>
                  <div className="case-card-meta">
                    <span>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
                      </svg>
                      {caseItem.nationality || 'N/A'}
                    </span>
                    <span>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
                      </svg>
                      {caseItem.date_of_birth || 'N/A'}
                    </span>
                    <span>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/>
                      </svg>
                      {caseItem.passport_number || 'N/A'}
                    </span>
                  </div>
                  <div className="case-card-documents">
                    {caseItem.documents?.map(doc => (
                      <span key={doc.id} className={`doc-tag ${doc.document_type}`}>
                        {doc.document_type.replace('_', ' ').toUpperCase()}
                      </span>
                    ))}
                  </div>
                </Link>
              ))}
            </div>
          )}
        </>
      )}

      {activeTab === 'queue' && (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Processing Queue</h2>
          </div>
          <div className="card-body">
            {cases.flatMap(c => c.documents || []).length === 0 ? (
              <div className="empty-state">
                <div className="empty-state-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>
                  </svg>
                </div>
                <div className="empty-state-title">No documents in queue</div>
                <div className="empty-state-text">Upload documents from a case detail view to see processing progress.</div>
              </div>
            ) : (
              <div className="space-y-12">
                {cases.flatMap(c => (c.documents || []).map(doc => ({
                  ...doc,
                  passenger: c.passenger_name,
                  caseId: c.case_id,
                }))).map(doc => (
                  <div key={doc.id} className="flex items-center gap-16 p-4 bg-white border border-border rounded-lg">
                    <div className="w-48 flex-shrink-0">
                      <div className="font-medium text-sm">{doc.original_filename}</div>
                      <div className="text-xs text-secondary">{doc.document_type.toUpperCase()}</div>
                    </div>
                    <div className="flex-1">
                      <div className="progress-bar mb-2">
                        <div className={`progress-fill ${doc.processing_status}`} style={{ width: `${doc.progress}%` }}></div>
                      </div>
                      <div className="flex items-center gap-8 text-sm">
                        <span className={`badge badge-${doc.processing_status}`}>{doc.processing_status.toUpperCase()}</span>
                        <span className="text-secondary">{doc.progress}%</span>
                      </div>
                    </div>
                    <span className="badge badge-match">Ready</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {showNewCase && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50" onClick={() => setShowNewCase(false)}>
          <div className="card w-full max-w-md" onClick={e => e.stopPropagation()}>
            <div className="card-header flex justify-between items-center">
              <h2 className="card-title">New Passenger Case</h2>
              <button className="btn btn-outline" onClick={() => setShowNewCase(false)}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>
            <form onSubmit={handleNewCase} className="card-body space-y-4">
              <div className="input-group">
                <label className="input-label">Passenger Name *</label>
                <input type="text" className="input-field" value={newCaseData.passenger_name} onChange={e => setNewCaseData({...newCaseData, passenger_name: e.target.value})} placeholder="Full name" required />
              </div>
              <div className="form-row">
                <div className="input-group">
                  <label className="input-label">Nationality</label>
                  <input type="text" className="input-field" value={newCaseData.nationality} onChange={e => setNewCaseData({...newCaseData, nationality: e.target.value})} placeholder="e.g., IND" />
                </div>
                <div className="input-group">
                  <label className="input-label">Date of Birth</label>
                  <input type="text" className="input-field" value={newCaseData.date_of_birth} onChange={e => setNewCaseData({...newCaseData, date_of_birth: e.target.value})} placeholder="DD.MM.YYYY" />
                </div>
              </div>
              <div className="input-group">
                <label className="input-label">Passport Number</label>
                <input type="text" className="input-field" value={newCaseData.passport_number} onChange={e => setNewCaseData({...newCaseData, passport_number: e.target.value})} placeholder="e.g., Z1234567" />
              </div>
              <div className="flex justify-end gap-8 mt-8">
                <button type="button" className="btn btn-secondary" onClick={() => setShowNewCase(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Create Case</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}