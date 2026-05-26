document.addEventListener('DOMContentLoaded', () => {
    if (typeof anime === 'undefined') return;

    const code = document.querySelector('.error-code');
    if (!code) return;
// появление самого кода ошибки
    anime({
        targets: '.error-code', //эл к которому применяют анимацию
        scale: [0.7, 1], //маштаб от 70 до 100
        opacity: [0, 1], //прозрачность от полностью до видимого
        duration: 900, //длительность 900 миллисек
        easing: 'easeOutExpo'
    });
//появление текста и кнопок каскадом
    anime({
        targets: ['.error-title', '.error-message', '.error-hint', '.error-actions'], //список элементов
        translateY: [18, 0], //смещение по вертикали
        opacity: [0, 1], //плавное проявление из прозрачности
        delay: anime.stagger(120, { start: 250 }),
        easing: 'easeOutSine'
    });
});
