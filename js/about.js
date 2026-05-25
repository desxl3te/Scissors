document.addEventListener('DOMContentLoaded', async () => {
    const api = window.ScissorsApi;
    const featuresContainer = document.getElementById('features');
    const techContainer = document.getElementById('techStack');
    const contactsContainer = document.getElementById('contacts');
    const statusLine = document.getElementById('apiStatus');
    const docsLink = document.getElementById('docsLink');

    const fallbackData = {
        project_name: 'Scissors Bar',
        description: 'Бар с острыми впечатлениями. Смелые коктейли. Ночь в твоем вкусе.',
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
        technologies: ['FastAPI', 'Flask', 'MySQL', 'HTML', 'CSS', 'JavaScript']
    };

    function setStatus(message, isError = false) {
        if (!statusLine) return;
        statusLine.textContent = message;
        statusLine.classList.toggle('error', isError);
    }

    function renderFeatures(team) {
        if (!featuresContainer) return;
        featuresContainer.innerHTML = team.map((item) => `
            <article class="feature">
                <h3>${item.role}</h3>
                <p>${item.responsibility}</p>
            </article>
        `).join('');
    }

    function renderTech(technologies) {
        if (!techContainer) return;
        techContainer.innerHTML = technologies
            .map((item) => `<span class="tech-tag">${item}</span>`)
            .join('');
    }

    function renderContacts() {
        if (!contactsContainer) return;
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

        renderFeatures(payload.team || fallbackData.team);
        renderTech(payload.technologies || fallbackData.technologies);
        renderContacts();

        if (docsLink && api && api.config) {
            docsLink.href = `${api.config.apiBase}/docs`;
        }
    }

    renderPage(fallbackData);
    setStatus('Загружаем данные о проекте из FastAPI...');

    try {
        const payload = await api.getAbout();
        renderPage(payload);
        setStatus('Страница подключена к backend и получает данные по API.');
    } catch (error) {
        setStatus(error.message || 'Backend недоступен. Показан резервный контент.', true);
    }
});
