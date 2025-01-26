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
            console.log('Raw response:', response);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.text();
        })
        .then(text => {
            console.log('Response text:', text);
            return JSON.parse(text);
        })
        .then(data => {
            const tbody = document.querySelector('#updates-table tbody');
            tbody.innerHTML = ''; // Clear existing content
            
            data.forEach(platform => {
                const row = document.createElement('tr');
                
                const platformNameCell = document.createElement('td');
                const formattedDatetimeCell = document.createElement('td');
                formattedDatetimeCell.className = 'datetime-cell';

                platformNameCell.textContent = platform.platform_name;
                
                // Create container for date and link
                const dateContainer = document.createElement('div');
                dateContainer.className = 'date-container';
                
                const dateSpan = document.createElement('span');
                dateSpan.textContent = formatDate(platform.formatted_datetime);
                dateContainer.appendChild(dateSpan);
                
                if (platform.update_url) {
                    const link = document.createElement('a');
                    link.href = platform.update_url;
                    link.target = '_blank';
                    const linkIcon = document.createElement('img');
                    linkIcon.src = '/styles/link_sign.svg';
                    linkIcon.alt = 'Link';
                    linkIcon.className = 'link-icon';
                    link.appendChild(linkIcon);
                    dateContainer.appendChild(link);
                }
                
                formattedDatetimeCell.appendChild(dateContainer);
                
                row.appendChild(platformNameCell);
                row.appendChild(formattedDatetimeCell);
                
                tbody.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Ошибка при загрузке данных:', error);
            logError(error);
        });
});