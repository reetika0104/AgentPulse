/**
 * PULSE API Client
 * Handles authentication and API requests to the PULSE backend.
 */

const API_BASE = '/api/v1';

class PulseAPI {
  constructor() {
    this.token = localStorage.getItem('pulse_token');
  }

  setToken(token) {
    this.token = token;
    localStorage.setItem('pulse_token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('pulse_token');
  }

  isAuthenticated() {
    return !!this.token;
  }

  async request(path, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers,
    });

    if (response.status === 401) {
      this.clearToken();
      window.location.reload();
      throw new Error('Unauthorized');
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Auth
  async login(username, password) {
    const data = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
    this.setToken(data.access_token);
    return data;
  }

  logout() {
    this.clearToken();
  }

  // Brief
  async getLatestBrief() {
    return this.request('/brief/latest');
  }

  async triggerBrief() {
    return this.request('/brief/trigger', { method: 'POST' });
  }

  // Executions
  async getExecutions(limit = 20) {
    return this.request(`/executions?limit=${limit}`);
  }

  async getExecution(id) {
    return this.request(`/executions/${id}`);
  }

  // Health
  async getHealth() {
    return this.request('/health');
  }

  async getServiceHealth() {
    return this.request('/health/services');
  }

  // Status
  async getStatus() {
    return this.request('/status');
  }

  // Metrics
  async getMetrics() {
    return this.request('/agent/metrics');
  }

  // Agent phases
  async getPhases() {
    return this.request('/agent/phases');
  }

  // Config
  async getConfig() {
    return this.request('/config');
  }
}

export const api = new PulseAPI();
export default api;
