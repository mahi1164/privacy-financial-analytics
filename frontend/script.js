const BACKEND_URL = "http://127.0.0.1:5000";


function showStatus(message, type = "info") {
    const box = document.getElementById("status-box");
    box.className = `${type} p-4 mb-4 rounded-xl text-sm font-medium`;
    box.textContent = message;
    box.classList.remove("hidden");

    setTimeout(() => {
        box.classList.add("hidden");
    }, 3000);
}


function clusterBadgeClass(clusterLabel) {
    if (clusterLabel === "Low Spender") {
        return "bg-slate-500/10 text-slate-300";
    }
    if (clusterLabel === "Food Lover") {
        return "bg-orange-500/10 text-orange-300";
    }
    if (clusterLabel === "Traveler") {
        return "bg-sky-500/10 text-sky-300";
    }
    if (clusterLabel === "High Spender") {
        return "bg-rose-500/10 text-rose-300";
    }
    return "bg-blue-500/10 text-blue-300";
}


function testBackendConnection() {
    fetch(`${BACKEND_URL}/test`)
        .then((res) => res.json())
        .then(() => {
            showStatus("Backend is connected", "success");
        })
        .catch(() => {
            alert("Could not reach backend. Make sure backend/app.py is running on port 5000.");
        });
}


async function loadTransactions() {
    try {
        showStatus("Loading privacy-preserved transactions...", "info");
        const response = await fetch(`${BACKEND_URL}/api/transactions`);
        if (!response.ok) {
            throw new Error("Backend error");
        }

        const data = await response.json();
        renderTable(data);
        showStatus("Transactions loaded", "success");
    } catch (error) {
        console.error(error);
        showStatus("Failed to load transactions", "error");
    }
}


async function runAnalysis() {
    try {
        showStatus("Running user-level clustering...", "info");
        const response = await fetch(`${BACKEND_URL}/api/analyze`, { method: "POST" });
        if (!response.ok) {
            throw new Error("Analysis failed");
        }

        const result = await response.json();
        const clusteredUsers = result.users_clustered || 0;
        showStatus(`Clustering completed for ${clusteredUsers} users`, "success");
        await loadTransactions();
    } catch (error) {
        console.error(error);
        showStatus("Clustering failed", "error");
    }
}


function clearResults() {
    document.getElementById("table-body").innerHTML = "";
    document.getElementById("record-count").textContent = "0 records loaded";
    document.getElementById("stats").innerHTML = "";
}


function renderTable(data) {
    const tbody = document.getElementById("table-body");
    tbody.innerHTML = "";

    data.forEach((row) => {
        const clusterLabel = row.cluster || "Unclustered";
        const tr = document.createElement("tr");
        tr.className = "hover:bg-gray-800/50";
        tr.innerHTML = `
            <td class="px-8 py-4 font-mono">${row.anonymous_id || "N/A"}</td>
            <td class="px-8 py-4 font-medium">INR ${Number(row.noisy_amount || 0).toFixed(2)}</td>
            <td class="px-8 py-4">${row.category || "N/A"}</td>
            <td class="px-8 py-4">
                <span class="inline-block px-3 py-1 rounded-2xl text-xs font-medium ${clusterBadgeClass(clusterLabel)}">
                    ${clusterLabel}
                </span>
            </td>
            <td class="px-8 py-4 text-right">
                ${row.is_positive
                    ? '<span class="text-emerald-400">Yes</span>'
                    : '<span class="text-red-400">No</span>'}
            </td>
        `;
        tbody.appendChild(tr);
    });

    const uniqueUsers = new Set(data.map((row) => row.anonymous_id)).size;
    document.getElementById("record-count").textContent = `${data.length} transactions from ${uniqueUsers} users`;
    renderStats(data);
}


function renderStats(data) {
    const uniqueUsers = new Set(data.map((row) => row.anonymous_id)).size;
    const uniqueCategories = new Set(data.map((row) => row.category)).size;
    const clusterLabels = new Set(
        data.map((row) => row.cluster).filter((cluster) => cluster && cluster !== "Unclustered")
    ).size;
    const averageAmount = data.length
        ? data.reduce((sum, row) => sum + Number(row.noisy_amount || 0), 0) / data.length
        : 0;

    const statsHTML = `
        <div class="bg-gray-900 rounded-3xl p-6 text-center">
            <p class="text-gray-400 text-sm">Users</p>
            <p class="text-5xl font-semibold text-white mt-2">${uniqueUsers}</p>
        </div>
        <div class="bg-gray-900 rounded-3xl p-6 text-center">
            <p class="text-gray-400 text-sm">Categories</p>
            <p class="text-5xl font-semibold text-white mt-2">${uniqueCategories}</p>
        </div>
        <div class="bg-gray-900 rounded-3xl p-6 text-center">
            <p class="text-gray-400 text-sm">Cluster Types</p>
            <p class="text-5xl font-semibold text-white mt-2">${clusterLabels}</p>
        </div>
        <div class="bg-gray-900 rounded-3xl p-6 text-center md:col-span-3">
            <p class="text-gray-400 text-sm">Average Noisy Amount</p>
            <p class="text-5xl font-semibold text-emerald-400 mt-2">INR ${averageAmount.toFixed(0)}</p>
        </div>
    `;

    document.getElementById("stats").innerHTML = statsHTML;
}


window.onload = () => {
    console.log("PrivacyGuard frontend loaded");
    console.log("Backend URL:", BACKEND_URL);
};
