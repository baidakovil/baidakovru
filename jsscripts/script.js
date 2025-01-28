document.addEventListener('DOMContentLoaded', function () {
    function logError(error) {
        const errorData = {
            message: error.message,
            stack: error.stack
        };
        
        fetch('/api/log-error', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(errorData),
        })
        .then(response => response.json())
        .then(data => console.log('Error logged:', data))
        .catch(err => console.error('Failed to log error:', err));
    }

    function formatDate(dateStr) {
        const date = new Date(dateStr);
        const currentYear = new Date().getFullYear();
        const months = [
            'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
            'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
        ];
        
        const day = date.getDate().toString().padStart(2, '0');
        const month = months[date.getMonth()];
        const year = date.getFullYear();
        
        return year === currentYear ? 
            `${day} ${month}` : 
            `${day} ${month} ${year}`;
    }

    fetch('/api/updates')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const container = document.querySelector('#updates-content');
            container.innerHTML = '';
            
            data.forEach(platform => {
                const row = document.createElement('div');
                row.className = 'updates-row';
                
                // Platform name
                const platformName = document.createElement('div');
                platformName.className = 'platform-name';
                platformName.textContent = platform.platform_name;
                
                // Date
                const dateCell = document.createElement('div');
                dateCell.className = 'datetime-cell';
                dateCell.textContent = formatDate(platform.formatted_datetime);
                
                // Link
                const linkCell = document.createElement('div');
                linkCell.className = 'link-cell';
                
                if (platform.platform_url) {
                    const link = document.createElement('a');
                    link.href = platform.platform_url;
                    link.target = '_blank';
                    const linkIcon = document.createElement('img');
                    linkIcon.src = '/styles/link_sign.svg';
                    linkIcon.alt = 'Link';
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
        });
});