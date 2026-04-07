"""
TrustChain Inventory – Advanced FastAPI Backend
"""

import httpx
import asyncio
import os
import json
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import sys

from blockchain import Blockchain

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5001
bc = Blockchain(port=PORT)

app = FastAPI(
    title="TrustChain Advanced Node",
    description="Secure Blockchain-backed Inventory System",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Background Consensus Worker
# ---------------------------------------------------------------------------

async def background_consensus():
    """Periodically check with peers to sync the longest valid chain."""
    while True:
        try:
            # Only run if there are peers to talk to
            if bc.nodes:
                async with httpx.AsyncClient(timeout=5) as client:
                    for node in list(bc.nodes):
                        try:
                            # Use resolve endpoint's logic
                            resp = await client.get(f"{node}/chain")
                            if resp.status_code == 200:
                                data = resp.json()
                                # replace_chain handles validation and longest chain rule
                                if bc.replace_chain(data["chain"]):
                                    # If heal or sync happened, we could add a log here
                                    pass
                        except Exception:
                            continue
        except Exception:
            pass
        await asyncio.sleep(30) # Check every 30 seconds

@app.on_event("startup")
async def startup_event():
    # Start the consensus worker in the background
    asyncio.create_task(background_consensus())


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class TransactionRequest(BaseModel):
    tx_type: str           # ADD_STOCK | PURCHASE
    item: str
    quantity: int
    added_by: str          # User who performed the action
    signature: str         # Ed25519 signature hex
    public_key: str        # Ed25519 public key hex
    timestamp: int         # Epoch timestamp from client
    note: Optional[str] = ""


class NodeRequest(BaseModel):
    nodes: List[str]


class ChainPayload(BaseModel):
    chain: List[dict]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    integrity_ok = bc.verify_integrity()
    return {
        "node": PORT,
        "status": "COMPROMISED" if bc.locked else "HEALTHY",
        "integrity": integrity_ok,
        "chain_height": bc.chain_height,
        "total_nodes": list(bc.nodes),
        "metrics": bc.get_metrics()
    }


@app.post("/transactions/new")
def new_transaction(req: TransactionRequest):
    result = bc.add_transaction(
        req.tx_type, req.item, req.quantity, req.added_by, 
        req.signature, req.public_key, req.timestamp, req.note
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@app.get("/mine")
async def mine():
    block = bc.mine_block()
    if block is None:
        return {"success": False, "message": "Nothing to mine or node is locked."}

    await _broadcast_new_block(block.to_dict())

    return {
        "success": True,
        "message": "Block mined and broadcast!",
        "block": block.to_dict(),
    }


@app.get("/chain")
def full_chain():
    bc.verify_integrity()
    return {
        "chain": bc.chain_as_dicts(),
        "length": bc.chain_height,
        "locked": bc.locked,
    }


@app.get("/inventory")
def inventory():
    bc.verify_integrity()
    return {
        "inventory": bc.get_inventory_snapshot(),
        "locked": bc.locked,
    }

@app.get("/metrics")
def metrics():
    return bc.get_metrics()


@app.post("/nodes/register")
def register_nodes(req: NodeRequest):
    for node in req.nodes:
        bc.register_node(node)
    return {"message": "Nodes registered", "total_nodes": list(bc.nodes)}


@app.get("/nodes/resolve")
async def consensus():
    replaced = False
    async with httpx.AsyncClient(timeout=5) as client:
        for node in bc.nodes:
            try:
                resp = await client.get(f"{node}/chain")
                data = resp.json()
                if bc.replace_chain(data["chain"]):
                    replaced = True
            except Exception:
                pass
    return {
        "replaced": replaced,
        "chain": bc.chain_as_dicts(),
        "length": bc.chain_height,
    }


@app.post("/nodes/receive_block")
def receive_block(payload: ChainPayload):
    replaced = bc.replace_chain(payload.chain)
    return {"accepted": replaced, "chain_height": bc.chain_height}


@app.get("/pending")
def pending_transactions():
    return {"pending": bc.pending_transactions}

# ---------------------------------------------------------------------------
# Simulation Routes (Attack Lab)
# ---------------------------------------------------------------------------

@app.get("/simulate/tamper")
def tamper_chain(index: int = 1):
    """FOR DEMO ONLY: Manually tampers with a block in the SQLite database."""
    if not os.path.exists(bc.db_path):
        return {"error": "Database not found"}
    
    try:
        import sqlite3
        conn = sqlite3.connect(bc.db_path)
        c = conn.cursor()
        
        # Damage the transactions JSON of a specific block
        malicious_tx = [{"type": "MALICIOUS", "item": "VOID_ITEM", "quantity": 9999}]
        c.execute("UPDATE blocks SET transactions = ? WHERE block_index = ?", 
                  (json.dumps(malicious_tx), index))
        
        conn.commit()
        conn.close()
        return {"success": True, "message": f"Block {index} corrupted in SQL database!"}
    except Exception as e:
        return {"error": str(e)}
    
    return {"error": "Index out of range or chain empty"}


# ---------------------------------------------------------------------------
# Gossip helper
# ---------------------------------------------------------------------------

async def _broadcast_new_block(block_dict: dict):
    chain_payload = {"chain": bc.chain_as_dicts()}
    async with httpx.AsyncClient(timeout=3) as client:
        tasks = []
        for node in bc.nodes:
            tasks.append(
                client.post(f"{node}/nodes/receive_block", json=chain_payload)
            )
        await asyncio.gather(*tasks, return_exceptions=True)

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
