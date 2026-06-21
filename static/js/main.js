let totalTasks = 0;

async function startProcessing() {
    const guildId = document.getElementById('guildId').value;
    const btn = document.getElementById('startBtn');
    const input = document.getElementById('guildId');
    const logBox = document.getElementById('logBox');
    const progressBar = document.getElementById('progressBar');

    if (!guildId) {
        addLog('Error: Please enter a Server ID', 'error');
        return;
    }

    // Reset UI
    btn.disabled = true;
    input.disabled = true;
    logBox.innerHTML = '';
    progressBar.style.width = '0%';
    addLog('Connecting to backend...', 'info');

    try {
        const response = await fetch('/api/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ guild_id: guildId })
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n').filter(line => line.trim() !== '');
            
            for (const line of lines) {
                try {
                    const data = JSON.parse(line);
                    addLog(data.status, data.type);

                    if (data.total) totalTasks = data.total;
                    if (data.progress && totalTasks > 0) {
                        const percent = (data.progress / totalTasks) * 100;
                        progressBar.style.width = `${percent}%`;
                    }
                    if (data.type === 'done') {
                        progressBar.style.width = '100%';
                    }
                } catch (e) {
                    console.error("Parse error on chunk:", line);
                }
            }
        }
    } catch (err) {
        addLog(`Network Error: ${err.message}`, 'error');
    } finally {
        btn.disabled = false;
        input.disabled = false;
        addLog('Ready.', 'info');
    }
}

function addLog(message, type) {
    const logBox = document.getElementById('logBox');
    const el = document.createElement('div');
    el.className = `log-line ${type}`;
    
    const time = new Date().toLocaleTimeString([], { hour12: false });
    el.textContent = `[${time}] ${message}`;
    
    logBox.appendChild(el);
    logBox.scrollTop = logBox.scrollHeight;
}
