function handleIndexPageAnimations() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    const mainElements = document.querySelectorAll('.header-container, .top-separator, .reveal-element:not(.bottom-separator):not(.navigation)');
    const bottomSeparator = document.querySelector('.bottom-separator');
    const navigation = document.querySelector('.navigation');
    const updatesContainer = document.querySelector('.updates-container');
    
    const animationCompleteEvent = new Event('animationComplete');
    
    setTimeout(() => {
        loadingOverlay.style.display = 'none';
        
        mainElements.forEach((element, index) => {
            setTimeout(() => {
                element.classList.add('visible');
            }, 250 * index);
        });

        if (updatesContainer) {
            setTimeout(() => {
                updatesContainer.classList.add('visible');
                document.dispatchEvent(animationCompleteEvent);
            }, 250 * mainElements.length);
        }

        if (bottomSeparator) {
            setTimeout(() => {
                bottomSeparator.classList.add('visible');
            }, 200 * (mainElements.length + 1));
        }

        if (navigation) {
            setTimeout(() => {
                navigation.classList.add('visible');
            }, 250 * (mainElements.length + 2));
        }
    }, 2000);
}

function handleRegularPageAnimations() {
    const revealElements = document.querySelectorAll('.reveal-element');
    revealElements.forEach((element, index) => {
        setTimeout(() => {
            element.classList.add('visible');
        }, 250 * index);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    if (window.location.pathname === '/') {
        handleIndexPageAnimations();
    } else {
        handleRegularPageAnimations();
    }
});
