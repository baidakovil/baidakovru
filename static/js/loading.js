function revealElements(elements, delayMultiplier = 250, callback) {
    elements.forEach((element, index) => {
        setTimeout(() => {
            element.classList.add('visible');
            if (callback && index === elements.length - 1) callback();
        }, delayMultiplier * index);
    });
}

function handleIndexPageAnimations() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    const mainElements = document.querySelectorAll('.header-container, .top-separator, .reveal-element:not(.bottom-separator):not(.navigation)');
    const bottomSeparator = document.querySelector('.bottom-separator');
    const navigation = document.querySelector('.navigation');
    const updatesContainer = document.querySelector('.updates-container');
    
    setTimeout(() => {
        loadingOverlay.style.display = 'none';
        revealElements(mainElements, 250, () => {
            if (updatesContainer) {
                updatesContainer.classList.add('visible');
                document.dispatchEvent(new Event('animationComplete'));
            }
            if (bottomSeparator) bottomSeparator.classList.add('visible');
            if (navigation) navigation.classList.add('visible');
        });
    }, 2000);
}

document.addEventListener('DOMContentLoaded', function() {
    if (window.location.pathname === '/') {
        handleIndexPageAnimations();
    } else {
        revealElements(document.querySelectorAll('.reveal-element'));
    }
});
