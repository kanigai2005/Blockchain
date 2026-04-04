# 🔗 TrustChain Inventory

A DIY, lightweight, and transparent **Blockchain-backed Inventory Management System** built with Python, FastAPI, and Streamlit. This system focuses on **anti-corruption** and **auditability** by storing all stock movements (additions and sales) in an immutable, cryptographically-linked ledger.

## 🚀 Features

-   **⛓ Immutable Ledger**: Every transaction is stored in a block, linked by SHA-256 hashes.
-   **⛏ Proof of Work**: Blocks must be mined (computational effort) to be committed to the chain.
-   **🔍 Self-Healing Integrity**: The system automatically detects manual tampering with the JSON chain files.
-   **👤 Role-Based Attribution**: Transactions are signed with a unique Cryptographic Employee Signature.
-   **🛒 Smart Inventory**: Purchase transactions are automatically validated against current verified stock counts.
-   **🌐 Distributed Networking**: Register peer nodes and synchronize chains using the **Gossip Protocol** (Longest Chain Rule).

## 🛠 Tech Stack

-   **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (REST API)
-   **Frontend**: [Streamlit](https://streamlit.io/) (Interactive Dashboard)
-   **Database**: Local JSON persistence (No SQL/NoSQL required)
-   **Security**: SHA-256 Hashing, Pydantic validation

## 📋 Prerequisites

-   Python 3.8+
-   Pip (Python package manager)

## 🏗 Installation

1.  **Clone the repository** (or navigate to the project folder):
    ```bash
    cd "bc new"
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## 🚦 Running the Application

To run the full system, you need to start **two** processes: the API node and the Streamlit dashboard.

### 1. Start the API Node (Backend)
Open a terminal and run:
```bash
python api.py 5001
```
*The API will be available at `http://localhost:5001`.*

### 2. Start the Streamlit Dashboard (Frontend)
Open a **second** terminal and run:
```bash
streamlit run app.py
```
*The dashboard will automatically open in your browser (usually at `http://localhost:8501`).*

## 🔐 Default Credentials

| Role | Username | Password |
| :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` |
| **Sales** | `sales` | `sales123` |

## 🕹 How to Use

1.  **Login** as `admin` to add stock and mine blocks.
2.  **Add Stock**: Enter item names and quantities in the Admin tab. This adds transactions to the "Pending Pool".
3.  **Mine**: Click "Mine Pending Transactions" to commit your additions to the permanent ledger.
4.  **Sales**: Switch to the Sales tab (or login as `sales`) to process purchases. These also require mining to be officially recorded.
5.  **Audit**: View the **Ledger** tab to see the visual representation of the blockchain.
6.  **Network**: Connect multiple nodes by starting `api.py` on different ports (e.g., `5001`, `5002`) and registering them in the Network tab.

## 🛡 Anti-Corruption Mechanics

-   **No Backdating**: Transactions are timestamped and hashed into a sequence.
-   **Zero Deletions**: Deleting a record breaks the hash chain, locking the node until integrity is restored.
-   **Limited Access**: Only authenticated users can stage transactions; only admins can mine blocks.

---
*Developed for transparent supply chain and inventory auditing.*
