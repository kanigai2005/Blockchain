"""
TrustChain Inventory – Advanced Streamlit Dashboard
"""

import streamlit as st
import httpx
import json
import time
import hashlib
import os
import pandas as pd
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TrustChain Inventory Pro",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.main { background: #0a0e1a; }
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1226 50%, #0a0e1a 100%);
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1226 0%, #111827 100%) !important;
    border-right: 1px solid rgba(99,120,255,0.15);
}

/* ── UI Fix: Better Containers (Replaces broken div-form-panel) ── */
[data-testid="stVerticalBlock"] > div > div > div[data-testid="stVerticalBlock"] {
    background: rgba(17,24,39,0.4);
    border: 1px solid rgba(99,120,255,0.1);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
}

.hero-title {
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(90deg, #6378ff, #a78bfa, #60cdff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0; line-height: 1.1;
}

.metric-card {
    background: linear-gradient(135deg, rgba(99,120,255,0.12) 0%, rgba(96,205,255,0.08) 100%);
    border: 1px solid rgba(99,120,255,0.25);
    border-radius: 16px;
    padding: 24px 20px;
    text-align: center;
    transition: transform .2s;
}

.badge-healthy { color: #22c55e; background: rgba(34,197,94,0.1); padding: 4px 12px; border-radius: 999px; font-weight: 600; }
.badge-compromised { color: #ef4444; background: rgba(239,68,68,0.1); padding: 4px 12px; border-radius: 999px; font-weight: 600; animation: pulse 1s infinite; }

@keyframes pulse {
    0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; }
}

.block-card {
    background: rgba(17,24,39,0.8);
    border: 1px solid rgba(99,120,255,0.2);
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 12px;
}

.hash-chip {
    font-family: 'Courier New', monospace;
    font-size: 0.75rem;
    color: #a78bfa;
    background: rgba(167,139,250,0.1);
    padding: 2px 6px;
    border-radius: 4px;
}

.tx-pill {
    font-size: 0.75rem;
    padding: 2px 8px;
    border-radius: 999px;
    margin-right: 4px;
}

.insight-box {
    border-left: 4px solid #6378ff;
    padding: 10px 15px;
    background: rgba(99,120,255,0.05);
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

# ─── Auth & Crypto Helpers ───────────────────────────────────────────────────

def get_users():
    if not os.path.exists("users.json"): return {}
    with open("users.json", "r", encoding="utf-8") as f: return json.load(f)

def sign_transaction(private_key_pem, tx_data):
    try:
        pk = serialization.load_pem_private_key(private_key_pem.encode(), password=None)
        message = json.dumps(tx_data, sort_keys=True).encode()
        sig = pk.sign(message)
        return sig.hex()
    except Exception as e:
        st.error(f"Signing failed: {e}")
        return None

# ─── API Helpers ─────────────────────────────────────────────────────────────

def get_node_url():
    return st.session_state.get("node_url", "http://localhost:5001")

def api(method: str, path: str, **kwargs):
    url = f"{get_node_url()}{path}"
    try:
        if method == "GET": r = httpx.get(url, timeout=5, **kwargs)
        else: r = httpx.post(url, timeout=10, **kwargs)
        r.raise_for_status()
        return r.json(), None
    except Exception as e:
        return None, f"⚡ Connection error: {str(e)}"

# ─── Sidebar ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown('<p class="hero-title" style="font-size:1.8rem">🔗 TrustChain</p>', unsafe_allow_html=True)
    st.markdown('<p style="color:#64748b">Advanced Inventory Ledger</p>', unsafe_allow_html=True)
    st.divider()

    st.session_state["node_url"] = st.text_input("Node URL", value=get_node_url())
    if st.button("🔄 Refresh Data", use_container_width=True): st.rerun()

    health, _ = api("GET", "/health")
    if health:
        status_css = "badge-healthy" if health["status"] == "HEALTHY" else "badge-compromised"
        st.markdown(f'<div style="text-align:center"><span class="{status_css}">{health["status"]}</span></div>', unsafe_allow_html=True)
        st.markdown(f"**Height:** {health['chain_height']} | **Node:** {health['node']}")
        
        with st.expander("Node Metrics"):
            m = health.get("metrics", {})
            st.write(f"Avg Mine: {m.get('avg_mine_duration', 0):.2f}s")
            st.write(f"Total Mines: {m.get('total_mines', 0)}")
    
    if st.session_state.get("authenticated"):
        st.divider()
        u = st.session_state["user_info"]
        st.markdown(f"👤 **{u['display_name']}**")
        st.caption(f"Role: {u['role'].upper()}")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state["authenticated"] = False
            st.rerun()

# ─── Login Logic ─────────────────────────────────────────────────────────────

if not st.session_state.get("authenticated"):
    st.markdown('<div style="text-align:center; padding:50px"><h1>Welcome to TrustChain Pro</h1><p>Secure inventory management protocol</p></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        with st.form("login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Unlock Node", use_container_width=True):
                users = get_users()
                if username in users:
                    # Very simple password check for demo
                    pwd_hash = hashlib.sha256(password.encode()).hexdigest()
                    if pwd_hash == users[username]["password_hash"]:
                        st.session_state["authenticated"] = True
                        st.session_state["username"] = username
                        st.session_state["user_info"] = users[username]
                        st.rerun()
                st.error("Invalid credentials")
    st.stop()

# ─── Main Interface ──────────────────────────────────────────────────────────

st.markdown('<p class="hero-title">Inventory Dashboard</p>', unsafe_allow_html=True)

inv_data, _ = api("GET", "/inventory")
chain_data, _ = api("GET", "/chain")
pending_data, _ = api("GET", "/pending")

inventory = inv_data.get("inventory", {}) if inv_data else {}
chain = chain_data.get("chain", []) if chain_data else []
pending = pending_data.get("pending", []) if pending_data else []

# Metrics Row
m1, m2, m3, m4 = st.columns(4)
m1.metric("Verified Items", sum(inventory.values()))
m2.metric("Chain Height", len(chain))
m3.metric("Pending Pool", len(pending))
m4.metric("Active Nodes", len(health.get("total_nodes", [])) if health else 1)

tabs = st.tabs(["🛒 Operations", "📜 Ledger", "🛡 Security Lab", "📊 Analysis", "🌐 Network"])

# ─── Operations Tab ──────────────────────────────────────────────────────────
with tabs[0]:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("➕ Stock/Purchase")
        mode = st.radio("Action Type", ["ADD_STOCK", "PURCHASE"], horizontal=True)
        
        if mode == "ADD_STOCK":
            item = st.text_input("Item Name", placeholder="e.g. Laptop 2024")
            qty = st.number_input("Quantity", min_value=1, value=10)
        else:
            item = st.selectbox("Select Item", list(inventory.keys()) if inventory else ["N/A"])
            qty = st.number_input("Quantity", min_value=1, max_value=max(inventory.get(item, 1), 1))
            
        note = st.text_input("Transaction Note")
        
        if st.button(f"🚀 Sign & Submit {mode}", use_container_width=True):
            if item == "N/A": 
                st.warning("No items available.")
            else:
                user_info = st.session_state["user_info"]
                ts = int(time.time())
                tx_data = {
                    "type": mode,
                    "item": item,
                    "quantity": int(qty),
                    "added_by": st.session_state["username"],
                    "note": note,
                    "timestamp": ts
                }
                
                # Sign client-side
                if "private_key" not in user_info:
                    st.error("❌ Your account has no cryptographic key. Run `python gen_keys.py` and restart.")
                    st.stop()
                sig = sign_transaction(user_info["private_key"], tx_data)
                
                if sig:
                    res, err = api("POST", "/transactions/new", json={
                        "tx_type": mode,
                        "item": item,
                        "quantity": int(qty),
                        "added_by": st.session_state["username"],
                        "signature": sig,
                        "public_key": user_info["public_key"],
                        "timestamp": ts,
                        "note": note
                    })
                    if err: st.error(err)
                    else: st.success("✅ Signed & broadcast to peer network!")

    with col2:
        st.subheader("📦 Inventory Snapshot")
        if not inventory: st.info("No verified stock yet.")
        for k, v in inventory.items():
            color = "#22c55e" if v > 5 else "#ef4444"
            st.markdown(f"**{k}**: <span style='color:{color}; font-weight:800; font-size:1.2rem'>{v}</span>", unsafe_allow_html=True)
        
        st.divider()
        st.subheader("⏳ Pending pool")
        if not pending: st.caption("Pool is empty.")
        for p in pending:
            st.code(f"{p['type']} | {p['item']} x {p['quantity']}\nSig: {p['signature'][:20]}...")

    if st.session_state["user_info"]["role"] == "admin":
        st.divider()
        if st.button("⛏ Mine Block", use_container_width=True, type="primary"):
            with st.spinner("Finding Nonce... (PoW)"):
                res, err = api("GET", "/mine")
                if err:
                    st.error(err)
                elif res and res.get("success"):
                    blk = res.get("block", {})
                    st.success(f"✅ Block #{blk.get('index', '?')} Mined! Hash: `{blk.get('hash','')[:20]}…`")
                    st.rerun()
                else:
                    st.warning(res.get("message", "Nothing to mine or node is locked."))

# ─── Ledger Tab ──────────────────────────────────────────────────────────────
with tabs[1]:
    st.subheader("Immutable Chain Explorer")
    if not chain: st.info("Nothing yet.")
    for b in reversed(chain):
        with st.container():
            st.markdown(f"""
            <div class="block-card">
                <b>Block #{b['index']}</b> | Nonce: {b['nonce']} | {datetime.fromtimestamp(b['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}<br>
                <span style="font-size:0.7rem; color:#64748b">HASH: {b['hash']}</span><br>
                <span style="font-size:0.7rem; color:#64748b">PREV: {b['previous_hash']}</span>
            </div>
            """, unsafe_allow_html=True)
            with st.expander("Transaction Details"):
                st.json(b['transactions'])

# ─── Security Lab Tab ────────────────────────────────────────────────────────
with tabs[2]:
    st.subheader("🛡 Security & Attack Simulations")
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("### 51% Attack Simulation")
        st.write("Force an invalid block into the node storage to test self-healing.")
        if st.button("☢ Inject Malicious Block"):
            res, err = api("GET", "/simulate/tamper", params={"index": 1})
            if err: st.error(err)
            else: 
                st.warning("Attack Injected! Refresh to see the node lock itself.")
                st.rerun()
    
    with c2:
        st.markdown("### Signature Verification")
        st.write("All transactions require valid Ed25519 signatures from authorized employees.")
        st.info("Verified: ✅ Yes (Enabled node-wide)")

# ─── Analysis Tab ────────────────────────────────────────────────────────────
with tabs[3]:
    st.subheader("📊 Performance & Inventory Insights")
    
    if health:
        m = health.get("metrics", {})
        st.write("### Network Performance")
        st.bar_chart({"Mine Duration (s)": [m.get("avg_mine_duration", 0)]})

    st.divider()
    st.subheader("💡 Low Stock Alerts")
    low_stock = [k for k, v in inventory.items() if v < 3]
    if low_stock:
        for item in low_stock:
            st.warning(f"THRESHOLD BREACH: {item} is critically low!")
    else:
        st.success("All stock levels within safety buffers.")

# ─── Network Tab ─────────────────────────────────────────────────────────────
with tabs[4]:
    st.subheader("🌐 Node Topology")
    peer = st.text_input("Register Peer URL", placeholder="http://localhost:5002")
    if st.button("Register Peer"):
        res, err = api("POST", "/nodes/register", json={"nodes": [peer]})
        if not err: st.success("Peer registered.")
    
    st.divider()
    if st.button("🔄 Resolve Conflicts (Gossip Protocol)"):
        with st.spinner("Finding longest chain..."):
            res, err = api("GET", "/nodes/resolve")
            if not err: st.success(f"Resolved! Chain height is now {res['length']}")

st.divider()
st.caption("TrustChain Pro v2.0 - Cryptographic Audit Authority")
