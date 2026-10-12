const API_BASE = "http://localhost:8000";

function showToast(message, type = "success") {
    const container = document.getElementById("toast-container");
    if (!container) return;
    
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    
    let icon = "✓";
    if (type === "warning") icon = "⚠";
    if (type === "danger") icon = "✗";
    
    toast.innerHTML = `<span class="toast-icon">${icon}</span><span class="toast-message">${message}</span>`;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = "0";
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function getToken() {
    return localStorage.getItem("access_token");
}

function getRefreshToken() {
    return localStorage.getItem("refresh_token");
}

async function apiCall(endpoint, method = "GET", body = null) {
    let token = getToken();
    const headers = {
        "Content-Type": "application/json"
    };
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }
    
    const config = {
        method,
        headers
    };
    if (body) {
        config.body = JSON.stringify(body);
    }
    
    try {
        let response = await fetch(`${API_BASE}${endpoint}`, config);
        
        if (response.status === 401) {
            const refreshToken = getRefreshToken();
            if (refreshToken) {
                const refreshResponse = await fetch(`${API_BASE}/api/auth/refresh`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ refresh_token: refreshToken })
                });
                
                if (refreshResponse.ok) {
                    const data = await refreshResponse.json();
                    localStorage.setItem("access_token", data.access_token);
                    
                    config.headers["Authorization"] = `Bearer ${data.access_token}`;
                    response = await fetch(`${API_BASE}${endpoint}`, config);
                } else {
                    logout();
                    return null;
                }
            } else {
                logout();
                return null;
            }
        }
        
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: "Unknown error occurred" }));
            throw new Error(errData.detail || `HTTP Error: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        showToast(error.message || "Bağlantı hatası oluştu.", "danger");
        throw error;
    }
}

async function logout() {
    const token = getToken();
    if (token) {
        try {
            await fetch(`${API_BASE}/api/auth/revoke`, {
                method: "POST",
                headers: { "Authorization": `Bearer ${token}` }
            });
        } catch (e) {
            // Ignore failure on signout
        }
    }
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    window.location.href = "index.html";
}

function formatDate(isoString) {
    if (!isoString) return "";
    const date = new Date(isoString);
    const options = { day: 'numeric', month: 'long', year: 'numeric' };
    return date.toLocaleDateString('tr-TR', options);
}

function getDaysLeft(deadlineStr) {
    if (!deadlineStr) return null;
    const deadline = new Date(deadlineStr);
    const now = new Date();
    const timeDiff = deadline - now;
    const daysLeft = Math.ceil(timeDiff / (1000 * 60 * 60 * 24));
    return daysLeft;
}

function showModal(title, bodyHtml, footerHtml = "") {
    const overlay = document.getElementById("modal-overlay");
    const mTitle = document.getElementById("modal-title");
    const mBody = document.getElementById("modal-body");
    const mFooter = document.getElementById("modal-footer");
    
    if (!overlay) return;
    
    mTitle.innerText = title;
    mBody.innerHTML = bodyHtml;
    mFooter.innerHTML = footerHtml;
    
    overlay.classList.add("open");
}

function hideModal() {
    const overlay = document.getElementById("modal-overlay");
    if (overlay) overlay.classList.remove("open");
}
