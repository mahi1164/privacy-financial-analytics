/* frontend/script.js */
/* Full interactive logic for PrivacyGuard Finance */
/* COMPLETE & RUNNABLE - Step 9 (Final) */

const BACKEND_URL = 'http://127.0.0.1:5000';

function testBackendConnection() {
    fetch(`${BACKEND_URL}/test`)
        .then(res => res.json())
        .then(data => {
            alert("✅ Backend is healthy!\n" + JSON.stringify(data, null, 2));
        })
        .catch(() => {
            alert("⚠️ Could not reach backend.\nMake sure backend/app.py is running on port 5000");
        });
}

async function loadTransactions() {
    try {
        const res = await fetch(`${BACKEND_URL}/api/transactions`);
        if (!res.ok) throw new Error("Backend error");

        const data = await res.json();
        console.log("DATA:", data); // debug

        renderTable(data);

    } catch (err) {
        console.error(err);
        alert("❌ Could not load transactions.");
    }
}

async function runAnalysis() {
    try {
        const res = await fetch(`${BACKEND_URL}/api/analyze`, { method: 'POST' });
        if (!res.ok) throw new Error('Analysis failed');
        const result = await res.json();
        alert(`🚀 Clustering complete!\n${JSON.stringify(result, null, 2)}`);
        try {
            loadTransactions();
        } catch (e) {
            console.log("Load skipped after analysis");
        }
    } catch (err) {
        console.error(err);
        alert("❌ Analysis failed.\nCheck backend/routes.py and model.py");
    }
}

function clearResults() {
    document.getElementById('table-body').innerHTML = '';
    document.getElementById('record-count').textContent = '0 records loaded';
    document.getElementById('stats').innerHTML = '';
}

function renderTable(data) {
    const tbody = document.getElementById('table-body');
    tbody.innerHTML = '';
    
    data.forEach(row => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-gray-800/50';
        tr.innerHTML = `
            <td class="px-8 py-4 font-mono">${row.anonymous_id || "N/A"}</td>
            <td class="px-8 py-4 font-medium">
                ₹${row.noisy_amount ? row.noisy_amount.toFixed(2) : "0.00"}
            </td>
            <td class="px-8 py-4 capitalize">${row.category || "N/A"}</td>
            <td class="px-8 py-4">
                <span class="inline-block px-3 py-1 bg-blue-500/10 text-blue-400 rounded-2xl text-xs font-medium">
                    Cluster ${row.cluster !== null ? row.cluster : "N/A"}
                </span>
            </td>
            <td class="px-8 py-4 text-right">
                ${row.is_positive ? 
                    '<span class="text-emerald-400">✅ Yes</span>' : 
                    '<span class="text-red-400">❌ No</span>'}
            </td>
        `;
        tbody.appendChild(tr);
    });
    
    document.getElementById('record-count').textContent = `${data.length} records loaded`;
    renderStats(data);
}

function renderStats(data) {
    const statsHTML = `
        <div class="bg-gray-900 rounded-3xl p-6 text-center">
            <p class="text-gray-400 text-sm">Total Transactions</p>
            <p class="text-5xl font-semibold text-white mt-2">${data.length}</p>
        </div>
        <div class="bg-gray-900 rounded-3xl p-6 text-center">
            <p class="text-gray-400 text-sm">Avg Noisy Amount</p>
            <p class="text-5xl font-semibold text-white mt-2">₹${data.length ? (data.reduce((a, b) => a + b.noisy_amount, 0) / data.length).toFixed(0) : 0}</p>
        </div>
        <div class="bg-gray-900 rounded-3xl p-6 text-center border-2 border-emerald-400">
            <p class="text-gray-400 text-sm">Privacy Budget Used</p>
            <p class="text-5xl font-semibold text-emerald-400 mt-2">ε = 0.5</p>
        </div>
    `;
    document.getElementById('stats').innerHTML = statsHTML;
}

// Auto-init
window.onload = () => {
    console.log("✅ PrivacyGuard frontend fully loaded with script.js");
    console.log("Backend URL:", BACKEND_URL);
};