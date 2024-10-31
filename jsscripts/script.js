document.addEventListener('DOMContentLoaded', function () {
    fetch('/api/updates')
        .then(response => {
            console.log('Raw response:', response);
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
                dateCell.textContent = service.formatted_datetime ? new Date(service.formatted_datetime).toLocaleString('ru-RU') : 'Нет данных';
                
                row.appendChild(nameCell);
                row.appendChild(dateCell);
                tbody.appendChild(row);
            });
        })
        .catch(error => console.error('Ошибка при загрузке данных:', error));
});
