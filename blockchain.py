"""
TrustChain Inventory - Advanced Blockchain Engine
Secure, Auditable, and Distributed.
"""

import hashlib
import json
import time
import os
import sqlite3
from typing import List, Dict, Any, Optional
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

def compute_hash(data: dict) -> str:
    """SHA-256 hash of a dictionary, deterministically serialized."""
    raw = json.dumps(data, sort_keys=True).encode()
    return hashlib.sha256(raw).hexdigest()

# ---------------------------------------------------------------------------
# Cryptography Helpers
# ---------------------------------------------------------------------------

def verify_signature(public_key_hex: str, signature_hex: str, message_dict: dict) -> bool:
    """Verify an Ed25519 signature."""
    try:
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_key_hex))
        signature = bytes.fromhex(signature_hex)
        message = json.dumps(message_dict, sort_keys=True).encode()
        public_key.verify(signature, message)
        return True
    except Exception:
        return False

def sign_message(private_key_pem: str, message_dict: dict) -> str:
    """Sign a message using Ed25519 private key."""
    private_key = serialization.load_pem_private_key(private_key_pem.encode(), password=None)
    message = json.dumps(message_dict, sort_keys=True).encode()
    signature = private_key.sign(message)
    return signature.hex()

# ---------------------------------------------------------------------------
# Block
# ---------------------------------------------------------------------------

class Block:
    def __init__(
        self,
        index: int,
        transactions: List[Dict],
        nonce: int,
        previous_hash: str,
        timestamp: Optional[float] = None,
    ):
        self.index = index
        self.timestamp = timestamp or time.time()
        self.transactions = transactions
        self.nonce = nonce
        self.previous_hash = previous_hash
        self.hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        return compute_hash(self.to_dict_without_hash())

    def to_dict_without_hash(self) -> dict:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "nonce": self.nonce,
            "previous_hash": self.previous_hash,
        }

    def to_dict(self) -> dict:
        d = self.to_dict_without_hash()
        d["hash"] = self.hash
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "Block":
        b = cls(
            index=data["index"],
            transactions=data["transactions"],
            nonce=data["nonce"],
            previous_hash=data["previous_hash"],
            timestamp=data["timestamp"],
        )
        b.hash = data["hash"]
        return b


# ---------------------------------------------------------------------------
# Blockchain Engine
# ---------------------------------------------------------------------------

DIFFICULTY = 4  # Requirement: Start with "0000"

class Blockchain:
    def __init__(self, port: int):
        self.db_path = f"node_storage_{port}.db"
        self.storage_file = f"node_storage_{port}.json" # For migration check
        self.chain: List[Block] = []
        self.pending_transactions: List[Dict] = []
        self.nodes: set = set()
        self.locked = False
        
        # Performance Tracking
        self.metrics = {
            "last_mine_time": 0.0,
            "total_mines": 0,
            "avg_mine_duration": 0.0
        }

        self._setup_database()
        
        # Automatic Migration from JSON if it exists and DB is empty
        if os.path.exists(self.storage_file) and len(self.chain) == 0:
            self._migrate_from_json()
        elif len(self.chain) == 0:
            self._create_genesis_block()
            self._save_chain()

    def _setup_database(self):
        """Initializes SQLite schema."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS blocks (
            block_index INTEGER PRIMARY KEY,
            timestamp REAL,
            transactions TEXT,
            nonce INTEGER,
            previous_hash TEXT,
            hash TEXT
        )""")
        c.execute("CREATE TABLE IF NOT EXISTS peers (address TEXT PRIMARY KEY)")
        c.execute("""CREATE TABLE IF NOT EXISTS metrics (
            key TEXT PRIMARY KEY,
            value REAL
        )""")
        conn.commit()
        conn.close()
        self._load_chain()

    def _migrate_from_json(self):
        """Migrate legacy JSON storage to SQLite."""
        try:
            with open(self.storage_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.chain = [Block.from_dict(b) for b in data["chain"]]
            self.nodes = set(data.get("nodes", []))
            self.metrics = data.get("metrics", self.metrics)
            self._save_chain()
            # Optionally backup JSON: os.rename(self.storage_file, self.storage_file + ".bak")
        except Exception:
            self._create_genesis_block()
            self._save_chain()

    def _create_genesis_block(self):
        genesis = Block(
            index=0,
            transactions=[{"type": "GENESIS", "message": "TrustChain Advanced Genesis"}],
            nonce=0,
            previous_hash="0" * 64,
            timestamp=0.0,
        )
        self.chain.append(genesis)

    def _save_chain(self):
        """Directly writes complete state to SQLite."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Save Blocks
        for b in self.chain:
            c.execute("""INSERT OR REPLACE INTO blocks 
                         (block_index, timestamp, transactions, nonce, previous_hash, hash) 
                         VALUES (?, ?, ?, ?, ?, ?)""", 
                      (b.index, b.timestamp, json.dumps(b.transactions), b.nonce, b.previous_hash, b.hash))
        
        # Save Nodes
        for node in self.nodes:
            c.execute("INSERT OR IGNORE INTO peers (address) VALUES (?)", (node,))
            
        # Save Metrics
        for k, v in self.metrics.items():
            c.execute("INSERT OR REPLACE INTO metrics (key, value) VALUES (?, ?)", (k, v))
            
        conn.commit()
        conn.close()

    def _load_chain(self):
        """Reconstructs state from SQLite database."""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Load Blocks
            c.execute("SELECT * FROM blocks ORDER BY block_index ASC")
            db_blocks = c.fetchall()
            if db_blocks:
                self.chain = []
                for row in db_blocks:
                    b_data = {
                        "index": row[0],
                        "timestamp": row[1],
                        "transactions": json.loads(row[2]),
                        "nonce": row[3],
                        "previous_hash": row[4],
                        "hash": row[5]
                    }
                    self.chain.append(Block.from_dict(b_data))
            
            # Load Nodes
            c.execute("SELECT address FROM peers")
            self.nodes = set(row[0] for row in c.fetchall())
            
            # Load Metrics
            c.execute("SELECT key, value FROM metrics")
            for key, val in c.fetchall():
                if key in self.metrics:
                    self.metrics[key] = val
            
            conn.close()
        except Exception as e:
            print(f"DB Load Failure: {e}")

    def verify_integrity(self) -> bool:
        """Rapid SQL-based blockchain integrity check."""
        if not os.path.exists(self.db_path):
            return True
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT * FROM blocks ORDER BY block_index ASC")
            rows = c.fetchall()
            conn.close()

            last_hash = None
            for i, row in enumerate(rows):
                # row: (idx, ts, txs_json, nonce, prev_h, h)
                index, ts, transactions_json, nonce, prev_hash, current_hash = row
                
                recalculated = compute_hash({
                    "index": index,
                    "timestamp": ts,
                    "transactions": json.loads(transactions_json),
                    "nonce": nonce,
                    "previous_hash": prev_hash,
                })
                
                if current_hash != recalculated:
                    self.locked = True
                    return False
                if i > 0 and prev_hash != last_hash:
                    self.locked = True
                    return False
                last_hash = current_hash
                
            self.locked = False
            return True
        except Exception:
            self.locked = True
            return False

    def proof_of_work(self, block_data_func) -> int:
        """Find a nonce that starts with DIFFICULTY number of zeros."""
        nonce = 0
        start_time = time.time()
        while True:
            hash_attempt = compute_hash(block_data_func(nonce))
            if hash_attempt[:DIFFICULTY] == "0" * DIFFICULTY:
                duration = time.time() - start_time
                self._update_metrics(duration)
                return nonce
            nonce += 1

    def _update_metrics(self, duration: float):
        self.metrics["last_mine_time"] = duration
        self.metrics["total_mines"] += 1
        curr_avg = self.metrics["avg_mine_duration"]
        n = self.metrics["total_mines"]
        self.metrics["avg_mine_duration"] = (curr_avg * (n-1) + duration) / n

    def get_inventory_snapshot(self) -> Dict[str, int]:
        inventory: Dict[str, int] = {}
        for block in self.chain:
            for tx in block.transactions:
                item = tx.get("item")
                if not item: continue
                qty = tx.get("quantity", 0)
                if tx.get("type") == "ADD_STOCK":
                    inventory[item] = inventory.get(item, 0) + qty
                elif tx.get("type") == "PURCHASE":
                    inventory[item] = inventory.get(item, 0) - qty
        return inventory

    def add_transaction(
        self, tx_type: str, item: str, quantity: int, added_by: str, 
        signature: str, public_key: str, timestamp: int, note: str = ""
    ) -> Dict[str, Any]:
        """Verify signature before adding transaction to pool."""
        if self.locked:
            return {"success": False, "error": "Node LOCKED."}

        tx_data = {
            "type": tx_type,
            "item": item,
            "quantity": quantity,
            "added_by": added_by,
            "note": note,
            "timestamp": timestamp,
        }

        # Verify cryptographic signature
        if not verify_signature(public_key, signature, tx_data):
            return {"success": False, "error": "INVALID DIGITAL SIGNATURE."}

        # Inventory check for purchases
        if tx_type == "PURCHASE":
            inv = self.get_inventory_snapshot()
            if inv.get(item, 0) < quantity:
                return {"success": False, "error": "INSUFFICIENT STOCK."}

        full_tx = tx_data.copy()
        full_tx["signature"] = signature
        full_tx["public_key"] = public_key
        
        self.pending_transactions.append(full_tx)
        return {"success": True, "transaction": full_tx}

    def mine_block(self) -> Optional[Block]:
        if self.locked or not self.pending_transactions:
            return None

        last_block = self.chain[-1]
        idx = len(self.chain)
        txs = self.pending_transactions[:]
        phash = last_block.hash
        ts = time.time()

        def block_data_minimal(n):
            return {
                "index": idx,
                "timestamp": ts,
                "transactions": txs,
                "nonce": n,
                "previous_hash": phash,
            }

        nonce = self.proof_of_work(block_data_minimal)
        new_block = Block(idx, txs, nonce, phash, ts)
        
        self.chain.append(new_block)
        self.pending_transactions = []
        self._save_chain()
        return new_block

    def register_node(self, address: str):
        self.nodes.add(address.rstrip("/"))
        self._save_chain()

    def replace_chain(self, new_chain_data: List[dict]) -> bool:
        new_chain = [Block.from_dict(b) for b in new_chain_data]
        
        # We only accept longer chains, UNLESS we are currently corrupted (locked), 
        # in which case we accept a valid chain of equal length to heal ourselves.
        if len(new_chain) < len(self.chain):
            return False
        if len(new_chain) == len(self.chain) and not self.locked:
            return False
            
        if not self._is_chain_valid(new_chain):
            return False
            
        self.chain = new_chain
        self.locked = False  # <--- Healing Complete
        self._save_chain()
        return True

    @staticmethod
    def _is_chain_valid(chain: List[Block]) -> bool:
        for i in range(1, len(chain)):
            current = chain[i]
            previous = chain[i - 1]
            if current.previous_hash != previous.hash:
                return False
            if compute_hash(current.to_dict_without_hash()) != current.hash:
                return False
            # Check PoW
            if current.hash[:DIFFICULTY] != "0" * DIFFICULTY:
                return False
        return True

    def chain_as_dicts(self) -> List[dict]:
        return [b.to_dict() for b in self.chain]

    @property
    def chain_height(self) -> int:
        return len(self.chain)

    def get_metrics(self) -> dict:
        return self.metrics
