document.addEventListener('DOMContentLoaded', function () {
    fetch('http://127.0.0.1:5000/api/updates')
        .then(response => {
            console.log('Raw response:', response);
            return response.text();  // Изменено с .json() на .text()
        })
        .then(text => {
            console.log('Response text:', text);
            return JSON.parse(text);  // Теперь парсим текст вручную
        })
        .then(data => {
            const tbody = document.querySelector('#updates-table tbody');
            data.forEach(service => {
                const row = document.createElement('tr');
                const nameCell = document.createElement('td');
                const dateCell = document.createElement('td');
                
                nameCell.textContent = service.name;
                dateCell.textContent = service.last_update ? new Date(service.last_update).toLocaleString('ru-RU') : 'Нет данных';
                
                row.appendChild(nameCell);
                row.appendChild(dateCell);
                tbody.appendChild(row);
            });
        })
        .catch(error => console.error('Ошибка при загрузке данных:', error));
});
