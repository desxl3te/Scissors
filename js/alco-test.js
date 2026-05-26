document.addEventListener('DOMContentLoaded', () => {
    //вопросы
    const questions = [
        { q: 'Сколько пальцев на одной руке?', a: ['5', '6', '4'], correct: 0 },
        { q: 'Какой цвет у травы летом?', a: ['Синий', 'Зеленый', 'Красный'], correct: 1 },
        { q: 'Что тяжелее: килограмм ваты или килограмм железа?', a: ['Железо', 'Вата', 'Одинаково'], correct: 2 },
        { q: 'Столица России?', a: ['Санкт-Петербург', 'Казань', 'Москва'], correct: 2 },
        { q: 'Сколько будет 2 + 2 * 2?', a: ['8', '6', '4'], correct: 1 },
        { q: 'Как называется животное, которое дает молоко?', a: ['Корова', 'Волк', 'Лиса'], correct: 0 },
        { q: 'Что идет, когда дождь, а мы мокнем?', a: ['Зонт', 'Небо', 'Вода'], correct: 2 },
        { q: 'Сколько дней в неделе?', a: ['5', '7', '10'], correct: 1 },
        { q: 'Какой газ мы вдыхаем?', a: ['Кислород', 'Углекислый газ', 'Гелий'], correct: 0 },
        { q: 'Что находится между небом и землей?', a: ['Облака', 'И', 'Птицы'], correct: 1 },
        { q: 'Сколько ног у паука?', a: ['6', '8', '4'], correct: 1 },
        { q: 'Какой месяц идет после января?', a: ['Декабрь', 'Май', 'Февраль'], correct: 2 },
        { q: 'Сколько часов в сутках?', a: ['12', '24', '48'], correct: 1 },
        { q: 'Какой цвет у снега?', a: ['Белый', 'Черный', 'Синий'], correct: 0 },
        { q: 'Сколько будет 10 − 5?', a: ['3', '67', '5'], correct: 2 },
        { q: 'Какое время года идет после зимы?', a: ['Лето', 'Осень', 'Весна'], correct: 2 },
        { q: 'Сколько углов у квадрата?', a: ['4', '9', '5'], correct: 0 },
        { q: 'Какой напиток делают из винограда?', a: ['Чай', 'Вино', 'Кофе'], correct: 1 },
        { q: 'Сколько будет 3 × 3?', a: ['6', '14', '9'], correct: 2 },
        { q: 'Как называется планета, на которой мы живём?', a: ['Марс', 'Земля', 'Венера'], correct: 1 },
        { q: 'Сколько будет 5 + 5?', a: ['8', '10', '12'], correct: 1 },
        { q: 'Какой день идет после понедельника?', a: ['Воскресенье', 'Среда', 'Вторник'], correct: 2 },
        { q: 'Сколько лап у кошки?', a: ['2', '4', '6'], correct: 1 },
        { q: 'Что светит ночью на небе?', a: ['Солнце', 'Луна', 'Облако'], correct: 1 },
        { q: 'Сколько будет 20 : 2?', a: ['5', '10', '15'], correct: 1 },
        { q: 'Какой цвет у лимона?', a: ['Красный', 'Желтый', 'Зеленый'], correct: 1 },
        { q: 'Сколько месяцев в году?', a: ['10', '12', '14'], correct: 1 },
        { q: 'Что плавает в воде?', a: ['Камень', 'Дерево', 'Железо'], correct: 1 },
        { q: 'Сколько будет 7 − 3?', a: ['2', '4', '5'], correct: 1 },
        { q: 'Какой праздник отмечают 31 декабря?', a: ['День рождения', 'Новый год', '8 марта'], correct: 1 },
        { q: 'Что пьет корова?', a: ['Ягермейстер', 'Молоко', 'Вода'], correct: 2 }
    ];

    const startBtn = document.getElementById('startTestBtn'); //начать тест
    const startScreen = document.getElementById('start-screen'); //экран привет
    const quizContainer = document.getElementById('quiz-container'); //контейнер вопросов
    const questionText = document.getElementById('question-text');// текст текущего вопроса
    const optionsContainer = document.getElementById('options-container'); // контейнер для кнопок ответов
    const resultBox = document.getElementById('resultBox'); //блок с резами
    const resultTitle = document.getElementById('resultTitle'); //заголовок реза
    const resultText = document.getElementById('resultText'); // текст реза
    const winnerCoupon = document.getElementById('winnerCoupon'); //блок с промиком
//состояние теста
    let score = 0; //колво правильных ответов
    let currentIndex = 0; //индекс вопроса в массиве
    let currentQuestions = []; //массив из 10 случайных вопро
//вспомогательные функции
    function shuffle(items) {
        const array = [...items]; //создаем копию, чтоб не менять ориг
        for (let index = array.length - 1; index > 0; index -= 1) {
        //выбираем случайный индекс от 0 дл текущего
            const randomIndex = Math.floor(Math.random() * (index + 1));
            //меняем элементы местаи
            [array[index], array[randomIndex]] = [array[randomIndex], array[index]];
        }
        return array;
    }

    function showQuestion() {
    //если вопросы закончились завершаем тест
        if (currentIndex >= currentQuestions.length) {
            finishQuiz();
            return;
        }
// берем текущий вопр из массива
        const item = currentQuestions[currentIndex];
        // обновляем текст вопр
        questionText.textContent = `${currentIndex + 1}. ${item.q}`;
        // очищаем контейнер от ответов от предыдущего вопр
        optionsContainer.innerHTML = '';
//создаем кнопку для каждого варика ответа
        item.a.forEach((answer, answerIndex) => {
            const button = document.createElement('button');
            button.className = 'option-btn'; //класс длля стилизации
            button.textContent = answer; //текст кнопки
            // обработчик клика
            button.addEventListener('click', () => {
            //если индекс совпадает с правильным - увеличим счет
                if (answerIndex === item.correct) score += 1;
                //переход к след вопр
                currentIndex += 1;
                showQuestion();
            });
            optionsContainer.appendChild(button);
        });
    }
//завершаем тест и показываем рез
    function finishQuiz() {
    //скрываем блок с вопр, показываем рез
        quizContainer.style.display = 'none';
        resultBox.style.display = 'block';
        //показываем сколько правильных ответов
        resultText.textContent = `Правильных ответов: ${score} из ${currentQuestions.length}`;
//если 9+ правильных ответов то трезвый
        if (score >= 9) {
            resultTitle.textContent = '🎉 АБСОЛЮТНО ТРЕЗВ!';
            resultTitle.style.color = '#ff69b4';
            winnerCoupon.style.display = 'block'; //промик
            return;
        }
//еслм меньше 9 то пьянь ебанная
        resultTitle.textContent = '🍺 ЕСТЬ ПРИЗНАКИ ОПЬЯНЕНИЯ...';
        resultTitle.style.color = '#aaa';
        resultText.innerHTML += '<br>Упс! Твоя координация подводит. Промокод не выдан.';
        winnerCoupon.style.display = 'none';
    }
//запуск теста
    if (startBtn) {
        startBtn.addEventListener('click', () => {
        //сбрасываем счет и индекс для новой попытки
            score = 0;
            currentIndex = 0;
            //берем 10 вопр
            currentQuestions = shuffle(questions).slice(0, 10);
            //скрываем старт и показываем тест
            startScreen.style.display = 'none';
            quizContainer.style.display = 'block';
            //показываем первый аопр
            showQuestion();
        });
    }
});
