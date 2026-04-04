import json
import os
import hashlib
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

def run():
    if not os.path.exists("users.json"):
        print("users.json not found")
        return

    with open("users.json", "r", encoding="utf-8") as f:
        users = json.load(f)

    for username, data in users.items():
        # Generate Ed25519 key pair
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()

        # Serialize
        priv_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        pub_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )

        data["public_key"] = pub_bytes.hex()
        # In a real app we'd keep private keys secure, but for this demo:
        data["private_key"] = priv_bytes.decode()
        print(f"Generated keys for {username}")

    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

if __name__ == "__main__":
    run()
