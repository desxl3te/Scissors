// конфиг и константы
const API_BASE_URL = 'http://127.0.0.1:8000/api';

// ключ, под которым мы сохраняем данные в браузере
const SESSION_KEY = 'scissors_session';

// работа с токеном
function getStoredToken() {
    try {
        // пытаемся достать строку из localStorage и превратить её в объект
        const session = JSON.parse(localStorage.getItem(SESSION_KEY));
        // если объект есть и в нём есть токен — возвращаем его
        return session && session.token ? session.token : null;
    } catch (error) {
        // если данные сдохли, просто возвращаем null
        return null;
    }
}

function setStoredToken(token) {
    let session;
    try {
        session = JSON.parse(localStorage.getItem(SESSION_KEY)) || {};
    } catch (error) {
        // если ошибка чтения то пустой объект
        session = {};
    }
    // обновляем token
    session.token = token;
    // сохраняем объект обратно в localStorage (превращая в строку)
    localStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

// подготовка данных

// получаем параметры из адресной строки
const urlParams = new URLSearchParams(window.location.search);

const username = urlParams.get('user') || urlParams.get('name');

// обновление интерфейса
function fillProfile(user) {
    document.getElementById('username').textContent = user.user_name || 'Не указан';
    document.getElementById('email').textContent = user.email || 'Не указан';
    document.getElementById('role').textContent = user.role || 'customer';

    // форматируем дату создания
    document.getElementById('createdAt').textContent = user.created_at
        ? new Date(user.created_at).toLocaleDateString('ru-RU')
        : '—';
}


function clearProfile() {
    document.getElementById('username').textContent = 'Не указан';
    document.getElementById('email').textContent = '—';
    document.getElementById('role').textContent = '—';
    document.getElementById('createdAt').textContent = '—';
}

// загрузка данных пользователя
async function loadUserData() {
    // если в ссылке есть имя пользователя
    if (username) {
        try {
            // делаем запрос на получение публичного профиля
            const res = await fetch(`${API_BASE_URL}/users/${encodeURIComponent(username)}`);

            // проверяем статус ответа
            if (!res.ok) {
                if (res.status === 404) throw new Error('Пользователь не найден');
                throw new Error('Ошибка загрузки');
            }
            // если всё ок, заполняем профиль данными
            fillProfile(await res.json());
        } catch (error) {
            console.error('Ошибка загрузки:', error);
            clearProfile();
            // показываем имя из ссылки, но помечаем ошибку
            document.getElementById('username').textContent = username;
            document.getElementById('email').textContent = 'Ошибка';
            showMessage(error.message, 'error');
        }
        return;
    }

    // если имени в ссылке нет, пробуем загрузить свой профиль по токену
    const token = getStoredToken();

    // если токена нет — пользователь не авторизован
    if (!token) {
        clearProfile();
        showMessage('Войдите в аккаунт, чтобы увидеть профиль.', 'error');
        return;
    }

    try {
        // Запрашиваем данные "о себе" с заголовком авторизации
        const res = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!res.ok) {
            if (res.status === 401) throw new Error('Токен просрочен, войдите заново');
            throw new Error('Ошибка загрузки профиля');
        }

        const data = await res.json();
        fillProfile(data.result || data);
    } catch (error) {
        console.error('Ошибка загрузки:', error);
        clearProfile();
        document.getElementById('email').textContent = 'Ошибка';
        showMessage(error.message, 'error');
    }
}

// отображение токена
function displayCurrentToken() {
    const token = getStoredToken();
    const tokenBox = document.getElementById('token');

    if (token) {
        const shortToken = token.length > 50
            ? `${token.substring(0, 30)}...${token.substring(token.length - 20)}`
            : token;
        tokenBox.textContent = shortToken;
        tokenBox.style.color = '#4caf50'; // зеленый цвет
    } else {
        tokenBox.textContent = 'Токен отсутствует. Войдите в аккаунт.';
        tokenBox.style.color = '#ff9dbf'; // розовый цвет
    }
}

// обновление токена

async function refreshToken() {
    const oldToken = getStoredToken();

    if (!oldToken) {
        showMessage('Сначала войдите в аккаунт', 'error');
        return;
    }

    try {
        // Отправляем запрос на обновление токена
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
        displayCurrentToken(); // обновляем отображение токена на странице

        setTimeout(() => {
            const msgEl = document.getElementById('message');
            msgEl.className = 'message';
        }, 3000);

    } catch (error) {
        console.error('Ошибка обновления:', error);
        showMessage(`❌ ${error.message}`, 'error');
    }
}

// система увед
function showMessage(text, type) {
    const messageEl = document.getElementById('message');
    messageEl.textContent = text;
    messageEl.className = `message ${type}`;
    messageEl.style.display = 'block';
}
// запуск после загрузки страницы
document.addEventListener('DOMContentLoaded', () => {
    loadUserData();
    // инфа о токине
    displayCurrentToken();

    //  обработчик клика на кнопку обновления токена
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshToken);
    }
});