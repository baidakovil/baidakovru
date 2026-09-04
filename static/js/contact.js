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
        // Capture field values now — Turnstile widget may mutate DOM later.
        form.snapshot = {
            message: form.messageArea ? form.messageArea.value : (document.getElementById('message') ? document.getElementById('message').value : ''),
            subject: document.getElementById('subject') ? document.getElementById('subject').value : '',
            email: document.getElementById('email') ? document.getElementById('email').value : ''
        };
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
    // Build FormData explicitly from input values to avoid cases where
    // FormData(form.element) may capture empty values due to widget interactions.
    const fd = new FormData();
    try {
        // Prefer the snapshot captured during initial submit to avoid widgets clearing values
        const msgVal = (form.snapshot && form.snapshot.message !== undefined) ? form.snapshot.message : (form.messageArea ? form.messageArea.value : document.getElementById('message').value);
        const subjVal = (form.snapshot && form.snapshot.subject !== undefined) ? form.snapshot.subject : (document.getElementById('subject') ? document.getElementById('subject').value : '');
        const emailVal = (form.snapshot && form.snapshot.email !== undefined) ? form.snapshot.email : (document.getElementById('email') ? document.getElementById('email').value : '');

        fd.append('message', msgVal);
        fd.append('subject', subjVal);
        fd.append('email', emailVal);
        fd.append('cf-turnstile-response', token);

        const response = await fetch(form.element.action, {
            method: 'POST',
            body: fd
        });

        if (response.ok) {
            showSuccess();
        } else {
            console.error('Submit failed, status:', response.status);
            setSubmitting(false);
        }
    } catch (error) {
        console.error('Submission error:', error);
        setSubmitting(false);
    }
    // clear snapshot after attempt
    try { delete form.snapshot; } catch (e) {}
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
