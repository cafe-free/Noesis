/**
 * Noesis Frontend API Client & Auth Manager
 * Self-contained Vanilla JS with Fetch API
 */

const STORAGE_KEYS = {
  ACCESS_TOKEN: 'noesis_access_token',
  REFRESH_TOKEN: 'noesis_refresh_token',
  USER_DATA: 'noesis_user_data',
};

const Auth = {
  getAccessToken() {
    return localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
  },

  getRefreshToken() {
    return localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
  },

  getUserData() {
    try {
      const data = localStorage.getItem(STORAGE_KEYS.USER_DATA);
      return data ? JSON.parse(data) : null;
    } catch {
      return null;
    }
  },

  setSession(tokens, user = null) {
    if (tokens?.access_token) {
      localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, tokens.access_token);
    }
    if (tokens?.refresh_token) {
      localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, tokens.refresh_token);
    }
    if (user) {
      localStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(user));
    }
  },

  clearSession() {
    localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.USER_DATA);
  },

  isAuthenticated() {
    return !!this.getAccessToken();
  },

  async login(email, password) {
    const res = await fetch('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || 'Login failed');
    }
    this.setSession(data);
    const user = await this.fetchCurrentUser();
    return { tokens: data, user };
  },

  async register(email, password, username) {
    const res = await fetch('/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email,
        password,
        username: username || undefined,
      }),
    });
    const data = await res.json();
    if (!res.ok) {
      const detail = Array.isArray(data.detail)
        ? data.detail.map((e) => e.msg || e.message).join(', ')
        : data.detail || 'Registration failed';
      throw new Error(detail);
    }
    this.setSession(data);
    const user = await this.fetchCurrentUser();
    return { tokens: data, user };
  },

  async fetchCurrentUser() {
    const token = this.getAccessToken();
    if (!token) return null;

    const res = await fetch('/auth/me', {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) {
      return null;
    }
    const user = await res.json();
    localStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(user));
    return user;
  },

  async refresh() {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      this.clearSession();
      throw new Error('No refresh token available');
    }

    const res = await fetch('/auth/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    const data = await res.json();
    if (!res.ok) {
      this.clearSession();
      throw new Error(data.detail || 'Session refresh expired');
    }

    this.setSession(data);
    return data;
  },

  async logout(redirectUrl = '/login') {
    const refreshToken = this.getRefreshToken();
    if (refreshToken) {
      try {
        await fetch('/auth/logout', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });
      } catch (err) {
        console.warn('Logout network error:', err);
      }
    }
    this.clearSession();
    if (redirectUrl) {
      window.location.href = redirectUrl;
    }
  },

  requireAuth() {
    if (!this.isAuthenticated()) {
      window.location.href = '/login';
      return false;
    }
    return true;
  },

  redirectIfAuthenticated() {
    if (this.isAuthenticated()) {
      window.location.href = '/dashboard';
      return true;
    }
    return false;
  },
};

/**
 * Reusable fetch wrapper that automatically:
 * 1. Attaches Authorization header with Bearer token
 * 2. Serializes JSON bodies
 * 3. Attempts token refresh on 401 response and retries request
 * 4. Redirects to /login if unauthenticated or session expired
 */
async function apiFetch(url, options = {}) {
  const opts = { ...options };
  opts.headers = { ...opts.headers };

  // Set Content-Type for JSON objects
  if (
    opts.body &&
    typeof opts.body === 'object' &&
    !(opts.body instanceof FormData)
  ) {
    opts.body = JSON.stringify(opts.body);
    if (!opts.headers['Content-Type']) {
      opts.headers['Content-Type'] = 'application/json';
    }
  }

  // Attach token if available
  const token = Auth.getAccessToken();
  if (token && !opts.headers['Authorization']) {
    opts.headers['Authorization'] = `Bearer ${token}`;
  }

  let response = await fetch(url, opts);

  // Handle 401 Unauthorized with token refresh retry
  if (
    response.status === 401 &&
    !url.startsWith('/auth/login') &&
    !url.startsWith('/auth/register') &&
    !url.startsWith('/auth/refresh')
  ) {
    try {
      const newTokens = await Auth.refresh();
      // Retry with new token
      opts.headers['Authorization'] = `Bearer ${newTokens.access_token}`;
      response = await fetch(url, opts);
    } catch (refreshErr) {
      Auth.clearSession();
      window.location.href = '/login';
      throw new Error('Session expired. Please log in again.');
    }
  }

  return response;
}

/**
 * UI Utilities
 */
const UI = {
  renderJson(elementId, data, status = null) {
    const el = document.getElementById(elementId);
    if (!el) return;
    const formatted =
      typeof data === 'string' ? data : JSON.stringify(data, null, 2);
    el.textContent = status ? `[Status: ${status}]\n\n${formatted}` : formatted;
  },

  showBanner(elementId, message, type = 'info') {
    const el = document.getElementById(elementId);
    if (!el) return;
    el.textContent = message;
    el.className = `banner banner-${type}`;
    el.style.display = 'block';
  },

  hideBanner(elementId) {
    const el = document.getElementById(elementId);
    if (el) {
      el.style.display = 'none';
    }
  },
};
