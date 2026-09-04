import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { api, ApiError } from '../api';

export default function CaseDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [caseDetail, setCaseDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [processing, setProcessing] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [facePhotos, setFacePhotos] = useState({ doc: null, live: null });
  const [faceResult, setFaceResult] = useState(null);
  const [showFaceModal, setShowFaceModal] = useState(false);

  useEffect(() => {
    fetchCaseDetail();
  }, [id]);

  const fetchCaseDetail = async () => {
    try {
      const data = await api.cases.getDetail(id);
      setCaseDetail(data);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to load case');
    } finally {
      setLoading(false);
    }
  };

  const handleProcess = async () => {
    if (!caseDetail) return;
    setProcessing(true);
    try {
      await api.cases.process(caseDetail.id);
      fetchCaseDetail();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Processing failed');
    } finally {
      setProcessing(false);
    }
  };

  const handleFaceUpload = async (e) => {
    e.preventDefault();
    if (!facePhotos.doc || !facePhotos.live) return;
    setUploading(true);
    try {
      const result = await api.cases.uploadFacePhotos(caseDetail.id, facePhotos.doc, facePhotos.live);
      setFaceResult(result);
      fetchCaseDetail();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Face upload failed');
    } finally {
      setUploading(false);
      setShowFaceModal(false);
    }
  };

  const riskColors = {
    low: 'badge-low',
    medium: 'badge-medium',
    high: 'badge-high',
  };

  const riskIcons = {
    low: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>,
    medium: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>,
    high: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>,
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-64px)]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-4 border-royal-blue border-t-transparent rounded-full animate-spin"></div>
          <p className="text-secondary">Loading case details...</p>
        </div>
      </div>
    );
  }

  if (error && !caseDetail) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-64px)]">
        <div className="text-center">
          <div className="alert alert-error mb-4">{error}</div>
          <Link to="/" className="btn btn-primary">Back to Dashboard</Link>
        </div>
      </div>
    );
  }

  const c = caseDetail;
  const riskAssessment = c.risk_assessment;

  const getStatusBadge = (status) => {
    const badges = {
      completed: 'badge-completed',
      processing: 'badge-processing',
      waiting: 'badge-waiting',
      warning: 'badge-warning',
      failed: 'badge-failed',
    };
    return <span className={`badge ${badges[status] || ''}`}>{status?.toUpperCase() || 'PENDING'}</span>;
  };

  const renderTimeline = () => {
    const steps = [
      { key: 'ocr', label: 'OCR Extraction', detail: 'Text extraction from document images' },
      { key: 'mrz', label: 'MRZ Processing', detail: 'Machine Readable Zone decoding' },
      { key: 'checksum', label: 'MRZ Checksum', detail: 'ICAO checksum validation' },
      { key: 'ocr_mrz', label: 'OCR ↔ MRZ Verification', detail: 'Cross-reference OCR with MRZ data' },
      { key: 'validation', label: 'Document Validation', detail: 'Format, expiry, consistency checks' },
      { key: 'cross_doc', label: 'Cross-Document Verification', detail: 'Multi-document field comparison' },
      { key: 'tampering', label: 'Tampering Detection', detail: 'Image forensics & anomaly analysis' },
      { key: 'face', label: 'Face Verification', detail: 'Biometric face matching' },
      { key: 'risk', label: 'Risk Assessment', detail: 'Composite risk scoring' },
    ];

    return (
      <div className="timeline">
        {steps.map((step, idx) => {
          const verification = c.verifications?.find(v => v.check_name.toLowerCase().includes(step.label.split(' ')[0].toLowerCase()));
          const status = verification?.status || 'waiting';
          return (
            <div key={step.key} className="timeline-item">
              <div className={`timeline-marker ${status}`}>
                {status === 'completed' && <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><polyline points="20 6 9 17 4 12"/></svg>}
                {status === 'processing' && <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>}
                {status === 'warning' && <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>}
                {status === 'failed' && <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>}
              </div>
              <div className="timeline-content">
                <div className="timeline-step">{step.label} {getStatusBadge(status)}</div>
                <div className="timeline-details">{step.detail}</div>
                {verification?.details && status !== 'waiting' && (
                  <details className="mt-2">
                    <summary className="text-xs text-secondary cursor-pointer">View details</summary>
                    <pre className="mt-2 text-xs bg-navy text-cyan p-2 rounded overflow-auto">{verification.details}</pre>
                  </details>
                )}
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  const renderMRZCard = () => {
    if (!c.documents?.length) return null;
    const passport = c.documents.find(d => d.document_type === 'passport');
    if (!passport?.mrz_data) return null;
    const mrz = JSON.parse(passport.mrz_data);
    const checksum = JSON.parse(passport.verifications?.find(v => v.check_name === 'MRZ Checksum')?.details || '{}');

    return (
      <div className="mrz-card">
        <div className="flex items-center gap-8 mb-4">
          <span className="font-mono text-cyan">MRZ ANALYSIS</span>
          <span className={`badge ${passport.mrz_status === 'VALID' ? 'badge-valid' : 'badge-invalid'}`}>
            {passport.mrz_status}
          </span>
        </div>
        <div className="mrz-line"><span className="mrz-label">Line 1:</span> <span className="mrz-value">{mrz.mrz_lines?.[0] || 'N/A'}</span></div>
        <div className="mrz-line"><span className="mrz-label">Line 2:</span> <span className="mrz-value">{mrz.mrz_lines?.[1] || 'N/A'}</span></div>
        <div className="grid grid-2 gap-8 mt-8">
          <div>
            <div className="text-xs text-cyan mb-2">DECODED FIELDS</div>
            <div className="space-y-1 text-sm">
              <div><span className="text-cyan">Type:</span> {mrz.document_type}</div>
              <div><span className="text-cyan">Country:</span> {mrz.country_code}</div>
              <div><span className="text-cyan">Surname:</span> {mrz.surname}</div>
              <div><span className="text-cyan">Given Names:</span> {mrz.given_names}</div>
              <div><span className="text-cyan">Passport No:</span> {mrz.passport_number}</div>
              <div><span className="text-cyan">Nationality:</span> {mrz.nationality}</div>
              <div><span className="text-cyan">DOB:</span> {mrz.date_of_birth}</div>
              <div><span className="text-cyan">Sex:</span> {mrz.sex}</div>
              <div><span className="text-cyan">Expiry:</span> {mrz.expiry_date}</div>
            </div>
          </div>
          <div>
            <div className="text-xs text-cyan mb-2">CHECKSUM VALIDATION</div>
            <div className="space-y-2">
              {Object.entries(checksum.details || {}).map(([key, val]) => (
                <div key={key} className={`mrz-check ${val.valid ? 'valid' : 'invalid'}`}>
                  <span className="font-mono text-sm">{key.toUpperCase()}</span>
                  <span className="flex-1"></span>
                  <span className={val.valid ? 'text-green-400' : 'text-red-400'}>
                    {val.valid ? '✓ VALID' : '✕ INVALID'}
                  </span>
                  <span className="text-xs text-cyan/60">Exp: {val.expected} | Got: {val.computed}</span>
                </div>
              ))}
              {Object.keys(checksum.details || {}).length === 0 && (
                <div className="mrz-check warning"><span>Checksum data not available</span></div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderCrossDocVerification = () => {
    const crossDoc = c.verifications?.find(v => v.check_name === 'Cross-Document Verification');
    if (!crossDoc) return null;
    const data = JSON.parse(crossDoc.details || '{}');

    return (
      <div>
        <div className="flex items-center gap-8 mb-8">
          <span className="font-medium text-navy">CROSS-DOCUMENT VERIFICATION</span>
          <span className={`badge ${data.match ? 'badge-match' : 'badge-mismatch'}`}>
            {data.match ? 'ALL MATCH' : 'MISMATCHES FOUND'}
          </span>
        </div>
        <table className="comparison-table">
          <thead>
            <tr>
              <th className="field-name">Field</th>
              <th>Passport</th>
              <th>Visa</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {data.comparisons?.map((comp, idx) => (
              <tr key={idx}>
                <td className="field-name">{comp.field}</td>
                <td className="field-value">{comp.passport}</td>
                <td className="field-value">{comp.visa}</td>
                <td>
                  <span className={`badge ${comp.match ? 'badge-match' : 'badge-mismatch'}`}>
                    {comp.match ? '✓ MATCH' : '✕ MISMATCH'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {data.mismatches?.length > 0 && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="font-medium text-red-800 mb-2">Mismatch Details:</div>
            <ul className="text-sm text-red-700 space-y-1">
              {data.mismatches.map((field, idx) => (
                <li key={idx}>• {field} does not match between documents</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  };

  const renderTampering = () => {
    const tampering = c.tampering_results?.[0];
    if (!tampering) return null;

    return (
      <div>
        <div className="flex items-center gap-8 mb-8">
          <span className="font-medium text-navy">TAMPERING ANALYSIS</span>
          <span className={`badge ${tampering.tampering_status === 'CLEAN' ? 'badge-clean' : tampering.tampering_status === 'WARNING' ? 'badge-warning' : 'badge-detected'}`}>
            {tampering.tampering_status}
          </span>
        </div>

        <div className="grid grid-3 gap-16 mb-16">
          <div className="image-panel">
            <span className="panel-label">ORIGINAL RGB</span>
            {c.documents?.[0]?.file_path && (
              <img src={api.storage(c.documents[0].file_path.replace('storage/', ''))} alt="Original Document" />
            )}
            {!c.documents?.[0]?.file_path && <div className="image-panel-placeholder">Document Image</div>}
          </div>
          <div className="image-panel">
            <span className="panel-label">TAMPER HEATMAP</span>
            {tampering.heatmap_path && (
              <img src={api.storage(tampering.heatmap_path.replace('storage/', ''))} alt="Tamper Heatmap" />
            )}
            {!tampering.heatmap_path && <div className="image-panel-placeholder">Heatmap Visualization</div>}
          </div>
          <div className="image-panel">
            <span className="panel-label">NOISE RESIDUAL</span>
            {tampering.noise_residual_path && (
              <img src={api.storage(tampering.noise_residual_path.replace('storage/', ''))} alt="Noise Residual" />
            )}
            {!tampering.noise_residual_path && <div className="image-panel-placeholder">Noise Analysis</div>}
          </div>
        </div>

        <div className="grid grid-3 gap-16">
          <div className="stat-card text-center">
            <div className="stat-icon stat-icon-red">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
            </div>
            <div className="stat-value">{Math.round(tampering.confidence * 100)}%</div>
            <div className="stat-label">Tampering Confidence</div>
          </div>
          <div className="stat-card text-center">
            <div className="stat-icon stat-icon-amber">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
              </svg>
            </div>
            <div className="stat-value">{tampering.suspicious_region || 'None'}</div>
            <div className="stat-label">Suspicious Region</div>
          </div>
          <div className="stat-card text-center">
            <div className="stat-icon stat-icon-cyan">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="3"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
              </svg>
            </div>
            <div className="stat-value">{tampering.tampering_status}</div>
            <div className="stat-label">Overall Status</div>
          </div>
        </div>

        <div className="mt-8 p-4 bg-navy/5 rounded-lg">
          <div className="font-mono text-xs text-cyan mb-2">Technical Details:</div>
          <pre className="text-xs text-white/80 overflow-auto">{tampering.details}</pre>
        </div>
      </div>
    );
  };

  const renderFaceVerification = () => {
    const fv = c.face_verification;
    if (!fv) return null;

    return (
      <div>
        <div className="flex items-center gap-8 mb-8">
          <span className="font-medium text-navy">FACE VERIFICATION</span>
          <span className={`badge ${fv.match_status === 'MATCH' ? 'badge-match' : fv.match_status === 'WARNING' ? 'badge-warning' : 'badge-mismatch'}`}>
            {fv.match_status}
          </span>
        </div>

        <div className="face-comparison">
          <div className="face-panel">
            <div className="face-panel-label">Document Photo</div>
            <div className="face-panel-image">
              {fv.document_photo_path ? (
                <img src={api.storage(fv.document_photo_path.replace('storage/', ''))} alt="Document Photo" />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-secondary">No Photo</div>
              )}
            </div>
          </div>
          <div className="face-panel">
            <div className="face-panel-label">Live Photo</div>
            <div className="face-panel-image">
              {fv.live_photo_path ? (
                <img src={api.storage(fv.live_photo_path.replace('storage/', ''))} alt="Live Photo" />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-secondary">No Photo</div>
              )}
            </div>
          </div>
        </div>

        <div className="flex justify-center mt-8">
          <div className="text-center">
            <div className="face-similarity">{Math.round(fv.similarity_score * 100)}%</div>
            <div className={`face-status ${fv.match_status === 'MATCH' ? 'match' : fv.match_status === 'WARNING' ? 'warning' : 'mismatch'}`}>
              Similarity Score
            </div>
          </div>
        </div>

        <div className="mt-8 p-4 bg-navy/5 rounded-lg">
          <div className="font-mono text-xs text-cyan mb-2">Verification Details:</div>
          <pre className="text-xs text-white/80 overflow-auto">{fv.details}</pre>
        </div>
      </div>
    );
  };

  const renderRiskAssessment = () => {
    if (!riskAssessment) return null;

    return (
      <div>
        <div className="flex items-center gap-8 mb-8">
          <span className="font-medium text-navy">RISK ASSESSMENT</span>
          <span className={`badge ${riskColors[riskAssessment.risk_level]}`}>
            {riskAssessment.risk_level.toUpperCase()} RISK
          </span>
        </div>

        <div className={`risk-meter ${riskAssessment.risk_level}`} style={{ maxWidth: 400 }}>
          <div className="risk-meter-fill" style={{ width: `${riskAssessment.score}%` }}></div>
        </div>
        <div className="risk-meter-markers">
          <span className="risk-marker-marker low">LOW (0-29)</span>
          <span className="risk-marker-marker medium">MEDIUM (30-59)</span>
          <span className="risk-marker-marker high">HIGH (60-100)</span>
        </div>

        <div className="mt-8 risk-breakdown">
          {JSON.parse(riskAssessment.reasons || '[]').map((reason, idx) => {
            const level = reason.includes('Failed') || reason.includes('Detected') || reason.includes('Mismatch') ? 'high' : 'medium';
            return (
              <div key={idx} className="risk-reason">
                <div className={`risk-reason-icon ${level}`}>
                  {level === 'high' ? '✕' : '⚠'}
                </div>
                <div className="risk-reason-text">{reason}</div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <Link to="/" className="btn btn-outline mb-4">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/>
            </svg>
            Back to Dashboard
          </Link>
          <div className="flex items-center gap-16">
            <h1 className="page-title">{c.passenger_name}</h1>
            <span className={`badge ${riskColors[c.risk_level]}`} style={{ fontSize: '16px', padding: '8px 16px' }}>
              {c.risk_level.toUpperCase()} RISK
            </span>
          </div>
          <div className="text-secondary mt-2">
            Case ID: {c.case_id} | {c.nationality} | DOB: {c.date_of_birth} | Passport: {c.passport_number}
          </div>
        </div>
        <div className="flex gap-8">
          <button className="btn btn-primary" onClick={handleProcess} disabled={processing}>
            {processing ? 'Processing...' : 'Run Full Verification'}
          </button>
          <button className="btn btn-secondary" onClick={() => setShowFaceModal(true)}>
            Face Verification
          </button>
        </div>
      </div>

      {error && <div className="alert alert-error mb-8">{error}</div>}

      <div className="tabs mb-8">
        <button className={`tab ${activeTab === 'overview' ? 'active' : ''}`} onClick={() => setActiveTab('overview')}>
          Overview
        </button>
        <button className={`tab ${activeTab === 'timeline' ? 'active' : ''}`} onClick={() => setActiveTab('timeline')}>
          Processing Timeline
        </button>
        <button className={`tab ${activeTab === 'mrz' ? 'active' : ''}`} onClick={() => setActiveTab('mrz')}>
          MRZ Analysis
        </button>
        <button className={`tab ${activeTab === 'crossdoc' ? 'active' : ''}`} onClick={() => setActiveTab('crossdoc')}>
          Cross-Document
        </button>
        <button className={`tab ${activeTab === 'tampering' ? 'active' : ''}`} onClick={() => setActiveTab('tampering')}>
          Tampering Detection
        </button>
        <button className={`tab ${activeTab === 'face' ? 'active' : ''}`} onClick={() => setActiveTab('face')}>
          Face Verification
        </button>
        <button className={`tab ${activeTab === 'risk' ? 'active' : ''}`} onClick={() => setActiveTab('risk')}>
          Risk Assessment
        </button>
      </div>

      <div className="tab-content {activeTab === 'overview' ? 'active' : ''}">
        <div className="grid grid-2 gap-16 mb-16">
          <div className="card">
            <div className="card-header"><h2 className="card-title">Documents</h2></div>
            <div className="card-body space-y-8">
              {c.documents?.map(doc => (
                <div key={doc.id} className="p-4 bg-bg rounded-lg border border-border">
                  <div className="flex items-center justify-between mb-4">
                    <span className="font-medium">{doc.original_filename}</span>
                    <span className={`doc-tag ${doc.document_type}`}>
                      {doc.document_type.toUpperCase()}
                    </span>
                  </div>
                  <div className="grid grid-2 gap-4 text-sm">
                    <div><span className="text-secondary">MRZ Status:</span> <span className={`badge ${doc.mrz_status === 'VALID' ? 'badge-valid' : 'badge-invalid'}`}>{doc.mrz_status}</span></div>
                    <div><span className="text-secondary">Checksum:</span> <span className={`badge ${doc.checksum_status === 'VALID' ? 'badge-valid' : 'badge-invalid'}`}>{doc.checksum_status}</span></div>
                    <div><span className="text-secondary">OCR/MRZ:</span> <span className={`badge ${doc.ocr_mrz_match === 'MATCH' ? 'badge-match' : 'badge-mismatch'}`}>{doc.ocr_mrz_match}</span></div>
                    <div><span className="text-secondary">Validation:</span> <span className={`badge ${doc.validation_status === 'VALID' ? 'badge-valid' : 'badge-invalid'}`}>{doc.validation_status}</span></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="card">
            <div className="card-header"><h2 className="card-title">Quick Summary</h2></div>
            <div className="card-body space-y-4">
              {c.verifications?.map(v => (
                <div key={v.id} className="flex items-center justify-between p-3 bg-bg rounded-lg">
                  <span className="font-medium">{v.check_name}</span>
                  {getStatusBadge(v.status)}
                </div>
              ))}
            </div>
          </div>
        </div>

        {renderRiskAssessment()}
      </div>

      <div className={`tab-content ${activeTab === 'timeline' ? 'active' : ''}`}>
        <div className="card">
          <div className="card-body">{renderTimeline()}</div>
        </div>
      </div>

      <div className={`tab-content ${activeTab === 'mrz' ? 'active' : ''}`}>
        <div className="card">
          <div className="card-body">{renderMRZCard()}</div>
        </div>
      </div>

      <div className={`tab-content ${activeTab === 'crossdoc' ? 'active' : ''}`}>
        <div className="card">
          <div className="card-body">{renderCrossDocVerification()}</div>
        </div>
      </div>

      <div className={`tab-content ${activeTab === 'tampering' ? 'active' : ''}`}>
        <div className="card">
          <div className="card-body">{renderTampering()}</div>
        </div>
      </div>

      <div className={`tab-content ${activeTab === 'face' ? 'active' : ''}`}>
        <div className="card">
          <div className="card-body">{renderFaceVerification()}</div>
        </div>
      </div>

      <div className={`tab-content ${activeTab === 'risk' ? 'active' : ''}`}>
        <div className="card">
          <div className="card-body">{renderRiskAssessment()}</div>
        </div>
      </div>

      {showFaceModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50" onClick={() => setShowFaceModal(false)}>
          <div className="card w-full max-w-md" onClick={e => e.stopPropagation()}>
            <div className="card-header flex justify-between items-center">
              <h2 className="card-title">Upload Face Photos</h2>
              <button className="btn btn-outline" onClick={() => setShowFaceModal(false)}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>
            <form onSubmit={handleFaceUpload} className="card-body space-y-4">
              <div className="input-group">
                <label className="input-label">Document Photo</label>
                <input type="file" accept="image/*" className="input-field" onChange={e => setFacePhotos({...facePhotos, doc: e.target.files[0]})} required />
              </div>
              <div className="input-group">
                <label className="input-label">Live Photo</label>
                <input type="file" accept="image/*" className="input-field" onChange={e => setFacePhotos({...facePhotos, live: e.target.files[0]})} required />
              </div>
              <div className="flex justify-end gap-8 mt-8">
                <button type="button" className="btn btn-secondary" onClick={() => setShowFaceModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={uploading}>
                  {uploading ? 'Verifying...' : 'Verify Face'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}