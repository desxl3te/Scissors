document.addEventListener('DOMContentLoaded', () => {
    if (typeof anime === 'undefined') return;

    const code = document.querySelector('.error-code');
    if (!code) return;

    anime({
        targets: '.error-code',
        scale: [0.7, 1],
        opacity: [0, 1],
        duration: 900,
        easing: 'easeOutExpo'
    });

    anime({
        targets: ['.error-title', '.error-message', '.error-hint', '.error-actions'],
        translateY: [18, 0],
        opacity: [0, 1],
        delay: anime.stagger(120, { start: 250 }),
        easing: 'easeOutSine'
    });
});
