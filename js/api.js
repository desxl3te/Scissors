(function () {
//конфигурация
    const API_BASE = 'http://127.0.0.1:8000';
    const DASHBOARD_BASE = 'http://127.0.0.1:5000';
    const SESSION_KEY = 'scissors_session';
//вспомогательные функции
    function extractMessage(payload, fallbackMessage) {
        if (!payload) return fallbackMessage;

        const detail = payload.detail;

        if (typeof detail === 'string') return detail;

        if (Array.isArray(detail) && detail.length) {
            const messages = detail
                .map((item) => (item && typeof item.msg === 'string' ? item.msg : null))
                .filter(Boolean);
            if (messages.length) return messages.join('; ');
        }

        if (detail && typeof detail === 'object' && typeof detail.msg === 'string') {
            return detail.msg;
        }

        if (typeof payload.message === 'string') return payload.message;

        return fallbackMessage;
    }

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
                const error = new Error(extractMessage(payload, fallbackMessage));
                error.status = response.status;
                throw error;
            }

            return payload;
        });
    }

    async function request(baseUrl, path, options = {}) {
    //получаем текущий токен
        const session = getSession();
        const headers = { ...(options.headers || {}) };

        if (options.body && !headers['Content-Type']) {
            headers['Content-Type'] = 'application/json';
        }

        if (options.auth !== false && session.token) {
            headers.Authorization = `Bearer ${session.token}`;
        }
        //выполняем запрос через фетч (встроенная в браузере кнопка запроса к серверу)
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
//публичный апи
    window.ScissorsApi = {
    //конфигурация
        config: {
            apiBase: API_BASE,
            dashboardBase: DASHBOARD_BASE
        },
        getSession,
        saveSession,
        clearSession,
        //информация о сервисе
        getAbout() {
            return request(API_BASE, '/api/about', { auth: false });
        },
        //проверка здоровья сервиса
        getHealth() {
            return request(API_BASE, '/health', { auth: false });
        },
        //авторизация вход
        login(data) {
            return request(API_BASE, '/api/auth/login', {
                method: 'POST',
                body: data,
                auth: false
            });
        },
        //регистрация нового пользователя
        register(data) {
            return request(API_BASE, '/api/auth/register', {
                method: 'POST',
                body: data,
                auth: false
            });
        },
        //получение данных текущего пользователя
        getProfile() {
            return request(API_BASE, '/api/auth/me');
        },
        //обновление данных профиля
        updateProfile(data) {
            return request(API_BASE, '/api/auth/me', {
                method: 'PATCH',
                body: data
            });
        },
        //загрузка аватара
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
        //получение списка столов
        getTables() {
            return request(API_BASE, '/api/tables', { auth: false });
        },
        //проверка доступности столов на дату время
        getAvailability(params) {
            const search = new URLSearchParams(params);
            return request(API_BASE, `/api/tables/availability?${search.toString()}`, {
                auth: false
            });
        },
        //создание нового бронирования
        createReservation(data) {
            return request(API_BASE, '/api/reservations', {
                method: 'POST',
                body: data
            });
        },
        //получение списка брони текущего пользователя
        getMyReservations() {
            return request(API_BASE, '/api/reservations/me');
        },
        //отмена брони по айди
        cancelReservation(id) {
            return request(API_BASE, `/api/reservations/${id}/cancel`, {
                method: 'PATCH'
            });
        },
        //отправка соо в поддержку
        sendSupport(data) {
            return request(API_BASE, '/api/support', {
                method: 'POST',
                body: data
            });
        },
        //получение данных для дашборда
        getDashboard() {
            return request(DASHBOARD_BASE, '/api/dashboard', { auth: false });
        }
    };
})();
