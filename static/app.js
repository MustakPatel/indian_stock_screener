let allSignals = [];
let currentFilter = 'ALL';

document.addEventListener('DOMContentLoaded', () => {
    updateClock();
    setInterval(updateClock, 1000);
    fetchSignals();
});

function updateClock() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('en-IN', { timeZone: 'Asia/Kolkata', hour12: true });
    document.getElementById('live-time').innerText = timeStr + ' IST';
}

async function fetchSignals() {
    const container = document.getElementById('signals-container');
    container.innerHTML = `
        <div class="loading-spinner">
            <div class="spinner"></div>
            <p>Scanning NSE Stocks & Analyzing News Sentiment...</p>
        </div>
    `;

    try {
        const res = await fetch('/api/signals');
        const data = await res.json();
        
        if (data.status === 'success') {
            allSignals = data.data;
            updateKPIs(allSignals);
            renderSignals();
        } else {
            container.innerHTML = `<p class="error">Failed to fetch stock signals.</p>`;
        }
    } catch (err) {
        console.error('Error loading signals:', err);
        container.innerHTML = `<p class="error">Connection error while fetching stock data.</p>`;
    }
}

function updateKPIs(signals) {
    document.getElementById('kpi-scanned').innerText = signals.length;
    const buyCount = signals.filter(s => s.action === 'BUY').length;
    const sellCount = signals.filter(s => s.action === 'SELL').length;
    document.getElementById('kpi-buy').innerText = buyCount;
    document.getElementById('kpi-sell').innerText = sellCount;
}

function filterSignals(filter) {
    currentFilter = filter;
    document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
    if (event && event.target) {
        event.target.classList.add('active');
    }
    renderSignals();
}

function renderSignals() {
    const container = document.getElementById('signals-container');
    let filtered = allSignals;

    if (currentFilter === 'BUY') {
        filtered = allSignals.filter(s => s.action === 'BUY');
    } else if (currentFilter === 'SELL') {
        filtered = allSignals.filter(s => s.action === 'SELL');
    } else if (currentFilter === 'HOLD') {
        filtered = allSignals.filter(s => s.action === 'HOLD');
    }

    if (filtered.length === 0) {
        container.innerHTML = `<p style="grid-column: 1/-1; text-align: center; color: #94a3b8; padding: 40px;">No stocks matching category "${currentFilter}" found right now.</p>`;
        return;
    }

    container.innerHTML = filtered.map(s => {
        const sentimentLabel = s.sentiment ? s.sentiment.label : 'Neutral';
        const headline = s.sentiment && s.sentiment.headlines.length > 0 ? s.sentiment.headlines[0] : 'No recent major news.';
        const actionBadge = s.action_badge || (s.action === 'BUY' ? '🟢 PUT MONEY HERE (BUY)' : (s.action === 'SELL' ? '🔴 WITHDRAW MONEY (SELL)' : '🟡 HOLD / WATCH'));
        const actionDesc = s.action_desc || 'Consolidating market technicals.';
        
        return `
            <div class="signal-card">
                <div class="card-top">
                    <div class="symbol-name">${s.symbol}</div>
                    <div class="signal-badge ${s.signal_type}">${s.signal_type}</div>
                </div>

                <div class="action-banner ${s.action}">
                    ${actionBadge}
                </div>

                <div class="action-reason">
                    <strong>💡 AI Investment Insight:</strong> ${actionDesc}
                </div>

                <div class="price-row">
                    <span class="current-price">₹${s.price.toLocaleString('en-IN')}</span>
                </div>

                <div class="metrics-row">
                    <div class="metric-item">
                        <span>RSI (14)</span>
                        <strong>${s.rsi}</strong>
                    </div>
                    <div class="metric-item">
                        <span>Volume Spike</span>
                        <strong>${s.vol_ratio}x</strong>
                    </div>
                </div>

                <div class="targets-container">
                    <div>T1: <span class="target-val">₹${s.target_1}</span></div>
                    <div>T2: <span class="target-val">₹${s.target_2}</span></div>
                    <div>SL: <span class="sl-val">₹${s.stop_loss}</span></div>
                </div>

                <div class="news-box">
                    <div class="news-label">📰 News Sentiment: ${sentimentLabel}</div>
                    <div>${headline}</div>
                </div>

                <div class="card-action-btns">
                    <button class="btn-add-portfolio" onclick="quickAddPortfolio('${s.symbol}', ${s.price})">
                        ➕ Add to Portfolio
                    </button>
                    <button class="btn-copy" onclick="copyAlert('${escapeJsString(s.formatted_alert)}')">
                        📲 Telegram Alert
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

function quickAddPortfolio(symbol, price) {
    document.getElementById('input-symbol').value = symbol;
    document.getElementById('input-price').value = price;
    document.getElementById('input-quantity').value = 10;
    openAddModal();
    setTimeout(() => {
        const qtyInput = document.getElementById('input-quantity');
        qtyInput.focus();
        qtyInput.select();
    }, 100);
}

function escapeJsString(str) {
    return str.replace(/'/g, "\\'").replace(/\n/g, "\\n");
}

function switchView(viewName) {
    document.querySelectorAll('.view-container').forEach(v => v.style.display = 'none');
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    
    if (viewName === 'portfolio') {
        document.getElementById('view-portfolio').style.display = 'block';
        document.getElementById('tab-portfolio').classList.add('active');
        fetchPortfolio();
    } else if (viewName === 'ipo') {
        document.getElementById('view-ipo').style.display = 'block';
        document.getElementById('tab-ipo').classList.add('active');
        fetchIPOs();
    } else {
        document.getElementById('view-screener').style.display = 'block';
        document.getElementById('tab-screener').classList.add('active');
    }
}

async function fetchIPOs() {
    const container = document.getElementById('ipo-container');
    container.innerHTML = `
        <div class="loading-spinner">
            <div class="spinner"></div>
            <p>Scanning Active Indian IPOs & Grey Market Premium (GMP)...</p>
        </div>
    `;
    try {
        const res = await fetch('/api/ipo');
        const data = await res.json();
        if (data.status === 'success') {
            renderIPOs(data.data);
        }
    } catch (err) {
        console.error('Error fetching IPOs:', err);
    }
}

function renderIPOs(ipos) {
    const container = document.getElementById('ipo-container');
    if (!ipos || ipos.length === 0) {
        container.innerHTML = `<p style="grid-column: 1/-1; text-align: center; color: #94a3b8;">No active IPOs found right now.</p>`;
        return;
    }

    container.innerHTML = ipos.map(ipo => `
        <div class="signal-card">
            <div class="card-top">
                <div class="symbol-name">${ipo.name}</div>
                <div class="signal-badge">${ipo.type}</div>
            </div>

            <div class="action-banner ${ipo.recommendation.includes('APPLY') ? 'BUY' : 'SELL'}">
                ${ipo.badge}
            </div>

            <div class="action-reason">
                <strong>💡 AI IPO Decision:</strong> ${ipo.desc}
            </div>

            <div class="metrics-row">
                <div class="metric-item">
                    <span>Issue Price</span>
                    <strong>₹${ipo.issue_price}</strong>
                </div>
                <div class="metric-item">
                    <span>Grey Market Premium (GMP)</span>
                    <strong class="target-val">+₹${ipo.gmp_price} (+${ipo.gmp_pct}%)</strong>
                </div>
            </div>

            <div class="targets-container">
                <div>Est. Listing: <span class="target-val">₹${ipo.est_listing_price}</span></div>
                <div>Subscription: <span class="target-val">${ipo.subscription_x}x</span></div>
                <div>Profit/Lot: <span class="target-val">~₹${ipo.est_profit_per_lot.toLocaleString('en-IN')}</span></div>
            </div>

            <div class="news-box">
                <div>📅 <strong>Bidding Window:</strong> ${ipo.open_date} - ${ipo.close_date}</div>
            </div>
        </div>
    `).join('');
}

async function fetchPortfolio() {
    try {
        const res = await fetch('/api/portfolio');
        const data = await res.json();
        if (data.status === 'success') {
            renderPortfolio(data.data);
        }
    } catch (err) {
        console.error('Error fetching portfolio:', err);
    }
}

function renderPortfolio(data) {
    document.getElementById('port-invested').innerText = `₹${data.total_invested.toLocaleString('en-IN')}`;
    document.getElementById('port-val').innerText = `₹${data.current_value.toLocaleString('en-IN')}`;
    
    const pnlEl = document.getElementById('port-pnl');
    const pnlPctEl = document.getElementById('port-pnl-pct');
    const pnlCard = document.getElementById('card-pnl');
    
    const sign = data.total_pnl >= 0 ? '+' : '';
    pnlEl.innerText = `${sign}₹${data.total_pnl.toLocaleString('en-IN')}`;
    pnlPctEl.innerText = `${sign}${data.pnl_pct}% Overall P&L`;
    
    if (data.total_pnl >= 0) {
        pnlCard.className = 'kpi-card highlight-green';
    } else {
        pnlCard.className = 'kpi-card highlight-red';
    }

    const tbody = document.getElementById('portfolio-tbody');
    if (!data.holdings || data.holdings.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: #94a3b8; padding: 30px;">No active portfolio holdings found. Click "+ Add New Stock Buy" to record your trades!</td></tr>`;
        return;
    }

    tbody.innerHTML = data.holdings.map(h => {
        const pnlClass = h.pnl >= 0 ? 'target-val' : 'sl-val';
        const pnlSign = h.pnl >= 0 ? '+' : '';
        return `
            <tr>
                <td><strong>${h.symbol}</strong></td>
                <td>${h.quantity}</td>
                <td>₹${h.buy_price.toLocaleString('en-IN')}</td>
                <td>₹${h.current_price.toLocaleString('en-IN')}</td>
                <td>₹${h.current_value.toLocaleString('en-IN')}</td>
                <td class="${pnlClass}"><strong>${pnlSign}₹${h.pnl.toLocaleString('en-IN')} (${pnlSign}${h.pnl_pct}%)</strong></td>
                <td><span class="signal-badge">${h.recommendation}</span></td>
                <td><button class="btn-delete" onclick="deleteHolding('${h.symbol}')">Delete</button></td>
            </tr>
        `;
    }).join('');
}

function openAddModal() {
    document.getElementById('modal-trade').style.display = 'flex';
}

function closeAddModal() {
    document.getElementById('modal-trade').style.display = 'none';
}

async function handleFormSubmit(event) {
    event.preventDefault();
    const symbol = document.getElementById('input-symbol').value.trim();
    const quantity = document.getElementById('input-quantity').value;
    const buy_price = document.getElementById('input-price').value;

    try {
        const res = await fetch('/api/portfolio/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbol, quantity, buy_price })
        });
        const data = await res.json();
        if (data.status === 'success') {
            closeAddModal();
            renderPortfolio(data.data);
            document.getElementById('form-add-trade').reset();
        } else {
            alert(data.message || 'Failed to add holding');
        }
    } catch (err) {
        console.error('Error adding holding:', err);
    }
}

async function deleteHolding(symbol) {
    if (!confirm(`Are you sure you want to remove ${symbol} from your portfolio?`)) return;
    try {
        const res = await fetch('/api/portfolio/remove', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbol })
        });
        const data = await res.json();
        if (data.status === 'success') {
            renderPortfolio(data.data);
        }
    } catch (err) {
        console.error('Error removing holding:', err);
    }
}
