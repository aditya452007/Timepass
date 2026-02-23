const UI = {
    fireBtn: document.getElementById('fire-btn'),
    eventSelect: document.getElementById('event-type'),
    failRateInfo: document.getElementById('fail-rate-val'),
    failRateInput: document.getElementById('fail-rate'),
    dndToggle: document.getElementById('toggle-dnd'),
    onlineToggle: document.getElementById('toggle-online'),
    slowToggle: document.getElementById('toggle-slow'),
    auditLog: document.getElementById('audit-log'),
    
    // Scenarios
    scenarioBtns: document.querySelectorAll('.scenario-btn'),
    
    // Reset function
    resetNodes: () => {
        document.querySelectorAll('.box').forEach(el => {
            el.className = 'box node'; 
            if(el.classList.contains('worker-node')) el.classList.add('worker-node');
            if(el.classList.contains('dlq-node')) el.classList.add('dlq-node');
            const statusTarget = el.querySelector('.status');
            if(statusTarget) statusTarget.innerText = 'Idle';
        });
        document.querySelectorAll('.q-bar').forEach(el => el.style.width = '0%');
        document.querySelectorAll('.q-count').forEach(el => el.innerText = '0');
        
        // Remove animation marker if exists
        document.querySelectorAll('.dlq-node').forEach(el => {
             el.className = 'box dlq-node';
             el.querySelector('.status').innerText = '0 Messages';
        });
    }
};

let eventSource = null;

// Controls setup
UI.failRateInput.addEventListener('input', (e) => {
    UI.failRateInfo.innerText = `${e.target.value}%`;
});

// Tooltips toggle
let tooltipsEnabled = true;
document.body.classList.add('show-tooltips');
document.querySelector('.tooltip-toggle').addEventListener('click', () => {
    tooltipsEnabled = !tooltipsEnabled;
    if(tooltipsEnabled) {
        document.body.classList.add('show-tooltips');
    } else {
        document.body.classList.remove('show-tooltips');
    }
});

function logAudit(step, status, message) {
    const entry = document.createElement('div');
    entry.className = `log-entry ${status}`;
    
    const time = new Date().toLocaleTimeString([], {hour12: false, hour: '2-digit', minute:'2-digit', second:'2-digit'});
    entry.innerHTML = `<span class="log-time">[${time}]</span> <span class="log-msg">[${step.toUpperCase()}] ${message}</span>`;
    
    UI.auditLog.appendChild(entry);
    UI.auditLog.scrollTop = UI.auditLog.scrollHeight;
}

// Scenarios setup
UI.scenarioBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
        const type = e.target.dataset.scenario;
        if (!type) return;
        
        // Remove active state
        UI.scenarioBtns.forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        
        // Reset defaults
        UI.eventSelect.value = "order.placed";
        UI.failRateInput.value = 0;
        UI.failRateInfo.innerText = "0%";
        UI.dndToggle.checked = false;
        UI.onlineToggle.checked = false;
        UI.slowToggle.checked = false;
        
        if (type === 'happy') {
            UI.onlineToggle.checked = true;
        } else if (type === 'outage') {
            UI.failRateInput.value = 100;
            UI.failRateInfo.innerText = "100%";
            UI.eventSelect.value = "password.reset";
            UI.slowToggle.checked = true; // make retries readable
        } else if (type === 'dnd') {
            UI.dndToggle.checked = true;
            UI.eventSelect.value = "promo.flash_sale";
        } else if (type === 'async') {
            UI.slowToggle.checked = true;
            UI.eventSelect.value = "user.signup";
        }
    });
});

UI.fireBtn.addEventListener('click', triggerSimulation);

function triggerSimulation() {
    // Disabled UI
    UI.fireBtn.disabled = true;
    UI.fireBtn.innerText = "Processing...";
    
    // Clear state
    UI.resetNodes();
    UI.auditLog.innerHTML = '';
    
    const eventParams = new URLSearchParams({
        event: UI.eventSelect.value,
        fail_rate: UI.failRateInput.value,
        dnd: UI.dndToggle.checked,
        online: UI.onlineToggle.checked,
        slow: UI.slowToggle.checked
    });
    
    logAudit('system', 'info', `🚀 Firing Event: ${UI.eventSelect.value}`);
    
    if (eventSource) {
        eventSource.close();
    }
    
    eventSource = new EventSource(`/simulate?${eventParams.toString()}`);
    
    eventSource.onmessage = (event) => {
        const payload = JSON.parse(event.data);
        handleServerEvent(payload);
    };
    
    eventSource.onerror = (err) => {
        eventSource.close();
        UI.fireBtn.disabled = false;
        UI.fireBtn.innerText = "🔥 TRIGGER EVENT 🔥";
    };
}

function handleServerEvent(payload) {
    const { step, status, message, data, queues, dlq_count } = payload;
    
    if (step === 'done') {
        eventSource.close();
        UI.fireBtn.disabled = false;
        UI.fireBtn.innerText = "🔥 TRIGGER EVENT 🔥";
        logAudit(step, 'success', message);
        return;
    }
    
    // Update queues visually
    if (queues) {
        Object.entries(queues).forEach(([channel, count]) => {
            const countEl = document.querySelector(`#queue-${channel} .q-count`);
            const barEl = document.querySelector(`#q-bar-${channel}`);
            if(countEl && barEl) {
                countEl.innerText = count + " msg";
                // Arbitrary max mapping: let's say 2 items fills it 100% just for visualization
                barEl.style.width = `${Math.min((count / 2) * 100, 100)}%`;
            }
        });
    }
    
    // Update DLQ visually
    const dlqNode = document.getElementById('node-dlq');
    if (dlqNode && dlq_count !== undefined) {
        dlqNode.querySelector('.status').innerText = `${dlq_count} Messages`;
        if (dlq_count > 0) {
            dlqNode.className = 'box dlq-node has-items';
        }
    }
    
    // Visual Node Updating
    let targetNodeId = `node-${step}`; // e.g. node-ingestion, node-worker_email
    const nodeEl = document.getElementById(targetNodeId);
    
    if (nodeEl) {
        // Remove old state classes but keep identity
        nodeEl.className = `box ${nodeEl.classList.contains('worker-node') ? 'worker-node' : 'node'} ${status}`;
        
        if (!nodeEl.classList.contains('worker-node')) {
            const statusEl = nodeEl.querySelector('.status');
            if(statusEl) {
                if(status === 'processing') statusEl.innerText = 'Processing...';
                else if(status === 'success') statusEl.innerText = 'Done ✅';
                else if(status === 'failed' || status === 'error') statusEl.innerText = 'Blocked ❌';
            }
        }
    }
    
    logAudit(step, status, message);
}
