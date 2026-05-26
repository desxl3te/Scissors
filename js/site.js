//загрузка хтмл
document.addEventListener('DOMContentLoaded', () => {
    // api
    const api = window.ScissorsApi;
    const session = api.getSession();
    //бургер кнопка
    const burgerBtn = document.getElementById('burgerBtn');
    const sidePanel = document.getElementById('sidePanel');
    const overlay = document.getElementById('overlay');
    const closeBtn = document.getElementById('closeBtn');
    const panelLinks = document.querySelectorAll('.side-panel a'); //ссылки в меню
    //окно авторизации
    const authModal = document.getElementById('authModal');
    const closeModalBtn = document.querySelector('.close-modal');
    const tabBtns = document.querySelectorAll('.tab-btn'); //кнопки вкладок
    const tabContents = document.querySelectorAll('.tab-content'); //содержание
    //акк пользователя
    const userAccountBtn = document.getElementById('userAccountBtn');
    const userDropdownMenu = document.getElementById('userDropdownMenu');
    const loggedOutView = document.getElementById('loggedOutView'); //вид для неавторизованных
    const loggedInView = document.getElementById('loggedInView'); //вид для авторизованных
    const userNameDisplay = document.getElementById('userNameDisplay'); //name
    const userAvatarWrapper = document.getElementById('userAvatarWrapper'); //avatar
    //формы
    const loginForm = document.getElementById('loginForm'); //вход
    const registerForm = document.getElementById('registerForm'); //регистрация
    const editProfileForm = document.getElementById('editProfileForm'); //редактирование профиля
    const supportForm = document.getElementById('supportForm'); //поддержка
    //кнопки переключения вкладок
    const switchToRegister = document.getElementById('switchToRegister'); //ссылка зарегаться
    const switchToLogin = document.getElementById('switchToLogin'); //ссылка войти
    const logoutBtn = document.getElementById('logoutBtn'); //ссылка выход
    const editProfileLink = document.getElementById('editProfileLink');//ссылка редактировать
    const supportLink = document.getElementById('supportLink'); //ссылка поддержка
    //поля редакт профиля
    const editNameInput = document.getElementById('editName');
    const editPhoneInput = document.getElementById('editPhone');
    const editAvatarInput = document.getElementById('editAvatar');
    //окно спасибо
    const thankYouModal = document.getElementById('thankYouModal');
    const thankYouOkBtn = document.getElementById('thankYouOkBtn');
    //форма бронирования
    const bookingForm = document.getElementById('bookingForm');
    const reservationDateTime = document.getElementById('reservationDateTime'); //дата и время
    const reservationGuests = document.getElementById('reservationGuests'); //скок гостей
    const reservationDuration = document.getElementById('reservationDuration'); //длительность
    const tableSelect = document.getElementById('tableSelect'); //выбор столика
    const specialRequest = document.getElementById('specialRequest'); //пожелания
    const bookingStatus = document.getElementById('bookingStatus'); //статус-соо
    const reservationList = document.getElementById('reservationList'); //список броней
    const refreshReservationsBtn = document.getElementById('refreshReservationsBtn'); //кнопка обновления
    //переключение бокового меню
    function toggleMenu() {
        if (!burgerBtn || !sidePanel || !overlay) return;

        burgerBtn.classList.toggle('active');
        sidePanel.classList.toggle('active');
        overlay.classList.toggle('active');
        document.body.style.overflow = sidePanel.classList.contains('active') ? 'hidden' : '';
    }
    //переключение вкладок в модалке
    function activateTab(tabName) {
        const authTabsRow = document.querySelector('.auth-tabs');
        const isAuthTab = tabName === 'login' || tabName === 'register';

        if (authTabsRow) authTabsRow.style.display = isAuthTab ? 'flex' : 'none';

        tabBtns.forEach((btn) => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });

        tabContents.forEach((content) => {
            content.classList.toggle('active', content.id === `${tabName}Tab`);
        });
    }
    //открытие модалки
    function openAuthModal(tabName = 'login') {
        if (!authModal) return;
        authModal.style.display = 'block';
        document.body.style.overflow = 'hidden';
        // если откр вкл поддержка и пользовтель зашел в профиль то подставляем его данные
        if (tabName === 'support' && supportForm && isLoggedIn()) {
            const user = currentUser();
            const nameInput = supportForm.querySelector('#supportName');
            const emailInput = supportForm.querySelector('#supportEmail');

            if (nameInput && !nameInput.value) nameInput.value = user.user_name || '';
            if (emailInput && !emailInput.value) emailInput.value = user.email || '';
        }

        activateTab(tabName);
    }
    //закрытие модалки
    function closeAuthModal() {
        if (!authModal) return;
        authModal.style.display = 'none';
        document.body.style.overflow = '';
    }
    //получение текущего пользователя
    function currentUser() {
        return session.user || null;
    }
    //авторизован ли пользователь?
    function isLoggedIn() {
        return Boolean(session.token && session.user);
    }
    //сохранение данных (после входа/регистрации)
    function persistSession(payload) {
        session.token = payload.access_token;
        session.user = payload.user;
        api.saveSession({ token: session.token, user: session.user });
        renderUserState();
    }
    //очистка при выходе
    function clearSession() {
        session.token = null;
        session.user = null;
        api.clearSession();
        renderUserState();
        renderReservations([]);
    }
    //показ соо под формами
    function setFormMessage(target, message, isError = false) {
        if (!target) return;
        target.textContent = message || '';
        target.classList.toggle('is-error', isError); //если ошибка красный
        target.classList.toggle('is-success', Boolean(message) && !isError); //зеленый если все заебись
    }
    //создание и получение эл-та для статуса
    function upsertFormStatus(form) {
        if (!form) return null;

        let status = form.querySelector('.form-status');
        if (!status) {
            status = document.createElement('p');
            status.className = 'form-status';
            form.appendChild(status);
        }
        return status;
    }
    //блокировка кнопки
    function setSubmitState(form, busy, text) {
        if (!form) return;
        const submitButton = form.querySelector('button[type="submit"]');
        if (!submitButton) return;

        if (!submitButton.dataset.defaultText) {
            submitButton.dataset.defaultText = submitButton.textContent;
        }

        submitButton.disabled = busy; //блок и разблок
        submitButton.textContent = busy ? text : submitButton.dataset.defaultText;
    }
    //обнова интерфейса после входв/выхода
    function renderUserState() {
        const user = currentUser();
        //скрытие блока вход и профиль
        if (loggedOutView) {
            loggedOutView.style.display = user ? 'none' : 'block';
        }

        if (loggedInView) {
            loggedInView.style.display = user ? 'block' : 'none';
        }
        //обновляем им в меню
        if (userNameDisplay) {
            userNameDisplay.textContent = user ? user.user_name : 'Гость Бара';
        }
        //обновляем аву
        if (userAvatarWrapper) {
            let avatarUrl = user && user.avatar ? user.avatar : '';
            if (avatarUrl && !/^https?:\/\//i.test(avatarUrl)) {
                avatarUrl = api.config.apiBase + avatarUrl;
            }
            if (avatarUrl) {
                userAvatarWrapper.innerHTML =
                    '<img src="' + avatarUrl + '" alt="avatar" ' +
                    'style="width:100%;height:100%;object-fit:cover;border-radius:50%;display:block;">';
            } else {
                userAvatarWrapper.innerHTML = '<i class="fas fa-user user-avatar-icon"></i>';
            }
        }

        if (editNameInput) {
            editNameInput.value = user ? user.user_name : '';
        }

        if (editPhoneInput) {
            const hint = editPhoneInput.parentElement ? editPhoneInput.parentElement.querySelector('.form-hint') : null;
            editPhoneInput.value = user && user.phone ? user.phone : '';
            if (hint) hint.textContent = 'Номер для связи по бронированию.';
        }
    }
    //синхронизация профиля с сервером
    async function syncProfile() {
        if (!isLoggedIn()) return;

        try {
            const response = await api.getProfile();
            session.user = response.result;
            api.saveSession({ token: session.token, user: session.user });
            renderUserState();
        } catch (error) {
            clearSession();
        }
    }
    //загрузка доступных столиков
    async function loadAvailability() {
        if (!bookingForm || !reservationDateTime || !reservationGuests || !reservationDuration || !tableSelect) {
            return;
        }

        const dateValue = reservationDateTime.value;
        if (!dateValue) {
            tableSelect.innerHTML = '<option value="">Сначала выбери дату и время</option>';
            return;
        }

        setFormMessage(bookingStatus, 'Проверяем свободные столики...');

        try {
            const response = await api.getAvailability({
                reservation_time: dateValue,
                guests_count: reservationGuests.value,
                duration_hours: reservationDuration.value
            });
            //фильтруем ток свободные столики
            const availableTables = response.data.filter((item) => item.is_available);
            if (!availableTables.length) {
                tableSelect.innerHTML = '<option value="">Свободных столиков нет</option>';
                setFormMessage(bookingStatus, 'На выбранное время свободных столиков нет.', true);
                return;
            }

            tableSelect.innerHTML = availableTables
                .map((item) => (
                    `<option value="${item.id}">Столик ${item.table_number} · ${item.seats_count} мест</option>`
                ))
                .join('');

            setFormMessage(bookingStatus, `Найдено столиков: ${availableTables.length}`);
        } catch (error) {
            tableSelect.innerHTML = '<option value="">Не удалось получить список</option>';
            setFormMessage(bookingStatus, error.message || 'Не удалось проверить доступность.', true);
        }
    }
    //отображение списка броней
    function renderReservations(items) {
        if (!reservationList) return;

        if (!isLoggedIn()) {
            reservationList.innerHTML = '<p class="reservation-empty">Войди в аккаунт, чтобы видеть свои брони.</p>';
            return;
        }

        if (!items.length) {
            reservationList.innerHTML = '<p class="reservation-empty">Броней пока нет.</p>';
            return;
        }

        reservationList.innerHTML = items.map((item) => `
            <article class="reservation-card">
                <div>
                    <h4>Столик ${item.table_number}</h4>
                    <p>${item.reservation_time}</p>
                    <p>${item.guests_count} гостей · ${item.duration_hours} ч.</p>
                    <p>Статус: ${item.status}</p>
                </div>
                <button class="btn btn-small reservation-cancel" data-id="${item.id}" ${item.status === 'cancelled' ? 'disabled' : ''}>
                    ${item.status === 'cancelled' ? 'Отменено' : 'Отменить'}
                </button>
            </article>
        `).join('');
    }
    //загрузка броней с сервера
    async function loadReservations() {
        if (!reservationList) return;
        if (!isLoggedIn()) {
            renderReservations([]);
            return;
        }

        reservationList.innerHTML = '<p class="reservation-empty">Загружаем брони...</p>';

        try {
            const response = await api.getMyReservations();
            renderReservations(response.data);
        } catch (error) {
            reservationList.innerHTML = `<p class="reservation-empty">${error.message}</p>`;
        }
    }
    //обработка отмены брони
    async function handleReservationCancel(event) {
        const button = event.target.closest('.reservation-cancel');
        if (!button) return;

        try {
            await api.cancelReservation(button.dataset.id);
            await loadReservations();
            setFormMessage(bookingStatus, 'Бронь отменена.');
        } catch (error) {
            setFormMessage(bookingStatus, error.message || 'Не удалось отменить бронь.', true);
        }
    }
    //инициализация блесток
    function initHeroSparkles() {
        const container = document.getElementById('sparkles-container');
        if (!container || typeof anime === 'undefined') return;

        const logo = document.querySelector('.hero h1');
        const isFullscreen = !logo;

        function createSparkle() {
            const sparkle = document.createElement('div');
            sparkle.className = 'sparkle';

            const containerRect = container.getBoundingClientRect();

            if (logo) {
                const logoRect = logo.getBoundingClientRect();
                const offsetX = (Math.random() - 0.5) * logoRect.width * 1.4;
                const offsetY = (Math.random() - 0.5) * logoRect.height * 1.4;
                sparkle.style.left = `${logoRect.left - containerRect.left + logoRect.width / 2 + offsetX}px`;
                sparkle.style.top = `${logoRect.top - containerRect.top + logoRect.height / 2 + offsetY}px`;
            } else {
                sparkle.style.left = `${Math.random() * containerRect.width}px`;
                sparkle.style.top = `${Math.random() * containerRect.height}px`;
            }
            //размер
            const size = 4 + Math.random() * 7;
            sparkle.style.width = `${size}px`;
            sparkle.style.height = `${size}px`;
            container.appendChild(sparkle);
            //анимация появления
            anime({
                targets: sparkle,
                opacity: [{ value: 0, duration: 250 }, { value: 1, duration: 700 }, { value: 0, duration: 450 }],
                scale: [{ value: 0.5, duration: 250 }, { value: 1.15, duration: 700 }, { value: 0.6, duration: 450 }],
                easing: 'easeInOutSine',
                complete: () => sparkle.remove()
            });
        }
        //настройка частоты
        const burst = isFullscreen ? 4 : 1;
        const intervalMs = isFullscreen ? 400 : 500;

        for (let i = 0; i < (isFullscreen ? 16 : 1); i += 1) createSparkle();

        const sparkleInterval = setInterval(() => {
            for (let i = 0; i < burst; i += 1) createSparkle();
        }, intervalMs);

        document.addEventListener('visibilitychange', () => {
            if (document.hidden) clearInterval(sparkleInterval);
        });
    }
    //бургер клик
    if (burgerBtn) burgerBtn.addEventListener('click', toggleMenu); //открыть меню
    if (overlay) overlay.addEventListener('click', toggleMenu); //закрыть по клику меню
    if (closeBtn) closeBtn.addEventListener('click', toggleMenu); //закрыть по крестику
    panelLinks.forEach((link) => link.addEventListener('click', () => { //закрыть после выбора пункт
        if (sidePanel && sidePanel.classList.contains('active')) toggleMenu();
    }));
    //плавный скрол по якорям
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
        const targetSelector = anchor.getAttribute('href');
        if (!targetSelector || targetSelector === '#') return;

        anchor.addEventListener('click', (event) => {
            const target = document.querySelector(targetSelector);
            if (!target) return;
            event.preventDefault();
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
    });
    //выпадающее меню акк
    if (userAccountBtn) {
        userAccountBtn.addEventListener('click', (event) => {
            event.stopPropagation();
            if (!isLoggedIn()) {
                openAuthModal('login');
                return;
            }
            if (userDropdownMenu) {
                userDropdownMenu.classList.toggle('active');
            }
        });
    }
    //клик по войти рег
    if (document.querySelector('#loggedOutView .dropdown-link')) {
        document.querySelector('#loggedOutView .dropdown-link').addEventListener('click', (event) => {
            event.preventDefault();
            openAuthModal('login');
        });
    }
    //закрытие меню при клике
    document.addEventListener('click', (event) => {
        if (!userDropdownMenu || !userAccountBtn) return;
        if (!userDropdownMenu.contains(event.target) && !userAccountBtn.contains(event.target)) {
            userDropdownMenu.classList.remove('active');
        }
    });
    //модалка закрытие
    if (closeModalBtn) closeModalBtn.addEventListener('click', closeAuthModal); //по крестику
    window.addEventListener('click', (event) => {
        if (event.target === authModal) closeAuthModal(); //по клику на фон
        if (event.target === thankYouModal) thankYouModal.style.display = 'none'; //окно спасибр
    });

    tabBtns.forEach((btn) => {
        btn.addEventListener('click', () => activateTab(btn.dataset.tab));
    });

    if (switchToRegister) {
        switchToRegister.addEventListener('click', (event) => {
            event.preventDefault();
            activateTab('register');
        });
    }

    if (switchToLogin) {
        switchToLogin.addEventListener('click', (event) => {
            event.preventDefault();
            activateTab('login');
        });
    }

    if (editProfileLink) {
        editProfileLink.addEventListener('click', (event) => {
            event.preventDefault();
            openAuthModal('editProfile');
        });
    }

    if (supportLink) {
        supportLink.addEventListener('click', (event) => {
            event.preventDefault();
            openAuthModal('support');
        });
    }
    //кнопка ок спс
    if (thankYouOkBtn) {
        thankYouOkBtn.addEventListener('click', () => {
            if (thankYouModal) thankYouModal.style.display = 'none';
        });
    }
    //форма входа
    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const status = upsertFormStatus(loginForm);
            setSubmitState(loginForm, true, 'Входим...');
            setFormMessage(status, '');

            try {
                const payload = await api.login({
                    email: loginForm.querySelector('#email').value.trim(),
                    password: loginForm.querySelector('#password').value
                });
                persistSession(payload);
                await loadReservations();
                closeAuthModal();
            } catch (error) {
                setFormMessage(status, error.message || 'Не удалось войти.', true);
            } finally {
                setSubmitState(loginForm, false);
            }
        });
    }
    //форма регистрации
    if (registerForm) {
        registerForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const status = upsertFormStatus(registerForm);
            const password = registerForm.querySelector('#regPassword').value;
            const confirmPassword = registerForm.querySelector('#regConfirmPassword').value;
            //совпадают ли пароли
            if (password !== confirmPassword) {
                setFormMessage(status, 'Пароли не совпадают.', true);
                return;
            }

            setSubmitState(registerForm, true, 'Создаем аккаунт...');
            setFormMessage(status, '');

            try {
                const payload = await api.register({
                    user_name: registerForm.querySelector('#regName').value.trim(),
                    email: registerForm.querySelector('#regEmail').value.trim(),
                    password
                });
                persistSession(payload);
                await loadReservations();
                closeAuthModal();
            } catch (error) {
                setFormMessage(status, error.message || 'Не удалось зарегистрироваться.', true);
            } finally {
                setSubmitState(registerForm, false);
            }
        });
    }
    //редактирование профиля
    if (editProfileForm) {
        editProfileForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            if (!isLoggedIn()) {
                openAuthModal('login');
                return;
            }

            const status = upsertFormStatus(editProfileForm);
            setSubmitState(editProfileForm, true, 'Сохраняем...');
            setFormMessage(status, '');

            try {
                const payload = await api.updateProfile({
                    user_name: editNameInput ? editNameInput.value.trim() : undefined,
                    phone: editPhoneInput ? editPhoneInput.value.trim() : undefined
                });
                session.user = payload.result;

                const avatarFile = editAvatarInput && editAvatarInput.files
                    ? editAvatarInput.files[0]
                    : null;
                if (avatarFile) {
                    const avatarPayload = await api.uploadAvatar(avatarFile);
                    session.user = avatarPayload.result;
                    if (editAvatarInput) editAvatarInput.value = '';
                }

                api.saveSession({ token: session.token, user: session.user });
                renderUserState();
                setFormMessage(status, 'Профиль обновлен.');
            } catch (error) {
                setFormMessage(status, error.message || 'Не удалось обновить профиль.', true);
            } finally {
                setSubmitState(editProfileForm, false);
            }
        });
    }
    //поддержка
    if (supportForm) {
        supportForm.removeAttribute('action');
        supportForm.removeAttribute('method');

        supportForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const status = upsertFormStatus(supportForm);
            setSubmitState(supportForm, true, 'Отправляем...');
            setFormMessage(status, '');

            try {
                await api.sendSupport({
                    name: supportForm.querySelector('#supportName').value.trim(),
                    email: supportForm.querySelector('#supportEmail').value.trim(),
                    message: supportForm.querySelector('#supportMessage').value.trim()
                });
                supportForm.reset();
                closeAuthModal();
                if (thankYouModal) thankYouModal.style.display = 'block';
            } catch (error) {
                setFormMessage(status, error.message || 'Не удалось отправить сообщение.', true);
            } finally {
                setSubmitState(supportForm, false);
            }
        });
    }
    //выход
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (event) => {
            event.preventDefault();
            clearSession();
            closeAuthModal();
        });
    }
    //форма брони
    if (bookingForm) {
        if (reservationDateTime) {
            const now = new Date();
            now.setMinutes(now.getMinutes() - now.getTimezoneOffset() + 30);
            reservationDateTime.min = now.toISOString().slice(0, 16);
        }

        [reservationDateTime, reservationGuests, reservationDuration].forEach((input) => {
            if (input) input.addEventListener('change', loadAvailability);
        });

        bookingForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            if (!isLoggedIn()) {
                setFormMessage(bookingStatus, 'Сначала войди в аккаунт.', true);
                openAuthModal('login');
                return;
            }

            if (!tableSelect.value) {
                setFormMessage(bookingStatus, 'Сначала выбери свободный столик.', true);
                return;
            }

            setFormMessage(bookingStatus, '');
            setSubmitState(bookingForm, true, 'Бронируем...');

            try {
                const payload = await api.createReservation({
                    table_id: Number(tableSelect.value),
                    reservation_time: reservationDateTime.value,
                    duration_hours: Number(reservationDuration.value),
                    guests_count: Number(reservationGuests.value),
                    special_request: specialRequest.value.trim() || null
                });
                specialRequest.value = '';
                await loadAvailability();
                await loadReservations();
                setFormMessage(
                    bookingStatus,
                    `Готово. Забронирован столик ${payload.result.table_number} на ${payload.result.reservation_time}.`
                );
            } catch (error) {
                setFormMessage(bookingStatus, error.message || 'Не удалось создать бронь.', true);
            } finally {
                setSubmitState(bookingForm, false);
            }
        });
    }
//обновление броней
    if (refreshReservationsBtn) {
        refreshReservationsBtn.addEventListener('click', loadReservations);
    }
//отмена
    if (reservationList) {
        reservationList.addEventListener('click', handleReservationCancel);
    }

    renderUserState();
    loadReservations();
    initHeroSparkles();
});
