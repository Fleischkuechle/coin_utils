import requests
import hashlib
import json


def address_to_scripthash(address):
    # Convert Dogecoin address to script hash
    # This is a simplified version; ensure to handle the conversion correctly
    # You may need to use a library for accurate conversion
    return hashlib.sha256(address.encode()).hexdigest()


def get_utxos(scripthash):
    # Replace with your ElectrumX server's URL
    # electrumx_url = "http://your_electrumx_server:port"
    # electrumx_url = "http://electrum3.cipig.net:10060"
    electrumx_url = "http://electrum3.cipig.net"
    payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "blockchain.scripthash.get_history",
        "params": [scripthash],
    }

    response = requests.post(electrumx_url, json=payload)

    if response.status_code == 200:
        return response.json().get("result", [])
    else:
        print("Error:", response.json())
        return []


# Replace with your Dogecoin address
dogecoin_address = "D8koxBk542fETcJUqgd48aqFbZww9Rhmbt"
scripthash = address_to_scripthash(dogecoin_address)
utxos = get_utxos(scripthash)

# Print the UTXOs
print("Unspent Transaction Outputs (UTXOs):")
for utxo in utxos:
    print(f"TXID: {utxo['tx_hash']}, Vout: {utxo['tx_pos']}, Amount: {utxo['value']}")
