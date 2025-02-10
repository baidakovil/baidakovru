document.addEventListener('DOMContentLoaded', function () {
    // API endpoints configuration
    const API_ENDPOINTS = {
        updates: '/api/updates',
        logError: '/api/log-error'
    };

    function logError(error) {
        const errorData = {
            message: error.message,
            stack: error.stack
        };
        
        fetch(API_ENDPOINTS.logError, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(errorData),
        })
        .then(response => response.json())
        .catch(err => console.error('Failed to log error:', err));
    }

    fetch(API_ENDPOINTS.updates)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const container = document.querySelector('#updates-content');
            if (!container) {
                throw new Error('Updates container not found');
            }
            container.innerHTML = '';
            
            data.forEach(platform => {
                const row = document.createElement('div');
                row.className = 'updates-row';
                
                // Platform name
                const platformName = document.createElement('div');
                platformName.className = 'platform-name';
                platformName.textContent = platform.platform_name;
                
                // Date cell with tooltip
                const dateCell = document.createElement('div');
                dateCell.className = 'datetime-cell';
                dateCell.textContent = platform.time_ago;
                dateCell.title = platform.full_date;

                // Add click handler
                row.addEventListener('click', () => {
                    if (!row.classList.contains('processed')) {
                        // Clear existing timeout if any
                        if (row.dataset.timeoutId) {
                            clearTimeout(parseInt(row.dataset.timeoutId));
                        }

                        dateCell.classList.add('faded');
                        platformName.classList.add('with-date');
                        
                        // Create fixed platform name span
                        const platformNameText = document.createElement('span');
                        platformNameText.className = 'platform-name-text';
                        platformNameText.textContent = platform.platform_name + ':'; // Add semicolon here
                        
                        // Create scrolling date container with inner element
                        const dateScrollContainer = document.createElement('div');
                        dateScrollContainer.className = 'date-scroll-container';
                        
                        const dateScrollInner = document.createElement('div');
                        dateScrollInner.className = 'date-scroll-inner';
                        dateScrollInner.textContent = ' long long text' + platform.full_date; // Remove semicolon from here, add space
                        
                        dateScrollContainer.appendChild(dateScrollInner);
                        
                        // Clear platformName and add new structure
                        platformName.textContent = '';
                        platformName.appendChild(platformNameText);
                        platformName.appendChild(dateScrollContainer);
                        
                        const totalWidth = row.clientWidth;
                        const nameWidth = platformNameText.offsetWidth;
                        const availableWidth = totalWidth - nameWidth - 50;
                        const textWidth = dateScrollInner.offsetWidth;
                        
                        console.log('Width calculations:', {
                            totalRowWidth: totalWidth,
                            platformNameWidth: nameWidth,
                            availableSpace: availableWidth,
                            dateTextWidth: textWidth,
                            needsScroll: textWidth > availableWidth
                        });
                        
                        if (textWidth > availableWidth) {
                            // Calculate exact translation distance needed
                            const scrollDistance = textWidth - availableWidth;
                            dateScrollContainer.style.setProperty('--scroll-distance', `-${scrollDistance}px`);
                            dateScrollContainer.classList.add('animate-scroll');
                        }
                        
                        row.classList.add('processed');

                        // Set timeout to revert changes after 15 seconds
                        const timeoutId = setTimeout(() => {
                            dateCell.classList.remove('faded');
                            platformName.classList.remove('with-date');
                            platformName.textContent = platform.platform_name; // Reset to original without semicolon
                            if (dateScrollContainer.parentNode) {
                                dateScrollContainer.remove();
                            }
                            platformName.title = '';
                            row.classList.remove('processed');
                            row.dataset.timeoutId = '';
                        }, 15000);

                        row.dataset.timeoutId = timeoutId.toString();
                    }
                });
                
                // Link
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
                    
                    link.appendChild(linkIcon);
                    linkCell.appendChild(link);
                }
                
                row.appendChild(platformName);
                row.appendChild(dateCell);
                row.appendChild(linkCell);
                
                container.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error loading data:', error);
            logError(error);
            
            // Show user-friendly error message
            const container = document.querySelector('#updates-content');
            if (container) {
                container.innerHTML = '<div class="error-message">Не удалось загрузить обновления</div>';
            }
        });
});