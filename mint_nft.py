import json
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from math import gcd

# Connect to Avalanche Fuji testnet
url = "https://avalanche-fuji.drpc.org"
w3 = Web3(Web3.HTTPProvider(url))
w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

assert w3.is_connected(), "Failed to connect to Avalanche Fuji"
print(f"Connected to Avalanche Fuji. Block number: {w3.eth.block_number}")

# Load private key
with open("secret_key.txt", "r") as f:
    private_key = f.read().strip()

account = w3.eth.account.from_key(private_key)
my_address = account.address
print(f"Using address: {my_address}")

# Load contract
contract_address = "0x85ac2e065d4526FBeE6a2253389669a12318A412"
with open("NFT.abi", "r") as f:
    abi = json.load(f)

contract = w3.eth.contract(address=contract_address, abi=abi)


def send_transaction(tx):
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(f"Transaction sent: {tx_hash.hex()}")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Transaction confirmed in block: {receipt.blockNumber}")
    return receipt


def combine_nfts(token_id_a, token_id_b):
    tx = contract.functions.combine(my_address, token_id_a, token_id_b).build_transaction({
        'from': my_address,
        'nonce': w3.eth.get_transaction_count(my_address),
        'gas': 300000,
        'gasPrice': w3.eth.gas_price,
    })
    receipt = send_transaction(tx)
    
    # Calculate gcd directly in Python
    token_id = gcd(token_id_a, token_id_b)
    print(f"Combined token ID: {token_id}")
    return token_id


if __name__ == "__main__":
    # Use already claimed tokens
    token_a = 590681899797230787
    token_b = 3972141821347421435

    print(f"Using claimed tokens: {token_a} and {token_b}")
    print(f"Expected GCD (new token ID): {gcd(token_a, token_b)}")

    print("\n--- Combining NFTs ---")
    final_token = combine_nfts(token_a, token_b)
    print(f"\nFinal token ID: {final_token}")
    print(f"Check NFT at: https://testnet.snowtrace.io/address/{my_address}")