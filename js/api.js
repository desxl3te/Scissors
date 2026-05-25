(function () {
    const API_BASE = 'http://127.0.0.1:8000';
    const DASHBOARD_BASE = 'http://127.0.0.1:5000';
    const SESSION_KEY = 'scissors_session';

    function parseResponse(response, fallbackMessage) {
        return response.text().then((rawText) => {
            let payload = null;

            if (rawText) {
                try {
                    payload = JSON.parse(rawText);
                } catch (error) {
                    payload = { message: rawText };
                }
            }

            if (!response.ok) {
                const error = new Error(
                    (payload && (payload.detail || payload.message)) || fallbackMessage
                );
                error.status = response.status;
                throw error;
            }

            return payload;
        });
    }

    async function request(baseUrl, path, options = {}) {
        const session = getSession();
        const headers = { ...(options.headers || {}) };

        if (options.body && !headers['Content-Type']) {
            headers['Content-Type'] = 'application/json';
        }

        if (options.auth !== false && session.token) {
            headers.Authorization = `Bearer ${session.token}`;
        }

        const response = await fetch(`${baseUrl}${path}`, {
            method: options.method || 'GET',
            headers,
            body: options.body ? JSON.stringify(options.body) : undefined
        });

        return parseResponse(response, 'Ошибка запроса.');
    }

    function getSession() {
        try {
            return JSON.parse(localStorage.getItem(SESSION_KEY)) || { token: null, user: null };
        } catch (error) {
            return { token: null, user: null };
        }
    }

    function saveSession(payload) {
        localStorage.setItem(SESSION_KEY, JSON.stringify(payload));
    }

    function clearSession() {
        localStorage.removeItem(SESSION_KEY);
    }

    window.ScissorsApi = {
        config: {
            apiBase: API_BASE,
            dashboardBase: DASHBOARD_BASE
        },
        getSession,
        saveSession,
        clearSession,
        getAbout() {
            return request(API_BASE, '/api/about', { auth: false });
        },
        getHealth() {
            return request(API_BASE, '/health', { auth: false });
        },
        login(data) {
            return request(API_BASE, '/api/auth/login', {
                method: 'POST',
                body: data,
                auth: false
            });
        },
        register(data) {
            return request(API_BASE, '/api/auth/register', {
                method: 'POST',
                body: data,
                auth: false
            });
        },
        getProfile() {
            return request(API_BASE, '/api/auth/me');
        },
        updateProfile(data) {
            return request(API_BASE, '/api/auth/me', {
                method: 'PATCH',
                body: data
            });
        },
        uploadAvatar(file) {
            const session = getSession();
            const formData = new FormData();
            formData.append('file', file);
            return fetch(`${API_BASE}/api/auth/me/avatar`, {
                method: 'POST',
                headers: session.token ? { Authorization: `Bearer ${session.token}` } : {},
                body: formData
            }).then((response) => parseResponse(response, 'Не удалось загрузить аватар.'));
        },
        getTables() {
            return request(API_BASE, '/api/tables', { auth: false });
        },
        getAvailability(params) {
            const search = new URLSearchParams(params);
            return request(API_BASE, `/api/tables/availability?${search.toString()}`, {
                auth: false
            });
        },
        createReservation(data) {
            return request(API_BASE, '/api/reservations', {
                method: 'POST',
                body: data
            });
        },
        getMyReservations() {
            return request(API_BASE, '/api/reservations/me');
        },
        cancelReservation(id) {
            return request(API_BASE, `/api/reservations/${id}/cancel`, {
                method: 'PATCH'
            });
        },
        sendSupport(data) {
            return request(API_BASE, '/api/support', {
                method: 'POST',
                body: data
            });
        },
        getDashboard() {
            return request(DASHBOARD_BASE, '/api/dashboard', { auth: false });
        }
    };
})();
