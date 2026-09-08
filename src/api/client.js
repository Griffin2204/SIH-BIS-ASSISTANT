// Central API Client with transparent fallback to mock database

import { MOCK_STANDARDS } from '../data/mockStandards';
import { MOCK_LICENCES, MOCK_HUID_RECORDS } from '../data/mockLicences';
import { MOCK_CHAT_RESPONSES, DEFAULT_BOT_RESPONSE } from '../data/mockChat';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Helper to make API requests with fallback to mock data
 */
async function fetchWithFallback(endpoint, options, fallbackFn) {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3000); // 3-second timeout for live API check

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
 * 1. POST /api/chat - RAG Conversational Assistant
 */
export async function sendChatMessage(query, conversationHistory = []) {
  return fetchWithFallback(
    '/api/chat',
    {
      method: 'POST',
      body: JSON.stringify({ question: query, history: conversationHistory }),
    },
    async () => {
      await new Promise((resolve) => setTimeout(resolve, 800)); // Simulate network latency
      const lower = query.toLowerCase();

      const matched = MOCK_CHAT_RESPONSES.find((item) =>
        item.keywords.some((kw) => lower.includes(kw))
      );

      if (matched) {
        return {
          answer: matched.answer,
          confidenceScore: matched.confidenceScore,
          confidenceLabel: matched.confidenceLabel,
          citations: matched.citations,
        };
      }

      return {
        answer: DEFAULT_BOT_RESPONSE.answer,
        confidenceScore: DEFAULT_BOT_RESPONSE.confidenceScore,
        confidenceLabel: DEFAULT_BOT_RESPONSE.confidenceLabel,
        citations: DEFAULT_BOT_RESPONSE.citations,
      };
    }
  );
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
 * 4. POST /api/documents/upload - Document Processing & OCR
 */
export async function uploadDocument(file) {
  return fetchWithFallback(
    '/api/documents/upload',
    {
      method: 'POST',
      body: JSON.stringify({ filename: file.name, size: file.size }),
    },
    async () => {
      await new Promise((resolve) => setTimeout(resolve, 1200));
      return {
        fileId: `DOC-${Date.now()}`,
        filename: file.name,
        fileSizeFormatted: `${(file.size / (1024 * 1024)).toFixed(2)} MB`,
        status: 'Extracted & Analyzed',
        extractedText: `SAMPLE OCR EXTRACT: Product: PVC Electrical Conduit. Test Voltage: 1100V. Manufacturer: Polycab Wires. Standard Reference: IS 694. Compliance Pass rate: 98.4%.`,
        identifiedStandard: 'IS 694:2010',
        confidenceScore: '96.5%',
        suggestedActions: ['Apply for SIT Endorsement', 'Schedule Audit']
      };
    }
  );
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
