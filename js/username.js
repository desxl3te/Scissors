
const API_BASE_URL = 'http://127.0.0.1:8000/api';
const SESSION_KEY = 'scissors_session';

// Токен хранится в общем для всего сайта ключе scissors_session ({ token, user }).
function getStoredToken() {
    try {
        const session = JSON.parse(localStorage.getItem(SESSION_KEY));
        return session && session.token ? session.token : null;
    } catch (error) {
        return null;
    }
}

function setStoredToken(token) {
    let session;
    try {
        session = JSON.parse(localStorage.getItem(SESSION_KEY)) || {};
    } catch (error) {
        session = {};
    }
    session.token = token;
    localStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

// Получаем имя пользователя из URL (?user=...)
const urlParams = new URLSearchParams(window.location.search);
const username = urlParams.get('user') || urlParams.get('name'); // поддерживаем оба варианта

// Загрузка данных пользователя
async function loadUserData() {
    if (!username) {
        document.getElementById('username').textContent = 'Не указан';
        document.getElementById('email').textContent = '—';
        document.getElementById('role').textContent = '—';
        document.getElementById('createdAt').textContent = '—';
        showMessage('Укажите пользователя: ?user=имя', 'error');
        return;
    }

    try {
        const res = await fetch(`${API_BASE_URL}/users/${username}`);

        if (!res.ok) {
            if (res.status === 404) throw new Error('Пользователь не найден');
            throw new Error('Ошибка загрузки');
        }

        const user = await res.json();

        // Заполняем поля профиля
        document.getElementById('username').textContent = user.user_name || username;
        document.getElementById('email').textContent = user.email || 'Не указан';
        document.getElementById('role').textContent = user.role || 'customer';
        document.getElementById('createdAt').textContent = user.created_at
            ? new Date(user.created_at).toLocaleDateString('ru-RU')
            : '—';

    } catch (error) {
        console.error('Ошибка загрузки:', error);
        document.getElementById('username').textContent = username;
        document.getElementById('email').textContent = 'Ошибка';
        document.getElementById('role').textContent = '—';
        document.getElementById('createdAt').textContent = '—';
        showMessage(error.message, 'error');
    }
}

// Показать текущий токен (если есть)
function displayCurrentToken() {
    const token = getStoredToken();
    const tokenBox = document.getElementById('token');

    if (token) {
        const shortToken = token.length > 50
            ? `${token.substring(0, 30)}...${token.substring(token.length - 20)}`
            : token;
        tokenBox.textContent = shortToken;
        tokenBox.style.color = '#4caf50';
    } else {
        tokenBox.textContent = 'Токен отсутствует. Войдите в аккаунт.';
        tokenBox.style.color = '#ff9dbf';
    }
}

// Обновление токена
async function refreshToken() {
    const oldToken = getStoredToken();

    if (!oldToken) {
        showMessage('Сначала войдите в аккаунт', 'error');
        return;
    }

    try {
        const res = await fetch(`${API_BASE_URL}/auth/refresh`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${oldToken}`,
                'Content-Type': 'application/json'
            }
        });

        if (!res.ok) {
            if (res.status === 401) throw new Error('Токен просрочен, войдите заново');
            throw new Error('Ошибка обновления');
        }

        const data = await res.json();
        setStoredToken(data.access_token);

        showMessage('✅ Токен успешно обновлён!', 'success');
        displayCurrentToken();

        setTimeout(() => {
            const msgEl = document.getElementById('message');
            msgEl.className = 'message';
        }, 3000);

    } catch (error) {
        console.error('Ошибка обновления:', error);
        showMessage(`❌ ${error.message}`, 'error');
    }
}

// Показ сообщений
function showMessage(text, type) {
    const messageEl = document.getElementById('message');
    messageEl.textContent = text;
    messageEl.className = `message ${type}`;
    messageEl.style.display = 'block';
}
 // === ИНИЦИАЛИЗАЦИЯ ===
document.addEventListener('DOMContentLoaded', () => {
    loadUserData();
    displayCurrentToken();

    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshToken);
    }
});