document.addEventListener('DOMContentLoaded', async () => {
//подкл апи
    const api = window.ScissorsApi;
//кэш ссылки на эл-ты, чтоб не искать их постоянно
    const featuresContainer = document.getElementById('features'); //контейнер для карточек команды
    const techContainer = document.getElementById('techStack'); //контейнер для тегов технологий
    const contactsContainer = document.getElementById('contacts'); //контейнер для контактной инфы
    const statusLine = document.getElementById('apiStatus');// строка статуса подкл
    const docsLink = document.getElementById('docsLink'); //ссылка на документацию апи
//резерв данные
//если апи недоступен используются эти данные чтоб страница не была пустой
    const fallbackData = {
        project_name: 'Scissors Bar',
        description: 'Бар с острыми впечатлениями. Смелые коктейли. Ночь в твоем вкусе.',
        //инфа о команде
        team: [
            {
                role: 'Backend',
                responsibility: 'FastAPI, авторизация, бронирование и интеграция с MySQL'
            },
            {
                role: 'Frontend',
                responsibility: 'HTML, CSS, JavaScript, формы и страницы проекта'
            },
            {
                role: 'Database',
                responsibility: 'SQL-скрипты, тестовые данные и структура базы'
            }
        ],
        //стек технологий проекта
        technologies: ['FastAPI', 'Flask', 'MySQL', 'HTML', 'CSS', 'JavaScript']
    };
//вспомогательные функции
    function setStatus(message, isError = false) {
        if (!statusLine) return;
        statusLine.textContent = message;
        //добавляем и удаляем класс ошибки в зависимости от флага
        statusLine.classList.toggle('error', isError);
    }

    function renderFeatures(team) {
        if (!featuresContainer) return;
        //для каждого эл-та команды создаем хтмл карточку
        featuresContainer.innerHTML = team.map((item) => `
            <article class="feature">
                <h3>${item.role}</h3>
                <p>${item.responsibility}</p>
            </article>
        `).join(''); //соединяем массив строк в один хтмл
    }

    function renderTech(technologies) {
        if (!techContainer) return;
        //каждый тех тег оборачиваем в спам с классом
        techContainer.innerHTML = technologies
            .map((item) => `<span class="tech-tag">${item}</span>`)
            .join('');
    }

    function renderContacts() {
        if (!contactsContainer) return;
        //берем базовый адрес апи из конфига или исп дефолд
        const apiBase = api && api.config ? api.config.apiBase : 'http://127.0.0.1:8000';

        contactsContainer.innerHTML = `
            <div class="contact-item">
                <i class="fas fa-server"></i>
                <span>FastAPI: ${apiBase}</span>
            </div>
            <div class="contact-item">
                <i class="fas fa-chart-line"></i>
                <span>Dashboard: http://127.0.0.1:5000/api/dashboard</span>
            </div>
            <div class="contact-item">
                <i class="fas fa-database"></i>
                <span>MySQL: база scissors_bar</span>
            </div>
        `;
    }

    function renderPage(data) {
        const payload = data || fallbackData;
        document.title = `О проекте - ${payload.project_name || 'Scissors Bar'}`;

        const description = document.getElementById('aboutDescription');
        if (description) {
            description.textContent = payload.description || fallbackData.description;
        }
//рендерим остальные секции
        renderFeatures(payload.team || fallbackData.team);
        renderTech(payload.technologies || fallbackData.technologies);
        renderContacts();
//обновляем ссылку на документацию апи
        if (docsLink && api && api.config) {
            docsLink.href = `${api.config.apiBase}/docs`;
        }
    }
//запуск
    renderPage(fallbackData);
    //показываем статус загрузка
    setStatus('Загружаем данные о проекте из FastAPI...');
//пытаемся получить актуальные данные от бэка
    try {
        const payload = await api.getAbout();
        //если успешно то перерисовываем стр с реальными данными
        renderPage(payload);
        setStatus('Страница подключена к backend и получает данные по API.');
    } catch (error) {
    //если ошибка показывает соо об ошибке
    //страницв остается с резерв данными
        setStatus(error.message || 'Backend недоступен. Показан резервный контент.', true);
    }
});
