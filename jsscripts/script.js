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
            data.forEach(service => {
                const row = document.createElement('tr');
                const nameCell = document.createElement('td');
                const dateCell = document.createElement('td');
                
                nameCell.textContent = service.name;
                dateCell.textContent = service.formatted_datetime ? service.formatted_datetime : 'Нет данных';
                
                row.appendChild(nameCell);
                row.appendChild(dateCell);
                tbody.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Ошибка при загрузке данных:', error);
            logError(error);
        });
});