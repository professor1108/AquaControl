const apiBase = '/api/v1';

// Пороговые значения для подсветки датчиков
const THRESHOLDS = {
    temperature: { min: 20, max: 30, unit: '°C' },
    ph: { min: 6.0, max: 8.5, unit: '' },
    ammonia: { min: 0, max: 0.5, unit: ' мг/л' },
    oxygen: { min: 4.0, max: 10, unit: ' мг/л' },
    turbidity: { min: 0, max: 10, unit: ' NTU' }
};

const SENSOR_NAMES = {
    temperature: 'Температура',
    ph: 'pH',
    ammonia: 'Аммиак',
    oxygen: 'Кислород',
    turbidity: 'Мутность'
};

// ========== Датчики ==========
async function fetchStatus() {
    try {
        const response = await fetch(`${apiBase}/status/`);
        const data = await response.json();
        const sensorsDiv = document.getElementById('sensors');
        sensorsDiv.innerHTML = '';

        for (const [key, value] of Object.entries(data.sensors)) {
            const threshold = THRESHOLDS[key];
            let className = 'sensor-item';
            if (threshold) {
                if (key === 'temperature' || key === 'ammonia' || key === 'turbidity') {
                    if (value > threshold.max) className += ' danger';
                    else if (value > threshold.max * 0.9) className += ' alarm';
                } else if (key === 'oxygen') {
                    if (value < threshold.min) className += ' danger';
                    else if (value < threshold.min * 1.2) className += ' alarm';
                } else if (key === 'ph') {
                    if (value < threshold.min || value > threshold.max) className += ' danger';
                    else if (value < threshold.min + 0.3 || value > threshold.max - 0.3) className += ' alarm';
                }
            }
            const unit = threshold ? threshold.unit : '';

            const div = document.createElement('div');
            div.className = className;
            div.innerHTML = `
                <span class="sensor-label">${SENSOR_NAMES[key] || key}</span>
                <span class="sensor-value">${value.toFixed(1)}</span>
                <span class="sensor-unit">${unit}</span>
            `;
            sensorsDiv.appendChild(div);
        }
    } catch (e) {
        console.error('Ошибка получения датчиков', e);
    }
}

// ========== Устройства ==========
async function fetchDevices() {
    try {
        const response = await fetch(`${apiBase}/devices/`);
        const devices = await response.json();
        const devicesDiv = document.getElementById('devices');
        devicesDiv.innerHTML = '';

        devices.forEach(device => {
            const row = document.createElement('div');
            row.className = 'device-row';

            const nameSpan = document.createElement('span');
            nameSpan.className = 'device-info';
            nameSpan.textContent = device.name;
            row.appendChild(nameSpan);

            const statusSpan = document.createElement('span');
            statusSpan.className = 'device-status';
            const statusClass = device.status ? 'status-on' : 'status-off';
            statusSpan.innerHTML = `<span class="status-indicator ${statusClass}"></span> ${device.status ? 'Вкл' : 'Выкл'}`;
            row.appendChild(statusSpan);

            let details = '';
            if (device.type === 'light' && device.mode) {
                const modeNames = { day: 'День', night: 'Ночь', storm: 'Шторм', plant_growth: 'Рост растений' };
                details = `Режим: ${modeNames[device.mode] || device.mode}`;
            } else if (device.type === 'feeder' && device.power != null) {
                details = `Последняя порция: ${device.power} г`;
            }
            if (details) {
                const detailsSpan = document.createElement('span');
                detailsSpan.className = 'device-details';
                detailsSpan.textContent = details;
                row.appendChild(detailsSpan);
            }

            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'device-actions';

            if (device.type !== 'feeder') {
                const toggleBtn = document.createElement('button');
                toggleBtn.className = `btn-toggle ${device.status ? 'on' : 'off'}`;
                toggleBtn.textContent = device.status ? 'Выкл' : 'Вкл';
                toggleBtn.addEventListener('click', async () => {
                    await toggleDevice(device.id, !device.status);
                    fetchDevices();
                });
                actionsDiv.appendChild(toggleBtn);
            } else {
                const feedBtn = document.createElement('button');
                feedBtn.className = 'btn-feed';
                feedBtn.textContent = 'Покормить';
                feedBtn.addEventListener('click', async () => {
                    const portion = parseFloat(document.getElementById('portion').value) || 1.0;
                    await feedNow(portion);
                    fetchDevices();
                });
                actionsDiv.appendChild(feedBtn);
            }
            row.appendChild(actionsDiv);

            devicesDiv.appendChild(row);
        });
    } catch (e) {
        console.error('Ошибка получения устройств', e);
    }
}

async function toggleDevice(deviceId, newStatus) {
    try {
        const response = await fetch(`${apiBase}/devices/${deviceId}/status`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });
        if (!response.ok) {
            alert('Ошибка при переключении устройства');
        }
    } catch (e) {
        console.error(e);
    }
}

async function feedNow(portion) {
    try {
        const response = await fetch(`${apiBase}/control/feeding`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ portion: portion })
        });
        if (response.ok) {
            alert(`Кормление выполнено: ${portion} г`);
            fetchEvents();
        }
    } catch (e) {
        console.error(e);
    }
}

// ========== События ==========
async function fetchEvents() {
    try {
        const response = await fetch(`${apiBase}/events/?limit=20`);
        const events = await response.json();
        const list = document.getElementById('events');
        list.innerHTML = '';

        events.forEach(event => {
            const li = document.createElement('li');
            const time = new Date(event.timestamp).toLocaleTimeString('ru-RU', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });

            let typeLabel = '';
            switch (event.event_type) {
                case 'alarm': typeLabel = 'Тревога'; break;
                case 'auto': typeLabel = 'Авто'; break;
                case 'info': typeLabel = 'Инфо'; break;
                default: typeLabel = event.event_type;
            }

            li.innerHTML = `<span class="event-time">${time}</span><span class="event-type">[${typeLabel}]</span><span class="event-desc">${event.description}</span>`;
            list.appendChild(li);
        });
    } catch (e) {
        console.error('Ошибка получения событий', e);
    }
}

// ========== Обработчики кнопок управления ==========
document.getElementById('setTempBtn')?.addEventListener('click', async () => {
    const target = document.getElementById('targetTemp').value;
    if (target) {
        await fetch(`${apiBase}/control/temperature`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target: parseFloat(target) })
        });
        fetchEvents();
        fetchDevices();
    }
});

document.getElementById('feedBtn')?.addEventListener('click', async () => {
    const portion = parseFloat(document.getElementById('portion').value) || 1.0;
    await feedNow(portion);
    fetchDevices();
});

document.getElementById('setLightBtn')?.addEventListener('click', async () => {
    const mode = document.getElementById('lightMode').value;
    await fetch(`${apiBase}/control/light/mode`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode: mode })
    });
    fetchEvents();
    fetchDevices();
});

// ========== Периодическое обновление ==========
setInterval(fetchStatus, 5000);
setInterval(fetchDevices, 5000);
setInterval(fetchEvents, 10000);

// Первоначальная загрузка
fetchStatus();
fetchDevices();
fetchEvents();