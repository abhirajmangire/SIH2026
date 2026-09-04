const API_BASE = 'http://localhost:8000/api';

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function request(endpoint, options = {}) {
  const token = localStorage.getItem('token');
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new ApiError(error.detail || 'Request failed', response.status);
  }

  if (response.status === 204) return null;
  return response.json();
}

export const api = {
  auth: {
    login: (credentials) => request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    }),
  },

  dashboard: {
    getStats: () => request('/dashboard/stats'),
    getCases: () => request('/dashboard/cases'),
  },

  cases: {
    create: (data) => request('/cases', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    getDetail: (id) => request(`/cases/${id}`),
    uploadDocument: (caseId, documentType, file) => {
      const formData = new FormData();
      formData.append('document_type', documentType);
      formData.append('file', file);
      const token = localStorage.getItem('token');
      return fetch(`${API_BASE}/cases/${caseId}/documents`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      }).then(res => {
        if (!res.ok) throw new ApiError('Upload failed', res.status);
        return res.json();
      });
    },
    process: (caseId) => request(`/cases/${caseId}/process`, { method: 'POST' }),
    uploadFacePhotos: (caseId, documentPhoto, livePhoto) => {
      const formData = new FormData();
      formData.append('document_photo', documentPhoto);
      formData.append('live_photo', livePhoto);
      const token = localStorage.getItem('token');
      return fetch(`${API_BASE}/cases/${caseId}/face-verification`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      }).then(res => {
        if (!res.ok) throw new ApiError('Face upload failed', res.status);
        return res.json();
      });
    },
  },

  storage: (path) => `http://localhost:8000/storage/${path}`,
};

export { ApiError };