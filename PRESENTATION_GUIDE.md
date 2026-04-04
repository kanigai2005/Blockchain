# 🎤 TrustChain Inventory: Demo & Presentation Guide

This guide provides the exact "Pitch", the technical workings, and a step-by-step path you can take to present this project successfully.

---

## 💡 1. The Pitch (How to introduce the project)

**"Welcome to TrustChain Inventory Pro."**
*Traditional inventory systems rely on central databases that can be easily manipulated, leading to stock discrepancies, corruption, and unaccounted losses. TrustChain solves this by replacing the central database with a **custom-built, distributed cryptographic ledger**.*

*Every single stock movement (additions or purchases) is **digitally signed** by an employee and sealed into an **immutable block** using Proof-of-Work. The network is self-healing, meaning if anyone attempts to edit past records to hide missing stock, the entire network locks down that compromised node and replaces it with the truthful global consensus.*

---

## ⚙️ 2. Core Workings (What to highlight)

Prepare to talk briefly about these 4 core mechanisms during your presentation:

1.  **Ed25519 Digital Signatures**: Like Bitcoin, every user has a Public/Private keypair. Transactions are impossible to forge.
2.  **Proof of Work (Mining)**: A node must solve a cryptographic puzzle (finding a SHA-256 hash starting with `0000`) before the network accepts a block. 
3.  **Gossip Protocol (Consensus)**: Multiple nodes run independently. When we "Resolve Conflicts", the nodes talk to each other and adopt the **Longest Valid Chain**.
4.  **Self-Healing Integrity**: The backend constantly re-hashes the local storage. If a system admin opens the JSON file and tries to manually change `"quantity": 5` to `"quantity": 10`, the hash breaks, and the node instantly triggers a lockdown.

---

## 🎬 3. Step-by-Step Demo Script

**Environment Prep**: We have 3 backend nodes running simultaneously (Ports: 5001, 5002, 5003) and 1 Streamlit Dashboard.

### Step 1: The Login & Dashboard Overview
1. Open the dashboard `http://localhost:8501`.
2. Login as the Super Admin (`admin` / `admin123`).
3. Explain the layout: *Operations (for commerce), Ledger (for auditing), Security (for testing limits).*

### Step 2: A Secure Transaction
1. In the **Operations Tab**, select `ADD_STOCK`.
2. Enter an item (e.g., `MacBook Pro`) and quantity (e.g., `5`).
3. Click **"Sign & Submit"**. 
   * **Talking point**: *"Behind the scenes, my private key generated an Ed25519 signature. The network validated it and put the transaction in the Pending Pool."*
4. Click **"⛏ Mine Block"**.
   * **Talking point**: *"The node just performed Proof-of-Work to find a valid nonce, sealing that transaction into the immutable ledger."*

### Step 3: Peer Verification (The Network)
1. In the sidebar, change the Node URL from `http://localhost:5001` to `http://localhost:5002` and hit **Refresh**.
   * Note how Node 5002 shows **0 Verified Items** and **Height: 1**. It doesn't know about Node 1's block yet!
2. Go to the **🌐 Network Tab**.
3. Under "Register Peer", enter `http://localhost:5001` and click **Register Peer**.
4. Click **"🔄 Resolve Conflicts"**.
   * **Result**: Node 2 synchronizes and adopts the longest chain from Node 1. The inventory updates immediately! 
   * **Talking Point**: *"This is the Gossip Protocol in action. Decentralized synchronization without a central server."*

### Step 4: The 51% Attack / Tampering Simulation (The WOW Factor)
1. Head to the **🛡 Security Lab** tab.
2. Explain the scenario: *"What if a malicious employee gains access to the raw hard drive and tries to edit the database to cover up stolen stock?"*
3. Click **"☢ Inject Malicious Block"**.
4. Look at the Sidebar immediately — it will flash **🚨 COMPROMISED**.
5. Try to submit a new transaction; it will fail with `Node LOCKED`.
   * **Talking Point**: *"Because the cryptography no longer matches the history, the node's Self-Healing Integrity recognized the corruption and quarantined itself. It will no longer accept or broadcast transactions until it is repaired via network consensus."*

### Step 5: Wrap up with Analytics
1. Show the **📊 Analysis** tab to demonstrate that you are tracking network load (Mining block times) and automated smart-contract style minimum inventory thresholds.
