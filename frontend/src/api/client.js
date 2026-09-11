// Central API Client with transparent fallback to mock database

import { MOCK_STANDARDS } from '../data/mockStandards';
import { MOCK_LICENCES, MOCK_HUID_RECORDS } from '../data/mockLicences';
import { MOCK_CHAT_RESPONSES, DEFAULT_BOT_RESPONSE } from '../data/mockChat';

const RAW_API_URL = import.meta.env.VITE_API_BASE_URL || '';
const API_BASE_URL = RAW_API_URL ? RAW_API_URL.replace(/\/+$/, '') : (import.meta.env.DEV ? 'http://127.0.0.1:8000' : '');

/**
 * Helper to make API requests with fallback to mock data
 */
async function fetchWithFallback(endpoint, options, fallbackFn) {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5-second timeout for live API check

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    return { data, isMock: false };
  } catch (err) {
    // Graceful fallback to mock data
    const mockData = await fallbackFn();
    return { data: mockData, isMock: true, apiNote: 'Operating in RAG Mock Mode (Backend API disconnected)' };
  }
}

/**
 * 1. POST /ask - BIS Conversational Assistant Endpoint
 */
export async function sendChatMessage(query, language = null) {
  if (!query || !query.trim()) {
    throw new Error('Please enter a question.');
  }
  if (query.trim().length > 1000) {
    throw new Error('Question exceeds maximum limit of 1000 characters. Please shorten your query.');
  }

  const payload = { question: query.trim() };
  if (language && language !== 'auto') {
    payload.language = language;
  }

  const response = await fetch(`${API_BASE_URL}/ask`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let errorMsg = `Server error (${response.status})`;
    if (response.status === 429) {
      errorMsg = 'Too many requests. Please wait a moment before trying again.';
    } else if (response.status === 503) {
      errorMsg = 'AI Assistant service is temporarily unavailable. Please try again shortly.';
    } else {
      try {
        const errBody = await response.json();
        if (errBody?.detail) {
          if (Array.isArray(errBody.detail)) {
            errorMsg = errBody.detail.map((d) => d.msg || d.message).join('; ');
          } else {
            errorMsg = String(errBody.detail);
          }
        }
      } catch (_) {}
    }
    throw new Error(errorMsg);
  }

  const data = await response.json();
  return { data, isMock: false };
}

/**
 * GET /bis/services - BIS Application Service Categories
 */
export async function getBISServices() {
  return fetchWithFallback(
    '/bis/services',
    { method: 'GET' },
    async () => [
      { id: 'product_certification', name: 'Product Certification', description: 'Information on ISI mark scheme and product certification.' },
      { id: 'bis_registration', name: 'BIS Registration', description: 'Compulsory Registration Scheme (CRS) for electronics.' },
      { id: 'licensing', name: 'Licensing', description: 'Guidance on BIS CML licence application and verification.' },
      { id: 'indian_standards', name: 'Indian Standards', description: 'Directory of formulated Indian Standards (IS codes).' },
      { id: 'testing', name: 'Testing', description: 'Information on BIS laboratory testing procedures.' }
    ]
  );
}

/**
 * POST /bis/search - Dedicated BIS Search Endpoint
 */
export async function searchBIS(query, service = null, language = null) {
  if (!query || !query.trim()) {
    throw new Error('Please enter a search query.');
  }
  if (query.trim().length > 1000) {
    throw new Error('Search query exceeds maximum limit of 1000 characters. Please shorten your query.');
  }

  const payload = { query: query.trim(), service: service };
  if (language && language !== 'auto') {
    payload.language = language;
  }

  const response = await fetch(`${API_BASE_URL}/bis/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let errorMsg = `Server error (${response.status})`;
    if (response.status === 429) {
      errorMsg = 'Too many requests. Please wait a moment before trying again.';
    } else if (response.status === 503) {
      errorMsg = 'AI Assistant service is temporarily unavailable. Please try again shortly.';
    } else {
      try {
        const errBody = await response.json();
        if (errBody?.detail) {
          if (Array.isArray(errBody.detail)) {
            errorMsg = errBody.detail.map((d) => d.msg || d.message).join('; ');
          } else {
            errorMsg = String(errBody.detail);
          }
        }
      } catch (_) {}
    }
    throw new Error(errorMsg);
  }

  const data = await response.json();
  return { data, isMock: false };
}

/**
 * 2. POST /api/search - Standards Search
 */
export async function searchStandards(query = '', category = 'All Categories') {
  return fetchWithFallback(
    '/api/search',
    {
      method: 'POST',
      body: JSON.stringify({ query, category }),
    },
    async () => {
      await new Promise((resolve) => setTimeout(resolve, 400));
      let results = MOCK_STANDARDS;

      if (category && category !== 'All Categories') {
        results = results.filter((s) => s.category === category);
      }

      if (query.trim()) {
        const q = query.toLowerCase();
        results = results.filter(
          (s) =>
            s.code.toLowerCase().includes(q) ||
            s.title.toLowerCase().includes(q) ||
            s.description.toLowerCase().includes(q) ||
            s.category.toLowerCase().includes(q)
        );
      }

      return results;
    }
  );
}

/**
 * 3. POST /api/standards/recommend - Discovery Wizard
 */
export async function recommendStandards(productSpecs) {
  return fetchWithFallback(
    '/api/standards/recommend',
    {
      method: 'POST',
      body: JSON.stringify({ specs: productSpecs }),
    },
    async () => {
      await new Promise((resolve) => setTimeout(resolve, 600));
      return {
        mandatory: [MOCK_STANDARDS[0], MOCK_STANDARDS[1]],
        voluntary: [MOCK_STANDARDS[2]],
        recommendationSummary: 'Based on your product input, compulsory ISI certification is required prior to commercial distribution.'
      };
    }
  );
}

/**
 * 4. POST /documents/upload - Document Processing & Vector Indexing
 */
export async function uploadDocument(file) {
  if (!file) {
    throw new Error('No file selected.');
  }
  if (file.size === 0) {
    throw new Error('Selected file is empty (0 bytes).');
  }
  if (file.size > 15 * 1024 * 1024) {
    throw new Error('File size exceeds the 15 MB limit.');
  }
  const ext = file.name ? file.name.slice(file.name.lastIndexOf('.')).toLowerCase() : '';
  const allowed = ['.pdf', '.docx', '.txt'];
  if (!allowed.includes(ext)) {
    throw new Error('Unsupported file type. Please upload a PDF, DOCX, or TXT file.');
  }

  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/documents/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    let errorMsg = `Upload failed (${response.status})`;
    if (response.status === 413) {
      errorMsg = 'File size exceeds maximum allowed limit (15 MB).';
    } else if (response.status === 422) {
      errorMsg = 'Failed to process document text or extract readable content.';
    }
    try {
      const errBody = await response.json();
      if (errBody?.detail) {
        if (Array.isArray(errBody.detail)) {
          errorMsg = errBody.detail.map((d) => d.msg || d.message).join('; ');
        } else {
          errorMsg = String(errBody.detail);
        }
      }
    } catch (_) {}
    throw new Error(errorMsg);
  }

  const data = await response.json();
  return { data, isMock: false };
}

/**
 * 5. GET /documents - Retrieve list of uploaded & indexed documents
 */
export async function getDocuments() {
  const response = await fetch(`${API_BASE_URL}/documents`, {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
    },
  });

  if (!response.ok) {
    let errorMsg = `Failed to fetch documents (${response.status})`;
    try {
      const errBody = await response.json();
      if (errBody?.detail) {
        if (Array.isArray(errBody.detail)) {
          errorMsg = errBody.detail.map((d) => d.msg || d.message).join('; ');
        } else {
          errorMsg = String(errBody.detail);
        }
      }
    } catch (_) {}
    throw new Error(errorMsg);
  }

  const data = await response.json();
  return { data: data.documents || [], isMock: false };
}

/**
 * 6. GET /documents/:id/chunks - Retrieve chunk metadata for a document
 */
export async function getDocumentChunks(documentId) {
  const response = await fetch(`${API_BASE_URL}/documents/${encodeURIComponent(documentId)}/chunks`, {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
    },
  });

  if (!response.ok) {
    let errorMsg = `Failed to fetch chunks (${response.status})`;
    try {
      const errBody = await response.json();
      if (errBody?.detail) {
        errorMsg = String(errBody.detail);
      }
    } catch (_) {}
    throw new Error(errorMsg);
  }

  const data = await response.json();
  return { data, isMock: false };
}

/**
 * 5. GET /api/verification/status - Licence / HUID Verification
 */
export async function verifyLicenceOrHuid(type, queryNumber) {
  const clean = queryNumber.trim().toUpperCase();
  return fetchWithFallback(
    `/api/verification/status?type=${type}&query=${clean}`,
    { method: 'GET' },
    async () => {
      await new Promise((resolve) => setTimeout(resolve, 500));
      if (type === 'huid') {
        const found = MOCK_HUID_RECORDS[clean];
        if (found) return { found: true, record: found, type: 'huid' };
        return { found: false, message: `No active HUID record found for "${clean}". Ensure code is 6 characters etched on gold item.`, type: 'huid' };
      } else {
        const found = MOCK_LICENCES[clean];
        if (found) return { found: true, record: found, type: 'cml' };
        return { found: false, message: `No active BIS CML licence found for number "${clean}". Please verify number or check official Manakonline registry.`, type: 'cml' };
      }
    }
  );
}
