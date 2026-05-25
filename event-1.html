document.addEventListener('DOMContentLoaded', () => {
    const cardsContainer = document.getElementById('dashboardCards');
    const generatedAt = document.getElementById('dashboardGeneratedAt');
    const refreshButton = document.getElementById('refreshDashboardBtn');
    const statusLine = document.getElementById('dashboardStatus');
    const api = window.ScissorsApi;

    let statusChart = null;
    let weekdayChart = null;
    let tablesChart = null;

    function setStatus(message, isError = false) {
        if (!statusLine) return;
        statusLine.textContent = message;
        statusLine.classList.toggle('is-error', isError);
    }

    function drawChart(targetId, currentChart, config) {
        const canvas = document.getElementById(targetId);
        if (!canvas || typeof Chart === 'undefined') return currentChart;

        if (currentChart) currentChart.destroy();

        return new Chart(canvas, config);
    }

    async function loadDashboard() {
        setStatus('Загружаем дашборд...');

        try {
            const payload = await api.getDashboard();

            if (cardsContainer) {
                cardsContainer.innerHTML = payload.cards.map((item) => `
                    <article class="dashboard-card">
                        <span>${item.label}</span>
                        <strong>${item.value}</strong>
                    </article>
                `).join('');
            }

            if (generatedAt) {
                generatedAt.textContent = `Обновлено: ${payload.generated_at}`;
            }

            statusChart = drawChart('reservationStatusChart', statusChart, {
                type: 'doughnut',
                data: {
                    labels: payload.charts.reservation_status.labels,
                    datasets: [{
                        data: payload.charts.reservation_status.data,
                        backgroundColor: ['#ff69b4', '#ffb6c1', '#f5f5f5']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            labels: { color: '#f5f5f5' }
                        }
                    }
                }
            });

            weekdayChart = drawChart('weekdayLoadChart', weekdayChart, {
                type: 'bar',
                data: {
                    labels: payload.charts.weekday_load.labels,
                    datasets: [{
                        label: 'Брони',
                        data: payload.charts.weekday_load.data,
                        backgroundColor: '#ff69b4'
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: { ticks: { color: '#f5f5f5' } },
                        y: { ticks: { color: '#f5f5f5' }, beginAtZero: true }
                    },
                    plugins: {
                        legend: {
                            labels: { color: '#f5f5f5' }
                        }
                    }
                }
            });

            tablesChart = drawChart('popularTablesChart', tablesChart, {
                type: 'line',
                data: {
                    labels: payload.charts.popular_tables.labels,
                    datasets: [{
                        label: 'Количество броней',
                        data: payload.charts.popular_tables.data,
                        borderColor: '#ff69b4',
                        backgroundColor: 'rgba(255, 105, 180, 0.2)',
                        tension: 0.3,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: { ticks: { color: '#f5f5f5' } },
                        y: { ticks: { color: '#f5f5f5' }, beginAtZero: true }
                    },
                    plugins: {
                        legend: {
                            labels: { color: '#f5f5f5' }
                        }
                    }
                }
            });

            setStatus(`Подтвержденных броней: ${payload.summary.confirmed_reservations}`);
        } catch (error) {
            setStatus(error.message || 'Не удалось загрузить дашборд.', true);
        }
    }

    if (refreshButton) {
        refreshButton.addEventListener('click', loadDashboard);
    }

    loadDashboard();
});
