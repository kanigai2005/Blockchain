Project Name: TrustChain Inventory – Internal Anti-Corruption Blockchain System
Context:
Build a professional-grade Inventory Management System from scratch using Python. Crucial Constraint: Do not use any pre-existing blockchain libraries (no Web3, no Solidity, no Ganache). The blockchain engine must be custom-coded to satisfy a "Distributed Systems" academic requirement.
System Architecture:
The Engine: A Python class that manages a blockchain (SHA-256 hashing, immutable blocks, and local JSON file storage).
The Backend (FastAPI): A high-performance API to handle transactions, mining, and node-to-node synchronization (Gossip Protocol).
The Frontend (Streamlit/Modern Web): A professional dashboard for Administrators and Sales staff.
Core Features to Include:
DIY Blockchain Logic:
Block Structure: Index, Timestamp, Transactions List, Proof (nonce), and Previous Hash.
Genesis Block creation on startup.
Persistence: Automatically save/load the chain to a local file named node_storage_[PORT].json.
Internal Anti-Corruption Logic:
Sales-Driven Automation: Inventory can only be reduced via a "PURCHASE" transaction.
Validation Rule: The engine must scan the entire verified history and block any "PURCHASE" if the item count is insufficient.
Distributed Networking (Gossip Protocol):
Multi-Node Support: Ability to register other nodes (IP/Port).
Consensus: When a block is mined, broadcast it to all registered nodes.
Conflict Resolution: Implement the "Longest Chain Rule" to ensure all nodes sync to a single version of the truth.
Novelty Features (Must Include):
Self-Healing Integrity Verification: On every page refresh or action, the system must re-calculate the hashes of the entire stored JSON chain. If a single character was manually tampered with in the file, show a "🚨 TAMPERING DETECTED" status and lock the node.
Cryptographic Employee Signatures: Every transaction must be automatically tagged with a unique signature (e.g., EMP-PORT-TIMESTAMP_HASH) to ensure 100% accountability for every stock movement.
Visual Ledger Visualization: A modern UI that represents blocks as a connected chain of cards, showing the cryptographic link between them.
UI/UX Requirements:
Professional Dashboard: Use a "Dark Mode" or "Clean Corporate Blue" theme.
Status Indicators: A real-time "Health Badge" (Green for Valid, Red for Compromised).
Role-Based Tabs:
Admin Tab: For adding initial stock and managing the network.
Sales Tab: For processing customer purchases.
Ledger Tab: To view the raw, immutable history of the blockchain.
Live Metrics: Show "Total Verified Items" and "Chain Height" as large cards.
Technical Stack:
Language: Python 3.x
Frameworks: FastAPI (Networking), Streamlit (UI), Httpx (Broadcasts).
Security: SHA-256 (Hashlib).
Output Expectation:
Provide a fully functional, single-file or modularized Python script that I can run in multiple terminals to simulate a distributed inventory network.
