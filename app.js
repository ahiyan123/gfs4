const API = "http://bore.pub:4916";

async function updateStats() {
    try {
        const res = await fetch(`${API}/status`);
        const data = await res.json();
        document.getElementById('node-name').innerText = data.node;
        document.getElementById('v-count').innerText = data.vault_count;
        document.getElementById('s-count').innerText = data.staging_count;
        document.getElementById('v-bar').style.width = `${Math.min(data.vault_count * 10, 100)}%`;
        document.getElementById('s-bar').style.width = `${Math.min(data.staging_count * 5, 100)}%`;
    } catch (e) { console.error("Offline"); }
}

function log(msg, type='info') {
    const div = document.createElement('div');
    div.className = type === 'think' ? 'text-slate-500 italic' : 'text-blue-300';
    div.innerHTML = `> ${msg}`;
    document.getElementById('console').appendChild(div);
}

document.getElementById('dropzone').onclick = () => document.getElementById('fileInput').click();

document.getElementById('fileInput').onchange = async (e) => {
    for (let file of e.target.files) {
        log(`Ingesting: ${file.name}`);
        log(`G4-Sentinel: Thinking...`, 'think');
        const fd = new FormData();
        fd.append('file', file);
        await fetch(`${API}/ingest`, { method: 'POST', body: fd });
        setTimeout(updateStats, 2000);
    }
};

document.getElementById('micBtn').onclick = () => {
    const rec = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    rec.start();
    log("Voice Mode Active...", "think");
    rec.onresult = (e) => log(`Intent: "${e.results[0][0].transcript}"`);
};

setInterval(updateStats, 5000);
updateStats();
