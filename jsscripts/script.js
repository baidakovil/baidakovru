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
            data.forEach(platform => {
                const row = document.createElement('tr');
                
                const platformNameCell = document.createElement('td');
                const formattedDatetimeCell = document.createElement('td');
                const updateDescCell = document.createElement('td');

                platformNameCell.textContent = platform.platform_name;
                formattedDatetimeCell.textContent = platform.formatted_datetime;
                updateDescCell.textContent = platform.update_desc;
                
                row.appendChild(platformNameCell);
                row.appendChild(formattedDatetimeCell);
                row.appendChild(updateDescCell);
                
                tbody.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Ошибка при загрузке данных:', error);
            logError(error);
        });
});