const form = {
    element: document.getElementById('contact-form'),
    button: document.getElementById('submit-button'),
    turnstileContainer: document.getElementById('turnstile-container'),
    messageArea: document.getElementById('message'),
    buttonText: {
        default: translations.submit,
        loading: translations.loading
    }
};

let turnstile = {
    loaded: false,
    widgetId: null
};

async function handleSubmit(e) {
    e.preventDefault();
    if (form.element.dataset.submitting === 'true') return;

    try {
        setSubmitting(true);
        await showCaptcha();
    } catch (error) {
        console.error('Form submission error:', error);
        setSubmitting(false);
    }
}

async function showCaptcha() {
    form.turnstileContainer.hidden = false;

    if (!turnstile.loaded) {
        await loadTurnstileScript();
        turnstile.loaded = true;
    }

    if (turnstile.widgetId) {
        window.turnstile.reset(turnstile.widgetId);
    }

    turnstile.widgetId = window.turnstile.render('#turnstile-container', {
        sitekey: config.TURNSTILE_SITE_KEY,
        callback: submitForm,
        'error-callback': () => setSubmitting(false)
    });
}

async function submitForm(token) {
    const formData = new FormData(form.element);
    formData.append('cf-turnstile-response', token);

    try {
        const response = await fetch(form.element.action, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            showSuccess();
        } else {
            throw new Error('Submit failed');
        }
    } catch (error) {
        console.error('Submission error:', error);
        setSubmitting(false);
    }
}

function showSuccess() {
    form.element.innerHTML = `
        <div class="form-message success">
            ${translations.success}
        </div>
    `;
}

function setSubmitting(isSubmitting) {
    form.element.dataset.submitting = isSubmitting;
    form.button.disabled = isSubmitting;
    form.button.textContent = isSubmitting ? form.buttonText.loading : form.buttonText.default;
}

function loadTurnstileScript() {
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js';
        script.async = script.defer = true;
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
    });
}

form.element.addEventListener('submit', handleSubmit);
