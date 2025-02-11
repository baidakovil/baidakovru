const CONFIG = {
    API_ENDPOINTS: {
        updates: '/api/updates',
        logError: '/api/log-error'
    },
    ANIMATION: {
        DURATION: 5000,
        SCROLL_MARGIN: 50,
        SCROLL_THRESHOLD: 5
    },
    EVENT_TYPES: {
        // GitHub events
        'github_push': 'New code in repository',
        'github_pr': 'New pull request',
        'github_issue': 'New issue activity',
        'github_create': 'New repository created',
        'github_fork': 'Repository forked',
        // iNaturalist events
        'inat_observation': 'New nature observation',
        // Telegram events
        'telegram_post': 'New channel post',
        // Last.fm events
        'lastfm_scrobble': 'Listened to track',
        // LinkedIn events
        'linkedin_post': 'New post',
        // FlightRadar events
        'fr24_flight': 'New flight recorded'
    }
};

class UpdatesManager {
    constructor() {
        this.container = document.querySelector('#updates-content');
    }

    async init() {
        try {
            const data = await this.fetchUpdates();
            this.renderUpdates(data);
        } catch (error) {
            this.handleError(error);
        }
    }

    async fetchUpdates() {
        const response = await fetch(CONFIG.API_ENDPOINTS.updates);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    }

    createUpdateRow(platform) {
        const row = document.createElement('div');
        row.className = 'updates-row';
        
        const platformName = this.createPlatformElement(platform);
        const dateCell = this.createDateElement(platform);
        const linkCell = this.createLinkElement(platform);

        this.attachClickHandler(row, platformName, dateCell, platform);

        row.append(platformName, dateCell, linkCell);
        return row;
    }

    createPlatformElement(platform) {
        const platformName = document.createElement('div');
        platformName.className = 'platform-name';
        platformName.textContent = platform.platform_name;
        return platformName;
    }

    createDateElement(platform) {
        const dateCell = document.createElement('div');
        dateCell.className = 'datetime-cell';
        dateCell.textContent = platform.time_ago;
        return dateCell;
    }

    createLinkElement(platform) {
        const linkCell = document.createElement('div');
        linkCell.className = 'link-cell';
        
        if (platform.platform_url) {
            const link = document.createElement('a');
            link.href = platform.platform_url;
            link.target = '_blank';
            link.rel = 'noopener noreferrer'; // Security best practice
            
            const linkIcon = document.createElement('img');
            linkIcon.src = '/static/svg/link_sign.svg'; // Updated path
            linkIcon.alt = 'External link';
            linkIcon.className = 'link-icon';
            
            // Add tooltip
            const url = new URL(platform.platform_url);
            link.title = `Go to ${url.href.replace(/^https?:\/\//, '')}`;

            link.appendChild(linkIcon);
            linkCell.appendChild(link);
        }
        return linkCell;
    }   

    attachClickHandler(row, platformName, dateCell, platform) {
        row.addEventListener('click', () => {
            if (row.classList.contains('processed')) {
                return;
            }

            this.clearExistingAnimation(row);
            this.setupScrollAnimation(row, platformName, dateCell, platform);
        });
    }

    clearExistingAnimation(row) {
        if (row.dataset.timeoutId) {
            clearTimeout(parseInt(row.dataset.timeoutId));
            row.dataset.timeoutId = '';
        }
    }

    setupScrollAnimation(row, platformName, dateCell, platform) {
        dateCell.classList.add('faded');
        platformName.classList.add('with-date');

        const { platformNameText, dateScrollContainer, dateScrollInner } = 
            this.createScrollElements(platform);

        platformName.textContent = '';
        platformName.appendChild(platformNameText);
        platformName.appendChild(dateScrollContainer);

        this.calculateAndApplyScroll(
            row, platformNameText, dateScrollContainer, 
            dateScrollInner
        );

        this.setResetTimeout(row, platformName, dateCell, platform);
    }

    createScrollElements(platform) {
        const platformNameText = document.createElement('span');
        platformNameText.className = 'platform-name-text';
        platformNameText.textContent = `${platform.platform_name}:`;

        const dateScrollContainer = document.createElement('div');
        dateScrollContainer.className = 'date-scroll-container';

        const dateScrollInner = document.createElement('div');
        dateScrollInner.className = 'date-scroll-inner italic-text';
        dateScrollInner.textContent = `${CONFIG.EVENT_TYPES[platform.update_event]} at ${platform.full_date}`;

        dateScrollContainer.appendChild(dateScrollInner);

        return { platformNameText, dateScrollContainer, dateScrollInner };
    }

    calculateAndApplyScroll(row, platformNameText, dateScrollContainer, dateScrollInner) {
        const measurements = {
            totalWidth: row.clientWidth,
            nameWidth: platformNameText.offsetWidth,
            textWidth: dateScrollInner.offsetWidth
        };

        const availableWidth = measurements.totalWidth - 
            measurements.nameWidth - CONFIG.ANIMATION.SCROLL_MARGIN;

        if (measurements.textWidth > availableWidth + CONFIG.ANIMATION.SCROLL_THRESHOLD) {
            const scrollDistance = measurements.textWidth - availableWidth;
            dateScrollContainer.style.setProperty('--scroll-distance', `-${scrollDistance}px`);
            dateScrollContainer.classList.add('animate-scroll');
        }

        row.classList.add('processed');
    }

    setResetTimeout(row, platformName, dateCell, platform) {
        const timeoutId = setTimeout(() => {
            dateCell.classList.remove('faded');
            platformName.classList.remove('with-date');
            platformName.textContent = platform.platform_name;
            if (platformName.querySelector('.date-scroll-container')) {
                platformName.querySelector('.date-scroll-container').remove();
            }
            row.classList.remove('processed');
            row.dataset.timeoutId = '';
        }, CONFIG.ANIMATION.DURATION);

        row.dataset.timeoutId = timeoutId.toString();
    }

    renderUpdates(data) {
        if (!this.container) {
            throw new Error('Updates container not found');
        }
        this.container.innerHTML = '';
        
        data.forEach(platform => {
            const row = this.createUpdateRow(platform);
            this.container.appendChild(row);
        });
    }

    logError(error) {
        const errorData = {
            message: error.message,
            stack: error.stack
        };
        
        fetch(CONFIG.API_ENDPOINTS.logError, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(errorData),
        })
        .then(response => response.json())
        .catch(err => console.error('Failed to log error:', err));
    }

    handleError(error) {
        console.error('Error:', error);
        this.logError(error);
        
        if (this.container) {
            this.container.innerHTML = '<div class="error-message">Не удалось загрузить обновления</div>';
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const updatesManager = new UpdatesManager();
    updatesManager.init();
});